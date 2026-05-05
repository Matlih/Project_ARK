import os
from pathlib import Path
import rasterio
import numpy as np

def find_band_file(safe_folder_path: str, band_suffix: str) -> str:
    """
    Recursively searches a .SAFE folder for a specific band resolution.
    Example band_suffix: 'B04_10m.jp2'
    """
    safe_dir = Path(safe_folder_path)
    # rglob searches all subdirectories dynamically
    matches = list(safe_dir.rglob(f"*{band_suffix}"))
    
    if not matches:
        raise FileNotFoundError(f"Could not find {band_suffix} in {safe_folder_path}")
    
    return str(matches[0])

def load_sentinel_bands(safe_folder_path: str):
    """
    Extracts the Red (B04) and NIR (B08) 10m bands from a .SAFE folder
    and returns them as NumPy arrays for Gate 3 (NDVI) math.
    """
    print(f"🛰️ Ingesting ARD from: {os.path.basename(safe_folder_path)}")
    
    # 1. Dynamically locate the files
    red_path = find_band_file(safe_folder_path, "B04_10m.jp2")
    nir_path = find_band_file(safe_folder_path, "B08_10m.jp2")
    
    # 2. Load into NumPy via Rasterio
    with rasterio.open(red_path) as src_red:
        # Read the first (and only) band in the jp2 file
        red_array = src_red.read(1)
        # We grab the profile in case we need to export GeoTIFFs later
        meta_profile = src_red.profile 
        
    with rasterio.open(nir_path) as src_nir:
        nir_array = src_nir.read(1)
        
    print(f"✅ Tensors loaded. Shape: {red_array.shape}")
    return red_array, nir_array, meta_profile

# --- Test Block ---
if __name__ == "__main__":
    # Test this immediately on your Luzon data
    luzon_path = "../../data/raw/Luzon_Typhoon"
    
    # We need the actual name of the .SAFE folder inside Luzon_Typhoon
    try:
        # Find the first .SAFE folder in the directory
        safe_dirs = [os.path.join(luzon_path, d) for d in os.listdir(luzon_path) if d.endswith(".SAFE")]
        if safe_dirs:
            target_safe = safe_dirs[0]
            red, nir, profile = load_sentinel_bands(target_safe)
            print("Ready for Gate 3 Processing.")
        else:
            print("❌ No .SAFE folder found in Luzon_Typhoon.")
    except Exception as e:
        print(f"Error during ingestion: {e}")