"""
Test script to simulate access attempts and verify they're saved to AWS.
This simulates both failed and successful access attempts.
"""

import time
import uuid
from datetime import datetime

from storage.local_store import store_log
from storage.sync import trigger_sync, _sync_worker
from utils.logger import log_info

print("=" * 70)
print("TEST: Simulating Access Attempts and Verifying AWS Storage")
print("=" * 70)

# Test 1: Failed RFID attempt
print("\n[TEST 1] Simulating FAILED RFID attempt...")
store_log({
    "rfid": "RFID-TEST-FAIL-001",
    "access_result": "DENIED",
    "reason": "INVALID_RFID"
})
log_info("Stored: Failed RFID attempt")
trigger_sync()

# Test 2: Failed PIN attempt
print("\n[TEST 2] Simulating FAILED PIN attempt...")
store_log({
    "rfid": "RFID-1001",
    "user_id": "user1",
    "access_result": "DENIED",
    "reason": "INVALID_PIN"
})
log_info("Stored: Failed PIN attempt")
trigger_sync()

# Test 3: Failed OTP attempt
print("\n[TEST 3] Simulating FAILED OTP attempt...")
store_log({
    "rfid": "RFID-1001",
    "user_id": "user1",
    "access_result": "DENIED",
    "reason": "INVALID_OTP"
})
log_info("Stored: Failed OTP attempt")
trigger_sync()

# Test 4: ML Anomaly detection failure
print("\n[TEST 4] Simulating ML ANOMALY detection (DENIED)...")
store_log({
    "rfid": "RFID-1001",
    "user_id": "user1",
    "access_result": "DENIED",
    "anomaly": True,
    "reason": "ML_ANOMALY"
})
log_info("Stored: ML Anomaly detection failure")
trigger_sync()

# Test 5: Successful access (GRANTED)
print("\n[TEST 5] Simulating SUCCESSFUL access (GRANTED)...")
store_log({
    "rfid": "RFID-1001",
    "user_id": "user1",
    "access_result": "GRANTED",
    "reason": "MFA_SUCCESS"
})
log_info("Stored: Successful access")
trigger_sync()

# Test 6: Another successful access
print("\n[TEST 6] Simulating another SUCCESSFUL access...")
store_log({
    "rfid": "RFID-1002",
    "user_id": "user2",
    "access_result": "GRANTED",
    "reason": "MFA_SUCCESS"
})
log_info("Stored: Another successful access")
trigger_sync()

print("\n" + "=" * 70)
print("Waiting 3 seconds for background sync threads to complete...")
print("=" * 70)
time.sleep(3)

# Force sync all remaining logs
print("\n[SYNC] Forcing final sync of all unsynced logs...")
_sync_worker()

print("\n" + "=" * 70)
print("Test complete! Now verifying in AWS...")
print("=" * 70)
