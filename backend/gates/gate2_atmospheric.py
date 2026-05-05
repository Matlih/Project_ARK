import os
import sys
import subprocess
import tempfile
import numpy as np
import rasterio
from rasterio.enums import Resampling
from pathlib import Path
from typing import List, Union

# Import your Data Models and Ingestion helpers
from backend.gates.gate1_sensor_qa import GateResult
from backend.gates.ingestion import find_band_file

def _run_fallback_cloud_mask(safe_dir: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Indestructible Fallback: Pure math NDSI cloud approximation.
    Executes if Fmask 4.0 crashes or is not installed.
    """
    print("⚠️ Fmask failed or not found. Engaging pure-math NDSI fallback...")
    
    b03_path = find_band_file(safe_dir, "B03_10m.jp2")  # Green
    b11_path = find_band_file(safe_dir, "B11_20m.jp2")  # SWIR
    
    with rasterio.open(b03_path) as src_b03:
        b03 = src_b03.read(1)
        valid_mask = b03 > 0
        H, W = b03.shape
        
        # Read B11 (20m) and upsample to B03 (10m) dimensions dynamically
        with rasterio.open(b11_path) as src_b11:
            b11 = src_b11.read(
                1,
                out_shape=(H, W),
                resampling=Resampling.bilinear
            )
            
    # Sentinel-2 L2A values are scaled by 10000. 
    # B03 > 0.2 (2000) & B11 < 0.1 (1000)
    cloud_mask = (b03 > 2000) & (b11 < 1000) & valid_mask
    
    # Fallback does not accurately calculate shadow, returning zeros
    shadow_mask = np.zeros_like(cloud_mask)
    
    return cloud_mask, shadow_mask, valid_mask


def run_gate2(scene_dir: Union[str, Path], ag_precision: bool = False) -> GateResult:
    """
    Executes Gate 2: Atmospheric Screening.
    Attempts Fmask 4.0, falls back to NDSI math on failure.
    """
    gate_name = "Gate 2: Atmospheric (Fmask/NDSI)"
    safe_dir = Path(scene_dir)
    
    cloud_mask = None
    shadow_mask = None
    valid_mask = None
    
    try:
        # Step 1: Attempt Fmask Execution
        with tempfile.TemporaryDirectory() as tmpdir:
            out_fmask = Path(tmpdir) / "fmask_out.tif"
            
            # This triggers the standard python-fmask CLI tool
            fmask_cmd = [
                "fmask_sentinel2Stacked.py", 
                "-o", str(out_fmask), 
                "--safedir", str(safe_dir)
            ]
            
            result = subprocess.run(fmask_cmd, capture_output=True, text=True)
            
            if result.returncode != 0 or not out_fmask.exists():
                raise RuntimeError(f"Fmask subprocess failed: {result.stderr}")
            
            # Fmask 4.0 Standard Codes: 2=Shadow, 4=Cloud, 255=No Data
            with rasterio.open(out_fmask) as src:
                fmask_data = src.read(1)
                valid_mask = fmask_data != 255
                cloud_mask = (fmask_data == 4) & valid_mask
                shadow_mask = (fmask_data == 2) & valid_mask
                
    except Exception as e:
        # STEP 2: The Indestructible Fallback
        try:
            cloud_mask, shadow_mask, valid_mask = _run_fallback_cloud_mask(safe_dir)
        except Exception as fallback_e:
            return GateResult(
                gate_name=gate_name, status="FAIL", confidence=1.0,
                reason=f"Total Atmospheric Failure: {str(fallback_e)}",
                compute_saved_hrs=1.85, metrics={}
            )

    # --- Step 3: Calculate Percentages ---
    total_valid = np.sum(valid_mask)
    if total_valid == 0:
        return GateResult(
            gate_name=gate_name, status="FAIL", confidence=1.0,
            reason="No valid scene data found.", compute_saved_hrs=1.85, metrics={}
        )
        
    cloud_pct = np.sum(cloud_mask) / total_valid
    shadow_pct = np.sum(shadow_mask) / total_valid
    
    # --- Step 4: Partial Extraction Check (Center 40%) ---
    H, W = cloud_mask.shape
    h_start, h_end = int(H * 0.3), int(H * 0.7)
    w_start, w_end = int(W * 0.3), int(W * 0.7)
    
    center_valid = valid_mask[h_start:h_end, w_start:w_end]
    center_cloud = cloud_mask[h_start:h_end, w_start:w_end]
    
    center_total_valid = np.sum(center_valid)
    center_cloud_pct = np.sum(center_cloud) / center_total_valid if center_total_valid > 0 else 1.0

    # --- Step 5: Evaluation Logic ---
    metrics = {
        "cloud_pct": round(float(cloud_pct), 4),
        "shadow_pct": round(float(shadow_pct), 4),
        "center_cloud_pct": round(float(center_cloud_pct), 4),
        "ag_precision_mode": ag_precision
    }
    
    threshold = 0.05 if ag_precision else 0.20
    
    if cloud_pct > threshold:
        # Check for Partial Pass
        if center_cloud_pct < 0.10:
            return GateResult(
                gate_name=gate_name, status="PARTIAL_PASS", confidence=0.85,
                reason=f"High total cloud ({cloud_pct:.1%}), but AOI center is clear ({center_cloud_pct:.1%}). Extracting center.",
                compute_saved_hrs=0.0, metrics=metrics
            )
        else:
            return GateResult(
                gate_name=gate_name, status="FAIL", confidence=0.95,
                reason=f"Cloud cover ({cloud_pct:.1%}) exceeds threshold ({threshold:.1%}). Center is obscured.",
                compute_saved_hrs=1.85, metrics=metrics
            )

    return GateResult(
        gate_name=gate_name, status="PASS", confidence=0.98,
        reason="Atmospheric interference within acceptable limits.",
        compute_saved_hrs=0.0, metrics=metrics
    )

def run_gate2_batch(paths: List[Union[str, Path]], ag_precision: bool = False) -> List[GateResult]:
    """Processes a batch of atmospheric checks sequentially."""
    return [run_gate2(p, ag_precision) for p in paths]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/gates/gate2_atmospheric.py <path_to_SAFE_folder>")
        sys.exit(1)
        
    target_path = sys.argv[1]
    print(f"Executing Gate 2 Atmospheric QA on: {os.path.basename(target_path)}\n")
    
    result = run_gate2(target_path)
    
    print(f"--- {result.gate_name} ---")
    print(f"Status:             {result.status}")
    print(f"Confidence:         {result.confidence}")
    print(f"Reason:             {result.reason}")
    print(f"Compute Saved (Hr): {result.compute_saved_hrs}")
    print("Metrics:")
    for k, v in result.metrics.items():
        print(f"  - {k}: {v}")