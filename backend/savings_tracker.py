import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any

# Assuming GateResult is available from your earlier pipeline
from backend.gates.gate1_sensor_qa import GateResult

# --- SQL SCHEMA DEFINITIONS ---
SCHEMA_QUERIES = [
    """
    CREATE TABLE IF NOT EXISTS rejection_events (
        id SERIAL PRIMARY KEY,
        event_id VARCHAR(100),
        scene_id VARCHAR(200),
        gate_name VARCHAR(50),
        fail_reason VARCHAR(200),
        cloud_pct FLOAT,
        compute_saved_hrs FLOAT,
        compute_saved_usd FLOAT,
        analyst_hrs_saved FLOAT,
        peso_loss_prevented FLOAT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ard_certified (
        id SERIAL PRIMARY KEY,
        scene_id VARCHAR(200),
        event_id VARCHAR(100),
        certified_at TIMESTAMP DEFAULT NOW(),
        gate1_confidence FLOAT,
        gate2_cloud_pct FLOAT,
        gate3_ndvi_mean FLOAT
    );
    """
]

class SavingsTracker:
    def __init__(self, db_url: str):
        """Initializes the database connection and ensures tables exist."""
        self.db_url = db_url
        self._init_db()

    def _get_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)

    def _init_db(self):
        """Builds the event-sourced tables if they do not exist."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    for query in SCHEMA_QUERIES:
                        cur.execute(query)
                conn.commit()
        except Exception as e:
            print(f"Database initialization failed: {e}")

    def log_rejection(self, gate_result: GateResult, event_id: str, scene_id: str):
        """Appends an immutable rejection event to the log."""
        compute_usd = float(gate_result.compute_saved_hrs) * 1.99
        analyst_hrs = float(gate_result.compute_saved_hrs) * 2.0
        
        # Only Gate 2 guarantees a cloud_pct metric, default to 0.0 for others
        cloud_pct = gate_result.metrics.get('cloud_pct', 0.0)

        query = """
            INSERT INTO rejection_events 
            (event_id, scene_id, gate_name, fail_reason, cloud_pct, 
             compute_saved_hrs, compute_saved_usd, analyst_hrs_saved, peso_loss_prevented)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            event_id, 
            scene_id, 
            gate_result.gate_name, 
            gate_result.reason[:200], # Truncate to avoid varchar overflow
            cloud_pct, 
            gate_result.compute_saved_hrs, 
            compute_usd, 
            analyst_hrs, 
            0.0 # 0 for gate rejections, populated later by Prithvi/Qwen
        )

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
            conn.commit()

    def log_certification(self, scene_id: str, event_id: str, gate_results: List[GateResult]):
        """Logs a scene that successfully passed all ARD gates."""
        # Extract specific metrics based on the known gate order
        g1_confidence = gate_results[0].confidence
        g2_cloud_pct = gate_results[1].metrics.get('cloud_pct', 0.0)
        g3_ndvi_mean = gate_results[2].metrics.get('ndvi_mean', 0.0)

        query = """
            INSERT INTO ard_certified 
            (scene_id, event_id, gate1_confidence, gate2_cloud_pct, gate3_ndvi_mean)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (scene_id, event_id, g1_confidence, g2_cloud_pct, g3_ndvi_mean))
            conn.commit()

    def get_running_totals(self) -> Dict[str, Any]:
        """Calculates exact system telemetry from the immutable event log."""
        totals = {
            "total_scenes_processed": 0,
            "total_rejected": 0,
            "total_ard_certified": 0,
            "total_compute_saved_hrs": 0.0,
            "total_compute_saved_usd": 0.0,
            "total_analyst_hrs_saved": 0.0,
            "rejection_by_gate": {},
            "last_5_events": []
        }

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Certifications
                cur.execute("SELECT COUNT(*) as count FROM ard_certified")
                totals["total_ard_certified"] = cur.fetchone()['count']

                # 2. Aggregated Savings & Rejections
                cur.execute("""
                    SELECT 
                        COUNT(*) as count,
                        COALESCE(SUM(compute_saved_hrs), 0) as total_hrs,
                        COALESCE(SUM(compute_saved_usd), 0) as total_usd,
                        COALESCE(SUM(analyst_hrs_saved), 0) as total_analyst
                    FROM rejection_events
                """)
                agg = cur.fetchone()
                totals["total_rejected"] = agg['count']
                totals["total_compute_saved_hrs"] = round(agg['total_hrs'], 2)
                totals["total_compute_saved_usd"] = round(agg['total_usd'], 2)
                totals["total_analyst_hrs_saved"] = round(agg['total_analyst'], 2)
                
                totals["total_scenes_processed"] = totals["total_ard_certified"] + totals["total_rejected"]

                # 3. Rejection Distribution by Gate
                cur.execute("SELECT gate_name, COUNT(*) as count FROM rejection_events GROUP BY gate_name")
                for row in cur.fetchall():
                    totals["rejection_by_gate"][row['gate_name']] = row['count']

                # 4. Last 5 Events (Ticker tape data)
                cur.execute("""
                    SELECT scene_id, gate_name, compute_saved_hrs, compute_saved_usd, created_at 
                    FROM rejection_events 
                    ORDER BY created_at DESC LIMIT 5
                """)
                # Convert datetime to ISO format string for JSON serialization
                events = []
                for row in cur.fetchall():
                    row['created_at'] = row['created_at'].isoformat()
                    events.append(row)
                totals["last_5_events"] = events

        return totals

    def get_event_stream(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns the raw rejection event stream for the WebSocket feed."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM rejection_events ORDER BY created_at DESC LIMIT %s", (limit,))
                events = []
                for row in cur.fetchall():
                    row['created_at'] = row['created_at'].isoformat()
                    events.append(row)
                return events