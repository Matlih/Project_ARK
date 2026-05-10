import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Architect's Rule: Always configure CORS for local decoupled frontend/backend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global registry to hold active WebSocket connections
active_connections = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    print("[ARK Backend] Frontend WebSocket connected.")
    
    # 1. Immediate connection confirmation
    await websocket.send_json({
        "type": "agent_update",
        "data": {
            "agent": "SYSTEM",
            "message": "WebSocket securely bound to ARK orchestrator."
        }
    })
    
    try:
        while True:
            # Keep connection alive and listen for incoming messages if any
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print("[ARK Backend] Frontend WebSocket disconnected.")

# Core Simulation Sequence
async def run_pipeline_simulation(region: str):
    if not active_connections:
        print("[ARK Backend] WARNING: No active WebSockets to receive data.")
        return

    # Broadcast helper function
    async def broadcast(payload):
        for ws in active_connections:
            try:
                await ws.send_json(payload)
            except Exception as e:
                print(f"[ARK Backend] Failed to send to socket: {e}")

    print(f"[ARK Backend] Launching simulation for {region}...")

    # T+1s: Gate 1 PASS
    await asyncio.sleep(1)
    await broadcast({
        "type": "gate_result",
        "data": {
            "gate_name": "GATE_1_QA", "status": "PASS",
            "confidence": 0.97, "reason": "SNR 28dB nominal",
            "compute_saved_hrs": 0, "processing_ms": 47
        }
    })

    # T+2s: Gate 2 FAIL (Cloud Cover)
    await asyncio.sleep(1)
    await broadcast({
        "type": "gate_result", 
        "data": {
            "gate_name": "GATE_2_CLOUD", "status": "FAIL",
            "confidence": 0.92,
            "reason": "Cloud cover 78.3% — exceeds 20% threshold",
            "compute_saved_hrs": 1.85, "processing_ms": 183
        }
    })

    # T+3s: Gate 3 PASS (ARD Certification)
    await asyncio.sleep(1)
    await broadcast({
        "type": "gate_result",
        "data": {
            "gate_name": "GATE_3_ARD", "status": "PASS",
            "confidence": 0.99, "reason": "Analysis Ready Data certified",
            "compute_saved_hrs": 0, "processing_ms": 82
        }
    })

    # T+4s: damage_assessment_node (Triggers Globe Zoom)
    await asyncio.sleep(1)
    await broadcast({
        "type": "agent_update",
        "data": {
            "agent": "damage_assessment_node",
            "message": "Analyzing SAR backscatter anomalies for infrastructure damage...",
            "coords": [121.7, 17.6]  # [lon, lat] for Northern Philippines
        }
    })

    # T+5s: economic_valuation_node
    await asyncio.sleep(1)
    await broadcast({
        "type": "agent_update",
        "data": {
            "agent": "economic_valuation_node",
            "message": "Calculating asset vulnerability indexes in target zone..."
        }
    })

    # T+6s: insurance_trigger_node
    await asyncio.sleep(1)
    await broadcast({
        "type": "agent_update",
        "data": {
            "agent": "insurance_trigger_node",
            "message": "Cross-referencing parametric thresholds with estimated wind speed..."
        }
    })

    # T+7s: recovery_planner_node
    await asyncio.sleep(1)
    await broadcast({
        "type": "agent_update",
        "data": {
            "agent": "recovery_planner_node",
            "message": "Generating initial resource allocation routing..."
        }
    })

    # T+8s: ndrrmc_reporter_node
    await asyncio.sleep(1)
    await broadcast({
        "type": "agent_update",
        "data": {
            "agent": "ndrrmc_reporter_node",
            "message": "Formatting finalized intelligence briefing..."
        }
    })

    # T+9s: pipeline_complete (Triggers Slide-in Report and Metric updates)
    await asyncio.sleep(1)
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_text = f"""NDRRMC SITUATION REPORT NO. 1
DATE: {current_date}
REGION: {region.upper()}

PRIORITY ALERT: Economic Impact Zone Detected
COORDINATES: 17.6N, 121.7E

ESTIMATED AGRICULTURAL DAMAGES: ₱ 1.61B
COMPUTE SAVINGS: $ 3,024.75

RECOMMENDATION:
Deploy aerial survey assets to Sector Alpha.
Initiate parametric insurance payouts for affected municipalities."""

    await broadcast({
        "type": "pipeline_complete",
        "data": {
            "total_peso_loss": 1610000000,
            "total_compute_saved_usd": 3024.75,
            "total_time_seconds": 58.3,
            "report": {
                "en": report_text,
                "fil": report_text.replace("SITUATION REPORT", "ULAT SITWASYON").replace("PRIORITY ALERT", "PRIYORIDAD NA ALERTO").replace("ESTIMATED AGRICULTURAL DAMAGES", "TINATAYANG PINSALA SA AGRIKULTURA")
            }
        }
    })
    print("[ARK Backend] Simulation complete.")

# -----------------------------------------
# REST API ENDPOINTS
# -----------------------------------------

@app.post("/demo")
@app.get("/demo")
async def trigger_demo(request: Request):
    """
    Acts as the main trigger. Handles both POST (from our UI) and GET (for browser testing).
    """
    region = "Philippines"
    if request.method == "POST":
        try:
            body = await request.json()
            region = body.get("region", "Philippines")
        except:
            pass

    # Launch the simulation in the background so the HTTP request returns immediately
    asyncio.create_task(run_pipeline_simulation(region))
    return {"status": "ACK", "message": f"Pipeline launched for {region}"}

@app.post("/reset")
async def reset_backend():
    """
    Acknowledges the frontend reset request. 
    In a real backend, this drops active DB transactions and resets state.
    """
    print("[ARK Backend] Received reset command.")
    return {"status": "ACK", "message": "Backend state wiped."}

if __name__ == "__main__":
    print("[ARK Backend] Starting mock WebSocket server on ws://localhost:8000/ws")
    uvicorn.run(app, host="0.0.0.0", port=8000)