

import bcrypt
import json

USERS_FILE = "users.json"

def _load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

USER_DB = _load_users()

def verify_pin(user_id: str, entered_pin: str) -> bool:
    # Find the user by user_id
    for rfid, data in USER_DB.items():
        if data.get("user_id") == user_id:
            stored_hash = data.get("pin_hash")
            if not stored_hash:
                return False
            return bcrypt.checkpw(entered_pin.encode(), stored_hash.encode())
    return False