# fog_node/ml/train_model.py

import pandas as pd  # type: ignore[import]
from sklearn.ensemble import IsolationForest
import joblib
import os
from datetime import datetime

# Get the absolute path of the directory this script is in
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

RFID_DATASET = os.path.join(_CURRENT_DIR, "../../datasets/rfid_access_logs.csv")
OPENHAB_DATASET = os.path.join(_CURRENT_DIR, "../../datasets/OpenHAB - Activity and Location Labels.csv")
MODEL_PATH = os.path.join(_CURRENT_DIR, "anomaly_model.pkl")
SCALER_PATH = os.path.join(_CURRENT_DIR, "scaler.pkl")
FREQ_MAP_PATH = os.path.join(_CURRENT_DIR, "device_freq_map.pkl")


def train():
    # Load RFID logs
    rfid_df = pd.read_csv(RFID_DATASET)
    
    # Calculate device frequency (how often each device appears in the logs)
    device_counts = rfid_df['device_id'].value_counts().to_dict()
    rfid_df['device_freq'] = rfid_df['device_id'].map(device_counts)
    
    # Load OpenHAB behavioral data
    oh_df = pd.read_csv(OPENHAB_DATASET)
    
    # Convert timestamp to hour to match RFID logs
    oh_df['hour'] = pd.to_datetime(oh_df['unix_timestamp'], unit='ms').dt.hour
    
    # Calculate behavioral context
    behavior_context = oh_df.groupby('hour').size().reset_index(name='activity_intensity')
    
    # Merge the datasets
    train_df = pd.merge(rfid_df, behavior_context, on='hour', how='left').fillna(0)

    # Feature selection based on your logic: [hour, failed_attempts, device_freq, activity_intensity]
    X = train_df[["hour", "failed_attempts", "device_freq", "activity_intensity"]]

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    model.fit(X)

    # Save artifacts for real-time detection
    joblib.dump(model, MODEL_PATH)
    joblib.dump(device_counts, FREQ_MAP_PATH)
    
    print("IsolationForest model and Frequency Map implemented successfully.")


if __name__ == "__main__":
    train()