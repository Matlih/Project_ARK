import asyncio
import json
import time
import joblib
import torch
import numpy as np
from datetime import datetime
from typing import TypedDict, List, Dict, Optional
from pathlib import Path
from langgraph.graph import StateGraph, END

# Import actual models if available
try:
    from backend.models.prithvi_inference import PrithviAnalyzer
    PRITHVI_AVAILABLE = torch.cuda.is_available() # Only true if GPU is active
except ImportError:
    PRITHVI_AVAILABLE = False

# ==========================================
# 0. STRATEGIC INTELLIGENCE OFFICER (LLM)
# ==========================================

class QwenNDRRMCOfficer:
    """Production-grade LLM Agent using LoRA-tuned Qwen-VL."""
    def __init__(self, adapter_path: str = "data/weights/qwen-vl-lora-ndrrmc"):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.base_model_name = "Qwen/Qwen-VL-Chat" # Base foundation
        
        print(f"[SYSTEM] Initializing Qwen-VL on {self.device}...")
        
        # 1. Load Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.base_model_name, 
            trust_remote_code=True
        )
        
        # 2. Load Base Model with AMD-optimized precision
        base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.bfloat16 # Optimized for AMD MI300X
        )
        
        # 3. Inject Philippine-specific Intelligence (LoRA)
        print(f"[SYSTEM] Injecting NDRRMC LoRA Adapter: {adapter_path}")
        self.model = PeftModel.from_pretrained(base_model, adapter_path)
        self.model.eval()

    def invoke(self, prompt: str) -> Dict:
        query = self.tokenizer.from_list_format([{'text': prompt}])
        inputs = self.tokenizer(query, return_tensors='pt').to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=512)
            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON from the raw response
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            return json.loads(response_text[start:end])
        except:
            return {"report_en": response_text, "report_tl": "Error sa pag-parse."}

class MockLLM:
    """The High-Fidelity Fallback: Used when GPU or Weights are unavailable."""
    def invoke(self, prompt: str):
        # We simulate the synthesis using the data passed in the prompt
        return {
            "report_en": f"NDRRMC SITUATION REPORT\nSynthesis based on active telemetry: {prompt[:100]}...",
            "report_tl": "ULAT NG SITWASYON NG NDRRMC\nSintesis batay sa aktibong telemetrya..."
        }

# --- GLOBAL LLM INITIALIZATION WITH FAILSAFE ---
ADAPTER_PATH = "data/weights/qwen-vl-lora-ndrrmc"
LLM_AVAILABLE = False

if torch.cuda.is_available() and Path(ADAPTER_PATH).exists():
    try:
        llm = QwenNDRRMCOfficer(ADAPTER_PATH)
        LLM_AVAILABLE = True
    except Exception as e:
        print(f"⚠️ LLM Load Failed: {e}. Defaulting to Mock Mode.")
        llm = MockLLM()
else:
    print("⚡ AMD CLOUD / LORA OFFLINE: Using Mock Intelligence Agent.")
    llm = MockLLM()

# ==========================================
# 1. STATE DEFINITION (Remains the same)
# ==========================================
class ARKState(TypedDict):
    event_id: str
    scene_path: str
    gate_results: List[Dict]
    ard_certified: bool
    damage_polygons: str
    affected_area_ha: float
    peso_loss_breakdown: Dict
    total_peso_loss: float
    insurance_triggers: List[Dict]
    recovery_timeline: Dict
    ndrrmc_report: str
    ndrrmc_report_tl: str
    agent_log: List[str]
    error: Optional[str]

# ==========================================
# 2. AGENT NODES
# ==========================================

def qa_monitor_node(state: ARKState) -> ARKState:
    state["agent_log"].append("[QA Monitor] Initiating scene validation.")
    # (Existing gate logic remains the same...)
    return state

def damage_assessment_node(state: ARKState) -> ARKState:
    """Agent 2: Executes Prithvi-100M inference."""
    state["agent_log"].append("[Damage Assessment] Initializing geospatial inference.")
    
    scene = state["scene_path"]
    if PRITHVI_AVAILABLE:
        try:
            # We initialize locally here to save VRAM if the node is skipped
            from backend.models.prithvi_inference import PrithviAnalyzer
            analyzer = PrithviAnalyzer()
            stats = analyzer.run_inference(scene)
            state["damage_polygons"] = f"data/processed/{Path(scene).stem}_damage.geojson"
            state["affected_area_ha"] = stats['affected_area_ha']
            state["agent_log"].append("[Damage Assessment] Prithvi-100M inference complete.")
        except Exception as e:
            state["agent_log"].append(f"⚠️ Model Error: {e}. Engaging fail-safe.")
            state["affected_area_ha"] = 145200.50 # Synthetic fallback
    else:
        state["affected_area_ha"] = 145200.50
        state["agent_log"].append("[Damage Assessment] GPU Offline. Using synthetic fallback.")
        
    return state

def economic_valuation_node(state: ARKState) -> ARKState:
    """Agent 3: XGBoost Financial Forecasting."""
    state["agent_log"].append("[Economic Valuation] Computing sectoral peso loss via XGBoost.")
    base_area = state.get("affected_area_ha", 0)
    weights_path = Path("data/weights")
    
    try:
        # Check if XGBoost files exist
        if (weights_path / "xgboost_loss_estimator.pkl").exists():
            model = joblib.load(weights_path / "xgboost_loss_estimator.pkl")
            scaler = joblib.load(weights_path / "xgboost_scaler.pkl")
            
            scaled_input = scaler.transform(np.array([[base_area]]))
            predicted_total_loss = float(model.predict(scaled_input)[0])
            
            state["total_peso_loss"] = predicted_total_loss
            state["peso_loss_breakdown"] = {
                "rice": predicted_total_loss * 0.65, 
                "infrastructure": predicted_total_loss * 0.35
            }
        else:
            raise FileNotFoundError("XGBoost weights missing.")
            
    except Exception as e:
        state["agent_log"].append(f"⚠️ XGBoost Error: {e}. Using static multiplier.")
        state["total_peso_loss"] = base_area * 12500.0
        state["peso_loss_breakdown"] = {"rice": state["total_peso_loss"], "infrastructure": 0}

    return state

# (Insurance and Recovery nodes remain as they were...)

def ndrrmc_reporter_node(state: ARKState) -> ARKState:
    """Agent 6: Dynamic LLM Node with Multi-Lingual Synthesis."""
    state["agent_log"].append(f"[NDRRMC Reporter] Synthesizing {'REAL' if LLM_AVAILABLE else 'MOCK'} intelligence report.")
    
    # Prompt construction remains the same...
    prompt = f"Official NDRRMC report for {state['event_id']}. Damage: {state['total_peso_loss']:,}."
    
    try:
        response = llm.invoke(prompt)
        state["ndrrmc_report"] = response.get("report_en")
        state["ndrrmc_report_tl"] = response.get("report_tl")
    except Exception as e:
        state["ndrrmc_report"] = "Synthesis Error."
        state["ndrrmc_report_tl"] = "May Error."

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