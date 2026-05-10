import asyncio
import json
import time
from datetime import datetime
from typing import TypedDict, List, Dict, Optional
from pathlib import Path
from langgraph.graph import StateGraph, END

# Import actual models if available
try:
    from backend.models.prithvi_inference import PrithviAnalyzer
    PRITHVI_AVAILABLE = True
except ImportError:
    PRITHVI_AVAILABLE = False

# Placeholder for LLM initialization 
# In production, this pulls your trained Qwen-VL LoRA
class MockLLM:
    def invoke(self, prompt: str):
        # Extract dynamic data if possible, or use the high-fidelity mock
        report_en = """NDRRMC SITUATION REPORT NO. 1
AS OF: May 2026

AFFECTED AREA: 127,000 hectares — Cagayan Valley
ECONOMIC IMPACT: ₱3.22 Billion

Rice: ₱1.8B
Corn: ₱340M
Vegetables: ₱190M
Infrastructure: ₱890M

INSURANCE TRIGGERS:
• Rice parametric policy — ACTIVATED
• Infrastructure bond — ACTIVATED
Estimated payout: ₱2.1B

PRIORITY MUNICIPALITIES:
1. Tuguegarao — 72hrs
2. Solana — 96hrs
3. Iguig — 120hrs"""

        report_tl = """ULAT NG SITWASYON NG NDRRMC BLG. 1
PETSA: Mayo 2026

APEKTADONG LUGAR: 127,000 ektarya — Lambak ng Cagayan
EPEKTONG PANG-EKONOMIYA: ₱3.22 Bilyon

Palay: ₱1.8B
Mais: ₱340M
Gulay: ₱190M
Imprastraktura: ₱890M

PARAMETRIC NA SEGURONG NA-ACTIVATE:
• Segurong Palay — AKTIBO
• Bono sa Imprastraktura — AKTIBO"""

        return {
            "report_en": report_en,
            "report_tl": report_tl
        }

llm = MockLLM()

# ==========================================
# 1. STATE DEFINITION
# ==========================================
class ARKState(TypedDict):
    event_id: str
    scene_path: str
    gate_results: List[Dict]
    ard_certified: bool
    damage_polygons: str         # GeoJSON file path
    affected_area_ha: float
    peso_loss_breakdown: Dict    # {rice: float, corn: float, infra: float}
    total_peso_loss: float
    insurance_triggers: List[Dict]
    recovery_timeline: Dict      # {municipality: days}
    ndrrmc_report: str           # Final English report text
    ndrrmc_report_tl: str        # Final Tagalog report text
    agent_log: List[str]         # Trace of all agent decisions
    error: Optional[str]

# ==========================================
# 2. AGENT NODES
# ==========================================

def qa_monitor_node(state: ARKState) -> ARKState:
    """Agent 1: Monitors input quality and ARD compliance."""
    state["agent_log"].append("[QA Monitor] Initiating scene validation.")
    
    gate_2_rejections = [g for g in state["gate_results"] if g.get("gate") == 2 and not g.get("passed")]
    if len(gate_2_rejections) > 0:
        rejection_rate = gate_2_rejections[0].get("rejection_rate", 0)
        if rejection_rate > 0.60:
            state["agent_log"].append(f"⚠️ ALERT: Cloud spike detected ({rejection_rate*100}%).")
    
    if not state["ard_certified"]:
        state["agent_log"].append("[QA Monitor] Scene failed ARD. Halting.")
        state["error"] = "ARD Certification Failed."
    else:
        state["agent_log"].append("[QA Monitor] Scene ARD certified. Proceeding to inference.")
        
    return state

def damage_assessment_node(state: ARKState) -> ARKState:
    """Agent 2: Executes Prithvi-100M inference."""
    global PRITHVI_AVAILABLE
    state["agent_log"].append("[Damage Assessment] Initializing geospatial inference.")
    
    scene = state["scene_path"]
    if PRITHVI_AVAILABLE:
        try:
            analyzer = PrithviAnalyzer()
            stats = analyzer.run_inference(scene)
            state["damage_polygons"] = f"data/processed/{Path(scene).stem}_damage.geojson"
            state["affected_area_ha"] = stats['affected_area_ha']
            state["agent_log"].append("[Damage Assessment] Prithvi inference complete.")
        except Exception as e:
            state["agent_log"].append(f"[Damage Assessment] Model error: {e}. Falling back to mocks.")
            PRITHVI_AVAILABLE = False

    if not PRITHVI_AVAILABLE:
        state["damage_polygons"] = f"data/processed/{Path(scene).stem}_damage_mock.geojson"
        state["affected_area_ha"] = 145200.50
        state["agent_log"].append("[Damage Assessment] Synthetic damage assessment completed.")
        
    return state

def economic_valuation_node(state: ARKState) -> ARKState:
    """Agent 3: Calculates financial damages."""
    state["agent_log"].append("[Economic Valuation] Computing sectoral peso loss.")
    base_area = state.get("affected_area_ha", 0)
    
    rice_loss = base_area * 12500.0
    infra_loss = 890_000_000 # DPWH default metric
    
    state["peso_loss_breakdown"] = {
        "rice": rice_loss,
        "infrastructure": infra_loss
    }
    state["total_peso_loss"] = sum(state["peso_loss_breakdown"].values())
    state["agent_log"].append(f"[Economic Valuation] Total loss estimated at PHP {state['total_peso_loss']:,.2f}")
    
    return state

def insurance_trigger_node(state: ARKState) -> ARKState:
    """Agent 4: Authorizes instant liquidity."""
    state["agent_log"].append("[Insurance Trigger] Evaluating parametric conditions.")
    triggers = []
    
    if state["total_peso_loss"] > 500_000_000:
        triggers.append({"policy": "PCIC Micro-Insurance", "status": "TRIGGERED", "amount": 250_000_000})
        
    state["insurance_triggers"] = triggers
    state["agent_log"].append(f"[Insurance Trigger] Authorized {len(triggers)} liquidity channels.")
    return state

def recovery_planner_node(state: ARKState) -> ARKState:
    """Agent 5: Strategizes deployment timelines."""
    state["agent_log"].append("[Recovery Planner] Ranking LGU prioritization.")
    state["recovery_timeline"] = {
        "Tuguegarao City": "72 Hours (Alpha Priority)",
        "Aparri": "96 Hours (Bravo Priority)"
    }
    state["agent_log"].append("[Recovery Planner] Response timelines established.")
    return state

def ndrrmc_reporter_node(state: ARKState) -> ARKState:
    """
    Agent 6: The dynamic LLM node.
    Synthesizes technical data into a government-ready bilingual SitRep using Qwen-VL.
    """
    state["agent_log"].append("[NDRRMC Reporter] Synthesizing final multi-lingual intelligence report.")
    
    damage_data = f"{state.get('affected_area_ha', 0):,.0f} hectares affected"
    economic_data = state.get("total_peso_loss", 0)
    
    prompt = f"""
    You are the Project ARK Strategic Intelligence Officer. 
    Your task is to synthesize the following disaster data into an official NDRRMC Situation Report.
    
    DATA:
    - Event: {state['event_id']}
    - Estimated Damage: PHP {economic_data:,}
    - Affected Sector: {damage_data}
    - Recovery Priority: {json.dumps(state['recovery_timeline'])}

    OUTPUT REQUIREMENTS:
    1. Generate two distinct versions: 'report_en' and 'report_tl'.
    2. TONE: Highly formal, administrative, and urgent. 
    3. LANGUAGE SPECIFICS (Filipino): 
       - Do NOT use conversational Tagalog. 
       - Use 'Lalawigan' for province, 'Kagyat' for immediate, 'Pinsala' for damage.
       - Use formal administrative Philippine terminology.
    
    Return your response in JSON format with keys: "report_en" and "report_tl".
    """

    # Call the LoRA-tuned LLM
    try:
        # In actual use, this invokes the model and parses JSON output
        response = llm.invoke(prompt) 
        state["ndrrmc_report"] = response.get("report_en", "English report generation failed.")
        state["ndrrmc_report_tl"] = response.get("report_tl", "Walang ulat sa Tagalog.")
    except Exception as e:
        state["agent_log"].append(f"⚠️ Report LLM Error: {e}")
        state["ndrrmc_report"] = "Standard report fallback active."
        state["ndrrmc_report_tl"] = "Standard na ulat fallback."

    state["agent_log"].append("[NDRRMC Reporter] Strategic intelligence report finalized.")
    return state

# ==========================================
# 3. GRAPH CONSTRUCTION
# ==========================================
def should_proceed(state: ARKState):
    if state.get("error"):
        return END
    return "damage_assessment"

workflow = StateGraph(ARKState)

workflow.add_node("qa_monitor", qa_monitor_node)
workflow.add_node("damage_assessment", damage_assessment_node)
workflow.add_node("economic_valuation", economic_valuation_node)
workflow.add_node("insurance_trigger", insurance_trigger_node)
workflow.add_node("recovery_planner", recovery_planner_node)
workflow.add_node("ndrrmc_reporter", ndrrmc_reporter_node)

workflow.set_entry_point("qa_monitor")
workflow.add_conditional_edges("qa_monitor", should_proceed)
workflow.add_edge("damage_assessment", "economic_valuation")
workflow.add_edge("economic_valuation", "insurance_trigger")
workflow.add_edge("insurance_trigger", "recovery_planner")
workflow.add_edge("recovery_planner", "ndrrmc_reporter")
workflow.add_edge("ndrrmc_reporter", END)

app = workflow.compile()

# ==========================================
# 4. ENTRY POINT
# ==========================================
async def run_ark_pipeline(event_id: str, scene_path: str, gate_results: List[Dict]) -> ARKState:
    initial_state = ARKState(
        event_id=event_id,
        scene_path=scene_path,
        gate_results=gate_results,
        ard_certified=True,
        damage_polygons="",
        affected_area_ha=0.0,
        peso_loss_breakdown={},
        total_peso_loss=0.0,
        insurance_triggers=[],
        recovery_timeline={},
        ndrrmc_report="",
        ndrrmc_report_tl="",
        agent_log=[],
        error=None
    )
    
    print(f"\n[SYSTEM] Initializing Project ARK Pipeline for {event_id}...")
    result = await app.ainvoke(initial_state)
    return result

if __name__ == "__main__":
    async def test_run():
        mock_gates = [{"gate": 1, "passed": True}]
        final_state = await run_ark_pipeline("TYPHOON-CARINA-DEMO", "data/raw/Luzon", mock_gates)
        print("\n[REPORT PREVIEW]")
        print(final_state["ndrrmc_report"])
        
    asyncio.run(test_run())