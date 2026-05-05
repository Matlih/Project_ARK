import os
from backend.gates.ingestion import find_band_file
from backend.gates.gate1_sensor_qa import run_gate1
from backend.gates.gate2_atmospheric import run_gate2

RAW_DIR = "data/raw"
TEST_REGIONS = ["Luzon_Typhoon", "Visayas_Agri", "Mindanao_Coast"]

print("==========================================")
print("🛰️ PROJECT ARK - PIPELINE INTEGRATION TEST")
print("==========================================")

for region in TEST_REGIONS:
    region_path = os.path.join(RAW_DIR, region)
    
    try:
        # 1. Locate the .SAFE folder
        safe_dirs = [d for d in os.listdir(region_path) if d.endswith(".SAFE")]
        if not safe_dirs:
            print(f"\n⚠️  Skipping {region}: No .SAFE folder found.")
            continue
            
        safe_folder_path = os.path.join(region_path, safe_dirs[0])
        b04_path = find_band_file(safe_folder_path, "B04_10m.jp2")
        
        print(f"\n" + "="*40)
        print(f"📍 TARGET: {region}")
        print("="*40)

# -----------------------------------------
        # GATE 1: SENSOR QA
        # -----------------------------------------
        print("\n[ GATE 1: SENSOR QA ]")
        g1_result = run_gate1(b04_path)
        g1_icon = "✅" if g1_result.status == "PASS" else "❌"
        
        print(f"   {g1_icon} {g1_result.status} (Confidence: {g1_result.confidence})")
        if g1_result.status == "FAIL":
            print(f"   🚨 Reason: {g1_result.reason}")
        if g1_result.compute_saved_hrs > 0:
            print(f"   ⏳ Compute Saved: {g1_result.compute_saved_hrs} hours")
        print(f"   📊 Metrics: {g1_result.metrics}")

        # -----------------------------------------
        # GATE 2: ATMOSPHERIC SCREENING
        # -----------------------------------------
        print("\n[ GATE 2: ATMOSPHERIC (Fmask/NDSI) ]")
        
        is_ag_target = (region == "Visayas_Agri")
        g2_result = run_gate2(safe_folder_path, ag_precision=is_ag_target)
        
        if g2_result.status == "PASS":
            g2_icon = "✅"
        elif g2_result.status == "PARTIAL_PASS":
            g2_icon = "⚠️"
        else:
            g2_icon = "❌"
            
        print(f"   {g2_icon} {g2_result.status} (Confidence: {g2_result.confidence})")
        if g2_result.status == "FAIL":
            print(f"   🚨 Reason: {g2_result.reason}")
        if g2_result.compute_saved_hrs > 0:
            print(f"   ⏳ Compute Saved: {g2_result.compute_saved_hrs} hours")
        print(f"   📊 Metrics: {g2_result.metrics}")

    except Exception as e:
        print(f"\n❌ Error processing {region}: {e}")

print("\n==========================================")
print("Pipeline Test Complete.")
print("==========================================")