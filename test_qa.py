import os
from backend.gates.ingestion import find_band_file
from backend.gates.gate1_sensor_qa import run_gate1

RAW_DIR = "data/raw"
TEST_REGIONS = ["Luzon_Typhoon", "Visayas_Agri", "Mindanao_Coast"]

print("==========================================")
print("🛰️ PROJECT ARK - GATE 1 INTEGRATION TEST")
print("==========================================")

for region in TEST_REGIONS:
    region_path = os.path.join(RAW_DIR, region)
    
    # 1. Look for the .SAFE folder in the region directory
    try:
        safe_dirs = [d for d in os.listdir(region_path) if d.endswith(".SAFE")]
        if not safe_dirs:
            print(f"\n⚠️  Skipping {region}: No .SAFE folder found.")
            continue
            
        safe_folder_path = os.path.join(region_path, safe_dirs[0])
        
        # 2. Use your ingestion script to find the Red Band (B04)
        b04_path = find_band_file(safe_folder_path, "B04_10m.jp2")
        
        # 3. Feed the path into Gate 1
        print(f"\n🔍 Processing {region}...")
        result = run_gate1(b04_path)
        
        # 4. Display the results
        status_icon = "✅" if result.status == "PASS" else "❌"
        print(f"   {status_icon} {result.status} (Confidence: {result.confidence})")
        
        if result.status == "FAIL":
            print(f"   🚨 Reason: {result.reason}")
            print(f"   ⏳ Compute Saved: {result.compute_saved_hrs} hours")
            
        print(f"   📊 Metrics: {result.metrics}")
        
    except Exception as e:
        print(f"\n❌ Error processing {region}: {e}")

print("\n==========================================")
print("Test Complete.")
print("==========================================")