# fog_node/ml/test_model.py

import pandas as pd  # type: ignore
import joblib
from sklearn.metrics import classification_report, confusion_matrix
import os

# Get the absolute path of the directory this script is in
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

RFID_DATASET = os.path.join(_CURRENT_DIR, "../../datasets/rfid_access_logs.csv")
OPENHAB_DATASET = os.path.join(_CURRENT_DIR, "../../datasets/OpenHAB - Activity and Location Labels.csv")
MODEL_PATH = os.path.join(_CURRENT_DIR, "anomaly_model.pkl")
SCALER_PATH = os.path.join(_CURRENT_DIR, "scaler.pkl")
FREQ_MAP_PATH = os.path.join(_CURRENT_DIR, "device_freq_map.pkl")

def evaluate():
    if not os.path.exists(MODEL_PATH):
        print("Model not found. Please run train_model.py first.")
        return

    # Load artifacts
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    device_freq_map = joblib.load(FREQ_MAP_PATH)

    # Load and Preprocess data
    rfid_df = pd.read_csv(RFID_DATASET)
    oh_df = pd.read_csv(OPENHAB_DATASET)
    oh_df['hour'] = pd.to_datetime(oh_df['unix_timestamp'], unit='ms').dt.hour
    behavior_context = oh_df.groupby('hour').size().reset_index(name='activity_intensity')
    
    test_df = pd.merge(rfid_df, behavior_context, on='hour', how='left').fillna(0)
    test_df['device_freq'] = test_df['device_id'].map(device_freq_map).fillna(1)

    # Prepare features and true labels
    X = test_df[["hour", "failed_attempts", "device_freq", "activity_intensity"]]
    y_true = test_df['label'].apply(lambda x: -1 if x == 'anomalous' else 1)

    # Scale and Predict
    X_scaled = scaler.transform(X)
    y_pred = model.predict(X_scaled)

    # Report
    print("\n" + "="*50)
    print("ML MODEL PERFORMANCE REPORT")
    print("="*50)
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=['Anomaly', 'Normal']))
    print("="*50)

if __name__ == "__main__":
    evaluate()