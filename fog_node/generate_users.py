import pandas as pd  # type: ignore
import json
import bcrypt
import pyotp
import os

DATASET_PATH = "../datasets/rfid_access_logs.csv"
USERS_FILE = "users.json"

def generate_users():
    print("Reading dataset...")
    df = pd.read_csv(DATASET_PATH)
    unique_rfids = df['rfid'].unique()
    
    # Calculate max failed attempts for each RFID from dataset
    # We use the max value found for each RFID in the CSV as their specific threshold
    thresholds = df.groupby('rfid')['failed_attempts'].max().to_dict()
    
    users_db = {}
    
    print(f"Generating credentials for {len(unique_rfids)} unique RFIDs...")
    for i, rfid in enumerate(unique_rfids):
        user_id = f"user_{rfid.replace('RFID-', '')}"
        
        # Get threshold from dataset, default to 3 if not found
        max_threshold = int(thresholds.get(rfid, 3))
        
        # Generate a simple alphanumeric PIN for testing (e.g., Pin1001)
        raw_pin = f"Pin{rfid.replace('RFID-', '')}"
        hashed_pin = bcrypt.hashpw(raw_pin.encode(), bcrypt.gensalt()).decode('utf-8')
        
        users_db[rfid] = {
            "user_id": user_id,
            "active": True,
            "pin_hash": hashed_pin,
            "raw_pin_for_testing": raw_pin,
            "otp_secret": pyotp.random_base32(),
            "phone": "+919471419637",
            "max_failed_threshold": max_threshold
        }
        
    with open(USERS_FILE, "w") as f:
        json.dump(users_db, f, indent=4)
        
    print(f"Successfully generated {USERS_FILE}")

if __name__ == "__main__":
    generate_users()
import pandas as pd  # type: ignore
import json
import bcrypt
import pyotp
import os

DATASET_PATH = "../datasets/rfid_access_logs.csv"
USERS_FILE = "users.json"

def generate_users():
    print("Reading dataset...")
    df = pd.read_csv(DATASET_PATH)
    unique_rfids = df['rfid'].unique()
    
    # Calculate max failed attempts for each RFID from dataset
    # We use the max value found for each RFID in the CSV as their specific threshold
    thresholds = df.groupby('rfid')['failed_attempts'].max().to_dict()
    
    users_db = {}
    
    print(f"Generating credentials for {len(unique_rfids)} unique RFIDs...")
    for i, rfid in enumerate(unique_rfids):
        user_id = f"user_{rfid.replace('RFID-', '')}"
        
        # Get threshold from dataset, default to 3 if not found
        max_threshold = int(thresholds.get(rfid, 3))
        
        # Generate a simple alphanumeric PIN for testing (e.g., Pin1001)
        raw_pin = f"Pin{rfid.replace('RFID-', '')}"
        hashed_pin = bcrypt.hashpw(raw_pin.encode(), bcrypt.gensalt()).decode('utf-8')
        
        users_db[rfid] = {
            "user_id": user_id,
            "active": True,
            "pin_hash": hashed_pin,
            "raw_pin_for_testing": raw_pin,
            "otp_secret": pyotp.random_base32(),
            "phone": "+919471419637",
            "max_failed_threshold": max_threshold
        }
        
    with open(USERS_FILE, "w") as f:
        json.dump(users_db, f, indent=4)
        
    print(f"Successfully generated {USERS_FILE}")

if __name__ == "__main__":
    generate_users()