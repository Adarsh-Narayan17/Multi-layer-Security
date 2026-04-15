# fog_node/rate_limit/limiter.py

import time
import json
import os
from utils.logger import log_warning

# =========================
# Configuration
# =========================

MAX_FAILED_ATTEMPTS = 3          # attempts before lock
LOCK_TIME_SECONDS = 60          # temporary lock time
STATE_FILE = "rate_limit_state.json"

# =========================
# Persistence Helper Functions
# =========================

def _load_state():
    """
    Load rate limit state from a local JSON file.
    """
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_state(state):
    """
    Save rate limit state to a local JSON file.
    """
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
    except IOError as e:
        print(f"Error saving rate limit state: {e}")


# =========================
# Core Logic
# =========================

def is_locked(identity: str) -> bool:
    """
    Check if identity (RFID or user_id) is currently locked.
    Returns True if either temporary or permanently locked.
    """
    state = _load_state()
    record = state.get(identity)
    if not record:
        return False

    # Check for permanent lock
    if record.get("permanently_locked", False):
        return True

    locked_until = record.get("locked_until", 0)
    return time.time() < locked_until


def is_permanently_locked(identity: str) -> bool:
    """
    Check if identity is permanently locked.
    """
    state = _load_state()
    record = state.get(identity)
    return record.get("permanently_locked", False) if record else False


def _get_user_threshold(identity: str) -> int:
    """
    Get the specific max failure threshold for a user from users.json.
    Defaults to MAX_FAILED_ATTEMPTS if not found.
    """
    try:
        with open("users.json", "r") as f:
            users_db = json.load(f)
            user_data = users_db.get(identity)
            if user_data:
                return user_data.get("max_failed_threshold", MAX_FAILED_ATTEMPTS)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return MAX_FAILED_ATTEMPTS


def trigger_permanent_lock(identity: str):
    """
    Immediately and permanently lock an identity.
    """
    state = _load_state()
    record = state.setdefault(identity, {"failed": 0, "locked_until": 0, "permanent_fails": 0, "permanently_locked": False})
    record["permanently_locked"] = True
    _save_state(state)


def record_failure(identity: str, permanent: bool = False):
    """
    Record a failed authentication attempt.
    If permanent=True, it tracks towards a permanent lock.
    If the number of failures exceeds the user's specific threshold from the dataset,
    the RFID is permanently locked.
    """
    state = _load_state()
    record = state.setdefault(identity, {"failed": 0, "locked_until": 0, "permanent_fails": 0, "permanently_locked": False})
    
    record["failed"] += 1
    
    # Get user-specific threshold from dataset
    threshold = _get_user_threshold(identity)

    # Check for permanent lock based on alphanumeric requirement
    if permanent:
        record["permanent_fails"] = record.get("permanent_fails", 0) + 1
        if record["permanent_fails"] >= 3:
            record["permanently_locked"] = True

    # Check for permanent lock based on the dataset threshold
    if record["failed"] >= threshold:
        record["permanently_locked"] = True
        log_warning(f"THRESHOLD EXCEEDED: RFID {identity} has been permanently terminated (failed_attempts={record['failed']}, threshold={threshold})")

    if record["failed"] >= MAX_FAILED_ATTEMPTS:
        record["locked_until"] = time.time() + LOCK_TIME_SECONDS
    
    _save_state(state)


def record_success(identity: str):
    """
    Reset failure count on successful authentication.
    """
    state = _load_state()
    if identity in state:
        state[identity] = {"failed": 0, "locked_until": 0}
        _save_state(state)


def get_failed_attempts(identity: str) -> int:
    """
    Return number of failed attempts (for ML features).
    """
    state = _load_state()
    record = state.get(identity)
    if not record:
        return 0
    return record.get("failed", 0)