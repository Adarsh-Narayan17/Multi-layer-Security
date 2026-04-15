# fog_node/ml/detector.py

import joblib
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

try:
    import pandas as pd  # type: ignore
except ImportError:
    pd = None
from datetime import datetime
import warnings

# Get the absolute path of the directory this script is in
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(_CURRENT_DIR, "anomaly_model.pkl")
FREQ_MAP_PATH = os.path.join(_CURRENT_DIR, "device_freq_map.pkl")
SCALER_PATH = os.path.join(_CURRENT_DIR, "scaler.pkl")
OPENHAB_DATASET = os.path.join(_CURRENT_DIR, "../../datasets/OpenHAB - Activity and Location Labels.csv")

# Load model, frequency mapping, and scaler
try:
    model = joblib.load(MODEL_PATH)
    device_freq_map = joblib.load(FREQ_MAP_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception:
    model = None
    device_freq_map = {}
    scaler = None


def get_current_activity_intensity(hour: int) -> int:
    """
    Simulate real-time behavioral context by fetching typical 
    activity intensity for the given hour from the OpenHAB dataset.
    """
    try:
        if os.path.exists(OPENHAB_DATASET):
            oh_df = pd.read_csv(OPENHAB_DATASET)
            oh_df['hour'] = pd.to_datetime(oh_df['unix_timestamp'], unit='ms').dt.hour
            intensity = oh_df[oh_df['hour'] == hour].shape[0]
            return intensity
    except Exception:
        pass
    return 0


def extract_features(context: dict) -> list:
    """
    Extract features matching the training model:
    [hour, failed_attempts, device_freq, activity_intensity]
    """
    access_hour = context["access_time"].hour
    failed_attempts = context["failed_attempts"]
    
    device_id = context.get("device_id", 1)
    # Get device frequency from map, default to 1 if not seen before
    device_freq = device_freq_map.get(device_id, 1)
    
    activity_intensity = context.get("activity_intensity", 0)

    return [access_hour, failed_attempts, device_freq, activity_intensity]


def is_anomalous(context: dict) -> bool:
    """
    Returns True if access attempt is anomalous.
    """
    if not model or not scaler:
        return False  # Fail-open

    features = extract_features(context)
    
    # Scale features before prediction
    features_scaled = scaler.transform([features])
    
    prediction = model.predict(features_scaled)

    return prediction[0] == -1