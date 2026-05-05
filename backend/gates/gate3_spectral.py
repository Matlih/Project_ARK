import sys
import numpy as np
import rasterio
from rasterio.enums import Resampling
from pathlib import Path
from typing import Union

# Import your Data Models and Ingestion helpers
from backend.gates.gate1_sensor_qa import GateResult
from backend.gates.ingestion import find_band_file

def _load_and_normalize(safe_dir: Path, band_suffix: str, target_shape: tuple = None) -> np.ndarray:
    """Loads a JP2 band, resamples if target_shape is provided, and normalizes to [0, 1]."""
    path = find_band_file(safe_dir, band_suffix)
    with rasterio.open(path) as src:
        if target_shape:
            # Resample 20m bands (like B11) to 10m
            arr = src.read(1, out_shape=target_shape, resampling=Resampling.bilinear)
        else:
            arr = src.read(1)
            
    # Sentinel-2 L2A optical depth scaling
    return arr.astype(np.float32) / 10000.0

def run_gate3(scene_dir: Union[str, Path], season: str = "wet") -> GateResult:
    """
    Executes Gate 3: Spectral Calibration Validation.
    Validates physical reflectance limits and index sanity using pure math.
    """
    gate_name = "Gate 3: Spectral Calibration"
    safe_dir = Path(scene_dir)
    
    try:
        # Load 10m Bands
        b04 = _load_and_normalize(safe_dir, "B04_10m.jp2") # Red
        b08 = _load_and_normalize(safe_dir, "B08_10m.jp2") # NIR
        b03 = _load_and_normalize(safe_dir, "B03_10m.jp2") # Green
        
        target_shape = b04.shape
        
        # Load 20m Band and upsample to 10m geometry
        b11 = _load_and_normalize(safe_dir, "B11_20m.jp2", target_shape=target_shape) # SWIR1
        
    except Exception as e:
        return GateResult(
            gate_name=gate_name, status="FAIL", confidence=1.0,
            reason=f"Band loading/resampling failed: {str(e)}",
            compute_saved_hrs=1.2, metrics={}
        )

    # -----------------------------------------
    # Check 1: NDVI Validity Limits
    # -----------------------------------------
    ndvi = (b08 - b04) / (b08 + b04 + 1e-8)
    valid_ndvi_mask = (b08 > 0.01) | (b04 > 0.01)
    valid_ndvi = ndvi[valid_ndvi_mask]
    
    if valid_ndvi.size == 0:
        return GateResult(gate_name, "FAIL", 1.0, "No valid reflectance data for NDVI.", 1.2, {})

    ndvi_mean = float(np.mean(valid_ndvi))
    
    # Physical limits check
    if np.any(valid_ndvi < -1.0) or np.any(valid_ndvi > 1.0):
        return GateResult(gate_name, "FAIL", 0.99, "NDVI out of absolute bounds [-1, 1]", 1.2, {"ndvi_mean": ndvi_mean})
        
    # Calibration sanity check
    if ndvi_mean < -0.3:
        reason = f"Mean NDVI ({ndvi_mean:.3f}) is suspiciously low. Possible sensor drift."
        metrics = {"qwen_prompt": f"Describe spectral calibration issue: NDVI={ndvi_mean:.3f}, Red/NIR abnormal."}
        return GateResult(gate_name, "FAIL", 0.90, reason, 1.2, metrics)

    # -----------------------------------------
    # Check 2: NDWI Water Index Sanity
    # -----------------------------------------
    ndwi = (b03 - b11) / (b03 + b11 + 1e-8)
    ndwi_std = float(np.std(ndwi[valid_ndvi_mask])) # Use same valid mask
    
    if ndwi_std < 0.01:
        reason = f"NDWI variance ({ndwi_std:.4f}) approaches zero. Image likely blank/corrupt."
        metrics = {"qwen_prompt": f"Describe spectral calibration issue: NDWI_std={ndwi_std:.4f} is too flat."}
        return GateResult(gate_name, "FAIL", 0.95, reason, 1.2, metrics)

    # -----------------------------------------
    # Check 3: Band Ratio Seasonal Check
    # -----------------------------------------
    red_nir_ratio = float(np.mean(b04[valid_ndvi_mask]) / (np.mean(b08[valid_ndvi_mask]) + 1e-8))
    seasonal_norms = {"wet": (0.1, 0.8), "dry": (0.2, 1.2)}
    
    # Default to wet if invalid season string is passed
    season = season if season in seasonal_norms else "wet"
    min_norm, max_norm = seasonal_norms[season]
    
    if red_nir_ratio < min_norm or red_nir_ratio > max_norm:
        reason = f"Red/NIR ratio ({red_nir_ratio:.3f}) violates {season} season baseline {seasonal_norms[season]}."
        metrics = {"qwen_prompt": f"Describe spectral calibration issue: Red/NIR ratio={red_nir_ratio:.3f} out of bounds."}
        return GateResult(gate_name, "FAIL", 0.85, reason, 1.2, metrics)

    # -----------------------------------------
    # Final Pass
    # -----------------------------------------
    metrics = {
        "ndvi_mean": round(ndvi_mean, 4),
        "ndwi_std": round(ndwi_std, 4),
        "red_nir_ratio": round(red_nir_ratio, 4),
        "season_profile": season
    }
    
    return GateResult(
        gate_name=gate_name, status="PASS", confidence=0.98,
        reason="Spectral signatures match expected Earth-observation physics.",
        compute_saved_hrs=0.0, metrics=metrics
    )