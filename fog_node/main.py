# fog_node/main.py

from rate_limit.limiter import (
    is_locked,
    is_permanently_locked,
    record_failure,
    record_success,
    get_failed_attempts
)
from ml.detector import is_anomalous, get_current_activity_intensity
from datetime import datetime
import time
from auth.rfid import simulate_rfid_scan, verify_rfid
from auth.pin import verify_pin
from auth.otp import send_otp, verify_otp
from storage.local_store import store_log
from storage.sync import trigger_sync
from utils.logger import log_info, log_warning, log_event

SESSION_TIMEOUT_SECONDS = 60


def main():
    # ==============================
    # RFID SCAN
    # ==============================
    rfid = simulate_rfid_scan()
    session_start = time.time()

    if is_locked(rfid):
        reason = "PERMANENT_LOCK" if is_permanently_locked(rfid) else "RATE_LIMIT_LOCK"
        store_log({
            "rfid": rfid,
            "access_result": "DENIED",
            "reason": reason
        })
        trigger_sync()

        log_warning(f"Lock triggered: {reason}")
        log_event(reason, {"rfid": rfid})
        return

    user = verify_rfid(rfid)

    if not user:
        record_failure(rfid)
        store_log({
            "rfid": rfid,
            "access_result": "DENIED",
            "reason": "INVALID_RFID"
        })
        trigger_sync()

        log_warning("Invalid RFID attempt")
        log_event("INVALID_RFID", {"rfid": rfid})
        return

    # ==============================
    # PIN VERIFICATION
    # ==============================
    pin = input("Enter Alphanumeric PIN: ")

    # Check alphanumeric requirement
    if not pin.isalnum():
        record_failure(rfid, permanent=True)
        store_log({
            "rfid": rfid,
            "user_id": user["user_id"],
            "access_result": "DENIED",
            "reason": "NON_ALPHANUMERIC_PIN"
        })
        trigger_sync()
        log_warning("Non-alphanumeric PIN attempt recorded")
        log_event("NON_ALPHANUMERIC_PIN", {"rfid": rfid, "user_id": user["user_id"]})
        return

    # Check session timeout
    if time.time() - session_start > SESSION_TIMEOUT_SECONDS:
        record_failure(rfid)
        store_log({
            "rfid": rfid,
            "user_id": user["user_id"],
            "access_result": "DENIED",
            "reason": "SESSION_TIMEOUT"
        })
        trigger_sync()
        log_warning("Authentication session timed out at PIN stage")
        log_event("SESSION_TIMEOUT", {"rfid": rfid, "user_id": user["user_id"]})
        return

    if not verify_pin(user["user_id"], pin):
        record_failure(rfid)
        store_log({
            "rfid": rfid,
            "user_id": user["user_id"],
            "access_result": "DENIED",
            "reason": "INVALID_PIN"
        })
        trigger_sync()

        log_warning("Invalid PIN")
        log_event("INVALID_PIN", {"rfid": rfid, "user_id": user["user_id"]})
        return

    # ==============================
    # OTP VERIFICATION
    # ==============================
    # Check session timeout before sending OTP
    if time.time() - session_start > SESSION_TIMEOUT_SECONDS:
        record_failure(rfid)
        store_log({
            "rfid": rfid,
            "user_id": user["user_id"],
            "access_result": "DENIED",
            "reason": "SESSION_TIMEOUT"
        })
        trigger_sync()
        log_warning("Authentication session timed out before OTP send")
        log_event("SESSION_TIMEOUT", {"rfid": rfid, "user_id": user["user_id"]})
        return

    # Send OTP via Twilio (if configured) or fall back to local TOTP.
    if not send_otp(user["user_id"]):
        record_failure(rfid)
        store_log({
            "rfid": rfid,
            "user_id": user["user_id"],
            "access_result": "DENIED",
            "reason": "OTP_SEND_FAILED"
        })
        trigger_sync()

        log_warning("Failed to send OTP")
        log_event("OTP_SEND_FAILED", {"rfid": rfid, "user_id": user["user_id"]})
        return

    otp = input("Enter OTP sent to your registered phone: ")

    # Check session timeout
    if time.time() - session_start > SESSION_TIMEOUT_SECONDS:
        record_failure(rfid)
        store_log({
            "rfid": rfid,
            "user_id": user["user_id"],
            "access_result": "DENIED",
            "reason": "SESSION_TIMEOUT"
        })
        trigger_sync()
        log_warning("Authentication session timed out at OTP stage")
        log_event("SESSION_TIMEOUT", {"rfid": rfid, "user_id": user["user_id"]})
        return

    if not verify_otp(user["user_id"], otp):
        record_failure(rfid)
        store_log({
            "rfid": rfid,
            "user_id": user["user_id"],
            "access_result": "DENIED",
            "reason": "INVALID_OTP"
        })
        trigger_sync()

        log_warning("Invalid OTP")
        log_event("INVALID_OTP", {"rfid": rfid, "user_id": user["user_id"]})
        return

    # ==============================
    # ML ANOMALY DETECTION (FOG)
    # ==============================
    now = datetime.utcnow()
    context = {
        "access_time": now,
        "failed_attempts": get_failed_attempts(rfid),
        "device_id": 1,
        "activity_intensity": get_current_activity_intensity(now.hour)
    }

    if is_anomalous(context):
        record_failure(rfid)
        store_log({
            "rfid": rfid,
            "user_id": user["user_id"],
            "access_result": "DENIED",
            "anomaly": True,
            "reason": "ML_ANOMALY"
        })
        trigger_sync()

        log_warning("ML anomaly detected")
        log_event("ML_ANOMALY", {
            "rfid": rfid,
            "user_id": user["user_id"],
            "failed_attempts": context["failed_attempts"]
        })
        return

    # ==============================
    # ACCESS GRANTED
    # ==============================
    record_success(rfid)

    store_log({
        "rfid": rfid,
        "user_id": user["user_id"],
        "access_result": "GRANTED",
        "reason": "MFA_SUCCESS"
    })

    trigger_sync()

    log_info("Locker Opened")
    log_event("ACCESS_GRANTED", {
        "rfid": rfid,
        "user_id": user["user_id"]
    })


if __name__ == "__main__":
    main()