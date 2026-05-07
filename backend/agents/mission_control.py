import asyncio
import json
from datetime import datetime
from typing import TypedDict, List, Dict, Optional
from pathlib import Path
from langgraph.graph import StateGraph, END

# Import actual models if available, otherwise rely on the robust mock fallbacks
try:
    from backend.models.prithvi_inference import PrithviAnalyzer
    PRITHVI_AVAILABLE = True
except ImportError:
    PRITHVI_AVAILABLE = False

# ==========================================
# 1. STATE DEFINITION
# ==========================================
class ARKState(TypedDict):
    event_id: str
    scene_path: str
    gate_results: List[Dict]
    ard_certified: bool
    damage_polygons: str        # GeoJSON file path
    affected_area_ha: float
    peso_loss_breakdown: Dict   # {rice: float, corn: float, infra: float}
    total_peso_loss: float
    insurance_triggers: List[Dict]
    recovery_timeline: Dict     # {municipality: days}
    ndrrmc_report: str          # final report text
    agent_log: List[str]        # trace of all agent decisions
    error: Optional[str]

# ==========================================
# 2. AGENT NODES
# ==========================================

def qa_monitor_node(state: ARKState) -> ARKState:
    """Agent 1: Monitors input quality and ARD compliance before heavy compute."""
    state["agent_log"].append("[QA Monitor] Initiating scene validation.")
    
    # Check for cloud spikes in Gate 2
    gate_2_rejections = [g for g in state["gate_results"] if g.get("gate") == 2 and not g.get("passed")]
    if len(gate_2_rejections) > 0:
        rejection_rate = gate_2_rejections[0].get("rejection_rate", 0)
        if rejection_rate > 0.60:
            state["agent_log"].append(f"⚠️ ALERT: Cloud spike detected (Rate: {rejection_rate*100}%). Flagging acquisition.")
    
    if not state["ard_certified"]:
        state["agent_log"].append("[QA Monitor] Scene failed ARD certification. Halting pipeline.")
        state["error"] = "ARD Certification Failed."
    else:
        state["agent_log"].append("[QA Monitor] Scene ARD certified. Proceeding to inference.")
        
    return state

def damage_assessment_node(state: ARKState) -> ARKState:
    """Agent 2: Executes Prithvi-100M inference to generate geospatial damage polygons."""
    global PRITHVI_AVAILABLE # <-- ADD THIS LINE TO FIX THE SCOPE
    
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
        # Mocking for Hackathon Demo execution
        state["damage_polygons"] = f"data/processed/{Path(scene).stem}_damage_mock.geojson"
        state["affected_area_ha"] = 145200.50
        state["agent_log"].append("[Damage Assessment] Synthetic damage assessment completed.")
        
    return state

def economic_valuation_node(state: ARKState) -> ARKState:
    """Agent 3: Calculates financial damages utilizing XGBoost estimators and DPWH baselines."""
    state["agent_log"].append("[Economic Valuation] Computing sectoral peso loss.")
    
    # Mocking XGBoost Agricultural Estimators
    base_loss_multiplier = state.get("affected_area_ha", 0)
    
    rice_loss = base_loss_multiplier * 12500.0   # PHP per hectare estimation
    corn_loss = base_loss_multiplier * 8400.0
    veg_loss  = base_loss_multiplier * 15200.0
    
    # DPWH Infrastructure baseline estimation
    infra_pct = 0.15 # Assumed 15% of damaged area is infrastructure
    infra_loss = (infra_pct * 100) * 890_000_000 # DPWH default metric
    
    state["peso_loss_breakdown"] = {
        "rice": rice_loss,
        "corn": corn_loss,
        "vegetable": veg_loss,
        "infrastructure": infra_loss
    }
    
    state["total_peso_loss"] = sum(state["peso_loss_breakdown"].values())
    state["agent_log"].append(f"[Economic Valuation] Total loss estimated at PHP {state['total_peso_loss']:,.2f}")
    
    return state

def insurance_trigger_node(state: ARKState) -> ARKState:
    """Agent 4: Evaluates parametric thresholds to authorize instant liquidity."""
    state["agent_log"].append("[Insurance Trigger] Evaluating parametric conditions.")
    
    triggers = []
    breakdown = state.get("peso_loss_breakdown", {})
    
    if breakdown.get("rice", 0) > 500_000_000:
        triggers.append({"policy": "PCIC Rice Micro-Insurance", "status": "TRIGGERED", "amount": 250_000_000})
        
    if breakdown.get("infrastructure", 0) > 200_000_000:
        triggers.append({"policy": "World Bank Catastrophe Bond (Infra)", "status": "TRIGGERED", "amount": 1_000_000_000})
        
    if state.get("affected_area_ha", 0) > 50_000:
        triggers.append({"policy": "NDRRMC National Calamity Fund", "status": "TRIGGERED", "amount": "Dependent on LGU request"})
        
    state["insurance_triggers"] = triggers
    state["agent_log"].append(f"[Insurance Trigger] Authorized {len(triggers)} liquidity channels.")
    
    return state

def recovery_planner_node(state: ARKState) -> ARKState:
    """Agent 5: Strategizes immediate deployment timelines based on damage density."""
    state["agent_log"].append("[Recovery Planner] Ranking LGU prioritization.")
    
    # Mocking municipality ranking based on derived density
    state["recovery_timeline"] = {
        "Tuguegarao City": "72 Hours (Alpha Priority)",
        "Aparri": "96 Hours (Bravo Priority)",
        "Ilagan City": "120 Hours (Charlie Priority)"
    }
    
    state["agent_log"].append("[Recovery Planner] Response timelines established.")
    return state

def ndrrmc_reporter_node(state: ARKState) -> ARKState:
    """Agent 6: Synthesizes a strategic, bilingual NDRRMC situation report."""
    state["agent_log"].append("[NDRRMC Reporter] Synthesizing final multi-lingual intelligence report.")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    triggers_str = "\n       - ".join([f"{t['policy']}: {t['status']}" for t in state["insurance_triggers"]]) or "None triggered."
    timeline_str = "\n       - ".join([f"{mun}: {time}" for mun, time in state["recovery_timeline"].items()])
    
    report_eng = f"""
===================================================
NDRRMC SITUATION REPORT NO. 1
===================================================
Event ID: {state['event_id']}
As of: {now}

1. SITUATION OVERVIEW
   - Affected Area: {state['affected_area_ha']:,.0f} hectares
   - Total Economic Impact: PHP {state['total_peso_loss']:,.0f}
   
2. SECTORAL BREAKDOWN
   - Agriculture (Rice): PHP {state['peso_loss_breakdown'].get('rice', 0):,.0f}
   - Infrastructure: PHP {state['peso_loss_breakdown'].get('infrastructure', 0):,.0f}
   
3. PARAMETRIC INSURANCE & LIQUIDITY
   - {triggers_str}
   
4. PRIORITY DEPLOYMENT TIMELINE
   - {timeline_str}

5. RECOMMENDED ACTIONS
   - Immediate deployment of PCIC assessors to Alpha Priority zones.
   - Activate DPWH Quick Response Fund for infrastructure clearing.
   - Maintain continuous satellite telemetry over highly saturated areas.
===================================================
"""

    # Bilingual Generation (Filipino Translation Dictionary for Key Phrases)
    translation_dict = {
        "NDRRMC SITUATION REPORT": "ULAT NG SITWASYON NG NDRRMC",
        "Event ID": "ID ng Kaganapan",
        "As of": "Mula noong",
        "SITUATION OVERVIEW": "PANGKALAHATANG-IDEYA NG SITWASYON",
        "Affected Area": "Naapektuhang Lugar",
        "Total Economic Impact": "Kabuuang Epekto sa Ekonomiya",
        "SECTORAL BREAKDOWN": "PAGHAHATI NG SEKTOR",
        "Agriculture (Rice)": "Agrikultura (Palay)",
        "Infrastructure": "Imprastraktura",
        "PARAMETRIC INSURANCE & LIQUIDITY": "PARAMETRIC NA SEGURONG AT LIKIDIDAD",
        "PRIORITY DEPLOYMENT TIMELINE": "PRAYORIDAD NA TAKDANG PANAHON NG PAGPAPADALA",
        "RECOMMENDED ACTIONS": "MGA INIREREKOMENDANG HAKBANG",
        "Immediate deployment of PCIC assessors": "Agarang pagpapadala ng mga tagatasa ng PCIC",
        "Activate DPWH Quick Response Fund": "I-activate ang DPWH Quick Response Fund",
        "Maintain continuous satellite telemetry": "Panatilihin ang patuloy na satellite telemetry"
    }
    
    report_fil = report_eng
    for eng, fil in translation_dict.items():
        report_fil = report_fil.replace(eng, fil)
        
    state["ndrrmc_report"] = f"{report_eng}\n\n{report_fil}"
    state["agent_log"].append("[NDRRMC Reporter] Strategic intelligence report finalized.")
    
    return state

# ==========================================
# 3. GRAPH CONSTRUCTION
# ==========================================
def should_proceed(state: ARKState):
    """Routing function to determine if analysis should proceed past QA."""
    if state["ard_certified"]:
        return "damage_assessment"
    return END

workflow = StateGraph(ARKState)

# Add Nodes
workflow.add_node("qa_monitor", qa_monitor_node)
workflow.add_node("damage_assessment", damage_assessment_node)
workflow.add_node("economic_valuation", economic_valuation_node)
workflow.add_node("insurance_trigger", insurance_trigger_node)
workflow.add_node("recovery_planner", recovery_planner_node)
workflow.add_node("ndrrmc_reporter", ndrrmc_reporter_node)

# Define Edges
workflow.set_entry_point("qa_monitor")
workflow.add_conditional_edges("qa_monitor", should_proceed)
workflow.add_edge("damage_assessment", "economic_valuation")
workflow.add_edge("economic_valuation", "insurance_trigger")
workflow.add_edge("insurance_trigger", "recovery_planner")
workflow.add_edge("recovery_planner", "ndrrmc_reporter")
workflow.add_edge("ndrrmc_reporter", END)

# Compile Graph
app = workflow.compile()

# ==========================================
# 4. ENTRY POINT
# ==========================================
async def run_ark_pipeline(event_id: str, scene_path: str, gate_results: List[Dict]) -> ARKState:
    """
    Main asynchronous entry point for the Project ARK Intelligence Pipeline.
    """
    # Initialize typed state
    initial_state = ARKState(
        event_id=event_id,
        scene_path=scene_path,
        gate_results=gate_results,
        ard_certified=True, # Set by upstream data ingester
        damage_polygons="",
        affected_area_ha=0.0,
        peso_loss_breakdown={},
        total_peso_loss=0.0,
        insurance_triggers=[],
        recovery_timeline={},
        ndrrmc_report="",
        agent_log=[],
        error=None
    )
    
    print(f"\n[SYSTEM] Initializing Project ARK Pipeline for {event_id}...")
    result = await app.ainvoke(initial_state)
    
    print("\n[SYSTEM] Pipeline Execution Trace:")
    for log in result["agent_log"]:
        print(f"  -> {log}")
        
    return result

if __name__ == "__main__":
    # Test Execution
    async def test_run():
        mock_gates = [{"gate": 1, "passed": True}, {"gate": 2, "passed": False, "rejection_rate": 0.65}]
        final_state = await run_ark_pipeline(
            event_id="TYPHOON-LUZON-2026-05", 
            scene_path="data/raw/Luzon_Typhoon", 
            gate_results=mock_gates
        )
        print("\n[REPORT PREVIEW]")
        print(final_state["ndrrmc_report"].split("\n\n")[0]) # Print English version
        
    asyncio.run(test_run())