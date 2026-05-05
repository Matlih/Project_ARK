import asyncio
import json
import torch
import psycopg2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict
from redis import Redis
from rq import Queue

# Import Gates
from backend.gates.gate1_sensor_qa import run_gate1
from backend.gates.gate2_atmospheric import run_gate2
from backend.gates.gate3_spectral import run_gate3

app = FastAPI(title="Project ARK: Data Certification API")

# --- Infrastructure Setup ---
# (Assumes local Redis and Postgres instances are running)
redis_conn = Redis(host='localhost', port=6379)
q = Queue('rejections', connection=redis_conn)

DB_DSN = "dbname=ark user=postgres password=postgres host=localhost"

# --- Models ---
class ProcessRequest(BaseModel):
    scene_path: str
    event_id: str

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

ws_manager = ConnectionManager()

# --- Async Background Worker Task (RQ) ---
def log_rejection_to_db(event_id: str, scene_path: str, reason: str, saved_hrs: float):
    """Background task to log rejected scenes to PostgreSQL without blocking the API."""
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO rejections (event_id, scene_path, reason, compute_saved_hrs) 
               VALUES (%s, %s, %s, %s)""",
            (event_id, scene_path, reason, saved_hrs)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Logging Error: {e}")

# --- API Endpoints ---

@app.post("/process")
async def process_scene(req: ProcessRequest):
    """
    Executes the ARD Certification Pipeline.
    Streams progress via WebSockets and returns the final JSON manifest.
    """
    scene = req.scene_path
    total_saved_hrs = 0.0
    gate_results = []
    
    # GATE 1
    g1 = run_gate1(scene)
    gate_results.append(g1)
    total_saved_hrs += g1.compute_saved_hrs
    await ws_manager.broadcast({"event_id": req.event_id, "gate": g1.gate_name, "status": g1.status})
    
    if g1.status == "FAIL":
        q.enqueue(log_rejection_to_db, req.event_id, scene, g1.reason, g1.compute_saved_hrs)
        return {"ard_certified": False, "total_saved_hrs": total_saved_hrs, "results": [g1.__dict__]}

    # GATE 2
    g2 = run_gate2(scene)
    gate_results.append(g2)
    total_saved_hrs += g2.compute_saved_hrs
    await ws_manager.broadcast({"event_id": req.event_id, "gate": g2.gate_name, "status": g2.status})
    
    if g2.status == "FAIL":
        q.enqueue(log_rejection_to_db, req.event_id, scene, g2.reason, g2.compute_saved_hrs)
        return {"ard_certified": False, "total_saved_hrs": total_saved_hrs, "results": [r.__dict__ for r in gate_results]}

    # GATE 3
    g3 = run_gate3(scene, season="wet")
    gate_results.append(g3)
    total_saved_hrs += g3.compute_saved_hrs
    await ws_manager.broadcast({"event_id": req.event_id, "gate": g3.gate_name, "status": g3.status})
    
    if g3.status == "FAIL":
        q.enqueue(log_rejection_to_db, req.event_id, scene, g3.reason, g3.compute_saved_hrs)
        return {"ard_certified": False, "total_saved_hrs": total_saved_hrs, "results": [r.__dict__ for r in gate_results]}

    # ALL PASSED
    await ws_manager.broadcast({"event_id": req.event_id, "status": "ARD_CERTIFIED"})
    return {
        "ard_certified": True,
        "total_saved_hrs": total_saved_hrs,
        "results": [r.__dict__ for r in gate_results]
    }

@app.get("/metrics")
def get_metrics():
    """Retrieves the last 100 rejection events."""
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        cur.execute("SELECT event_id, scene_path, reason, compute_saved_hrs, logged_at FROM rejections ORDER BY logged_at DESC LIMIT 100")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"event": r[0], "path": r[1], "reason": r[2], "saved_hrs": r[3], "time": r[4]} for r in rows]
    except Exception as e:
        return {"error": str(e), "message": "Database not initialized or unreachable."}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)