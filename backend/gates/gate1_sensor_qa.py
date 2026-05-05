import sys
import numpy as np
import rasterio
from pathlib import Path
from dataclasses import dataclass
from typing import Literal, List, Union

@dataclass
class GateResult:
    gate_name: str
    status: Literal["PASS", "FAIL"]
    confidence: float
    reason: str
    compute_saved_hrs: float
    metrics: dict

def run_gate1(image_path: Union[str, Path]) -> GateResult:
    """
    Executes Gate 1: Sensor Quality Assessment on a single Sentinel-2 L2A band.
    Focuses on Dead Pixels, Saturation, SNR, and Striping.
    """
    gate_name = "Gate 1: Sensor QA"
    
    try:
        with rasterio.open(str(image_path)) as src:
            img = src.read(1)
    except Exception as e:
        return GateResult(
            gate_name=gate_name,
            status="FAIL",
            confidence=1.0,
            reason=f"File read error: {str(e)}",
            compute_saved_hrs=0.42,
            metrics={}
        )

    # Base valid mask (Sentinel-2 nodata is typically 0)
    valid_mask = img > 0
    if not np.any(valid_mask):
        return GateResult(
            gate_name=gate_name,
            status="FAIL",
            confidence=1.0,
            reason="Image contains no valid data.",
            compute_saved_hrs=0.42,
            metrics={"valid_pixels": 0}
        )

    valid_pixels = img[valid_mask]
    H, W = img.shape
    
    # --- Check 1: Dead Pixels ---
    # Find the bounding box of the valid scene to exclude exterior nodata
    rows = np.any(valid_mask, axis=1)
    cols = np.any(valid_mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    scene_bbox = img[rmin:rmax+1, cmin:cmax+1]
    dead_pixel_count = np.sum(scene_bbox == 0)
    dead_pixel_pct = dead_pixel_count / scene_bbox.size

    # --- Check 2: Saturation ---
    # L2A surface reflectance is scaled by 10000. Values >= 10000 are likely saturated/clouds
    sat_count = np.sum(valid_pixels >= 10000)
    sat_pct = sat_count / valid_pixels.size

    # --- Check 3: SNR Estimate ---
    # Signal = mean of valid pixels
    signal = np.mean(valid_pixels)
    
    # Noise = std deviation of a homogeneous center region (~10% of image area)
    # sqrt(0.1) ≈ 0.316. Taking the middle ~1/3 of both dimensions.
    h_start, h_end = int(H * 0.33), int(H * 0.66)
    w_start, w_end = int(W * 0.33), int(W * 0.66)
    center_region = img[h_start:h_end, w_start:w_end]
    center_valid = center_region[center_region > 0]
    
    noise = np.std(center_valid) if center_valid.size > 0 else 0
    snr = signal / noise if noise > 1e-6 else float('inf')

    # --- Check 4: Striping ---
    # Compute row-wise variance across valid data within the bounding box
    row_means = [np.mean(row[row > 0]) for row in scene_bbox if np.any(row > 0)]
    if len(row_means) > 0:
        row_variance_coefficient = np.std(row_means) / (np.mean(row_means) + 1e-6)
    else:
        row_variance_coefficient = float('inf')

    # --- Evaluation Logic ---
    metrics = {
        "dead_pixel_pct": round(float(dead_pixel_pct), 5),
        "saturated_pct": round(float(sat_pct), 5),
        "snr": round(float(snr), 2),
        "row_variance_coefficient": round(float(row_variance_coefficient), 5),
    }

    fail_reasons = []
    if dead_pixel_pct > 0.005:
        fail_reasons.append(f"Dead pixels ({dead_pixel_pct:.2%}) > 0.5%")
    if sat_pct > 0.01:
        fail_reasons.append(f"Saturation ({sat_pct:.2%}) > 1.0%")
    if snr < 20:
        fail_reasons.append(f"SNR ({snr:.1f}) < 20")
    if row_variance_coefficient > 0.15:
        fail_reasons.append(f"Striping coeff ({row_variance_coefficient:.3f}) > 0.15")

    if fail_reasons:
        return GateResult(
            gate_name=gate_name,
            status="FAIL",
            confidence=0.95,
            reason=" | ".join(fail_reasons),
            compute_saved_hrs=0.42,
            metrics=metrics
        )
    
    return GateResult(
        gate_name=gate_name,
        status="PASS",
        confidence=0.98,
        reason="All sensor tolerances nominal.",
        compute_saved_hrs=0.0,
        metrics=metrics
    )

def run_gate1_batch(paths: List[Union[str, Path]]) -> List[GateResult]:
    """Processes a batch of sensor checks sequentially."""
    return [run_gate1(p) for p in paths]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/gates/gate1_sensor_qa.py <path_to_jp2>")
        sys.exit(1)
        
    target_path = sys.argv[1]
    print(f"Executing Gate 1 QA on: {target_path}\n")
    
    result = run_gate1(target_path)
    
    print(f"--- {result.gate_name} ---")
    print(f"Status:             {result.status}")
    print(f"Confidence:         {result.confidence}")
    print(f"Reason:             {result.reason}")
    print(f"Compute Saved (Hr): {result.compute_saved_hrs}")
    print("Metrics:")
    for k, v in result.metrics.items():
        print(f"  - {k}: {v}")