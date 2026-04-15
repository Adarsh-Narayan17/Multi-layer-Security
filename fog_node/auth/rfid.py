"""
rfid.py
-------
Simulates RFID-based authentication for the fog node.
"""

import json
from typing import Optional, Dict

USERS_FILE = "users.json"


def _load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


REGISTERED_RFID_TAGS = _load_users()


def normalize_rfid(rfid_id: str) -> str:
    """
    Normalize RFID input to standard format.
    """
    rfid_id = rfid_id.strip()

    # Convert numeric input like "1001" -> "RFID-1001"
    if rfid_id.isdigit():
        rfid_id = f"RFID-{rfid_id}"

    return rfid_id.upper()


def verify_rfid(rfid_id: str) -> Optional[Dict]:
    """
    Verify RFID tag against the loaded user database.

    Args:
        rfid_id (str): RFID tag ID

    Returns:
        dict | None: User metadata if valid, else None
    """
    user = REGISTERED_RFID_TAGS.get(rfid_id)

    if not user:
        return None

    if not user.get("active", False):
        return None

    return user


def simulate_rfid_scan() -> str:
    """
    Simulates RFID scan via terminal input.
    """
    raw_input = input("Scan RFID Tag: ")
    return normalize_rfid(raw_input)