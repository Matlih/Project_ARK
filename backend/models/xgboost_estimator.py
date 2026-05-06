import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import pickle
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# --- Configurations & Mappings ---
WEIGHTS_DIR = Path("data/weights")
MODEL_PATH = WEIGHTS_DIR / "xgboost_loss_estimator.pkl"
SCALER_PATH = WEIGHTS_DIR / "xgboost_scaler.pkl"

CROP_MAPPING = {0: "Rice", 1: "Corn", 2: "Vegetable", 3: "Other/Cash Crop"}

# Helper function to get province names (0-80)
def get_province_name(prov_id: int) -> str:
    # Top agricultural provinces mapped, fallback for others
    prov_map = {
        0: "Isabela", 1: "Nueva Ecija", 2: "Pangasinan", 3: "Cagayan", 
        4: "Iloilo", 5: "Camarines Sur", 6: "Tarlac", 7: "Cotabato",
        8: "Maguindanao", 9: "Bukidnon"
    }
    return prov_map.get(prov_id, f"Province_{prov_id}")

# --- Data Generation & Loading ---

def generate_synthetic_training_data(n_samples: int = 500) -> pd.DataFrame:
    """Generates a realistic synthetic dataset for model training."""
    print(f"Generating {n_samples} synthetic training samples...")
    np.random.seed(42)
    
    damage_area_ha = np.random.uniform(100, 50000, n_samples)
    crop_type = np.random.randint(0, 4, n_samples)
    province_id = np.random.randint(0, 81, n_samples)
    season = np.random.randint(0, 2, n_samples) # 0 = Wet, 1 = Dry
    ndvi_delta = np.random.uniform(-0.8, 0.0, n_samples)
    
    # Base valuation heuristics (Pesos per hectare)
    crop_values = {0: 55000, 1: 45000, 2: 75000, 3: 35000}
    base_value = np.array([crop_values[c] for c in crop_type])
    
    # Loss logic: Area * Value * Severity multiplier (NDVI drop)
    peso_loss = damage_area_ha * base_value * (1 + np.abs(ndvi_delta))
    
    # Add 10% real-world noise
    noise = np.random.normal(0, 0.10 * peso_loss)
    peso_loss = np.maximum(0, peso_loss + noise) # Floor at 0
    
    return pd.DataFrame({
        "damage_area_ha": damage_area_ha,
        "crop_type": crop_type,
        "province_id": province_id,
        "season": season,
        "ndvi_delta": ndvi_delta,
        "peso_loss": peso_loss
    })

def load_psa_data(csv_path: str | Path) -> pd.DataFrame:
    """Loads and standardizes real PSA Crop Loss data."""
    try:
        df = pd.read_csv(csv_path)
        # Flexible mapping logic: rename columns to match our standard schema
        col_mapping = {
            "Area_Affected_HA": "damage_area_ha",
            "Crop_ID": "crop_type",
            "Prov_Code": "province_id",
            "Season_Code": "season",
            "NDVI_Change": "ndvi_delta",
            "Estimated_Loss_PHP": "peso_loss"
        }
        df.rename(columns=lambda x: col_mapping.get(x, x), inplace=True)
        
        required_cols = ["damage_area_ha", "crop_type", "province_id", "season", "ndvi_delta", "peso_loss"]
        missing = [c for c in required_cols if c not in df.columns]
        
        if missing:
            raise ValueError(f"Missing required columns in PSA data: {missing}")
            
        return df[required_cols]
        
    except Exception as e:
        print(f"Failed to load PSA data: {e}. Falling back to synthetic.")
        return generate_synthetic_training_data()

# --- Model Training ---

def train_estimator(df: pd.DataFrame) -> xgb.XGBRegressor:
    """Trains the XGBoost model and saves artifacts to disk."""
    print("\n--- Training XGBoost Economic Loss Estimator ---")
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    
    X = df.drop(columns=["peso_loss"])
    y = df["peso_loss"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
        objective='reg:squarederror'
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluation
    preds = model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    
    print(f"Model Performance:")
    print(f"  - RMSE: PHP {rmse:,.2f}")
    print(f"  - R2 Score: {r2:.4f}")
    
    print("Feature Importance:")
    importances = model.feature_importances_
    for col, imp in zip(X.columns, importances):
        print(f"  - {col}: {imp:.4f}")
        
    # Serialize the artifacts
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, "wb") as f:
        # Also store the RMSE in the scaler object to calculate confidence intervals later
        scaler.validation_rmse = rmse 
        pickle.dump(scaler, f)
        
    print(f"\n✅ Weights saved to: {WEIGHTS_DIR}")
    return model

# --- Inference Layer ---

def predict_loss(damage_area_ha: float, crop_type: int, 
                 province_id: int, season: int, ndvi_delta: float) -> dict:
    """Loads weights and runs inference on a single damage event."""
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        raise FileNotFoundError("Model weights not found. Run training first.")
        
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
        
    input_data = pd.DataFrame([{
        "damage_area_ha": damage_area_ha,
        "crop_type": crop_type,
        "province_id": province_id,
        "season": season,
        "ndvi_delta": ndvi_delta
    }])
    
    scaled_data = scaler.transform(input_data)
    est_loss = float(model.predict(scaled_data)[0])
    
    # Calculate approx 10th/90th percentiles using validation RMSE
    # Z-score for 80% CI is ~1.28
    margin = 1.28 * getattr(scaler, 'validation_rmse', est_loss * 0.15)
    ci_lower = max(0.0, est_loss - margin)
    ci_upper = est_loss + margin
    
    return {
        "peso_loss_estimate": round(est_loss, 2),
        "confidence_interval": (round(ci_lower, 2), round(ci_upper, 2)),
        "crop_type_label": CROP_MAPPING.get(crop_type, "Unknown"),
        "province_name": get_province_name(province_id)
    }

if __name__ == "__main__":
    print("==========================================")
    print("🛰️ PROJECT ARK - XGBoost Loss Estimator")
    print("==========================================")
    
    # 1. Train Model
    training_data = generate_synthetic_training_data()
    train_estimator(training_data)
    
    # 2. Test Inference
    print("\n--- Running Test Inferences ---")
    tests = [
        {"damage_area_ha": 1500, "crop_type": 0, "province_id": 1, "season": 0, "ndvi_delta": -0.65}, # Severe Rice Damage
        {"damage_area_ha": 300, "crop_type": 2, "province_id": 9, "season": 1, "ndvi_delta": -0.20},  # Mild Veg Damage
        {"damage_area_ha": 12000, "crop_type": 1, "province_id": 0, "season": 0, "ndvi_delta": -0.80} # Catastrophic Corn Damage
    ]
    
    for i, t in enumerate(tests, 1):
        res = predict_loss(**t)
        print(f"\nTest {i} ({res['province_name']} - {res['crop_type_label']}):")
        print(f"  Inputs: {t['damage_area_ha']} HA, NDVI Drop: {t['ndvi_delta']}")
        print(f"  Estimated Loss: PHP {res['peso_loss_estimate']:,.2f}")
        print(f"  80% Confidence: PHP {res['confidence_interval'][0]:,.2f} to {res['confidence_interval'][1]:,.2f}")