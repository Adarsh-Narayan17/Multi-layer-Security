"""
otp.py
------
Handles OTP verification.

This module now prefers Twilio Verify for sending and checking OTPs
for real-world security verification, while keeping a local TOTP-based
fallback for offline/demo use.
"""

import json
from typing import Any, Dict

import pyotp

try:
    from twilio.rest import Client  # type: ignore[import]
    _TWILIO_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    Client = object  # type: ignore[assignment]
    _TWILIO_AVAILABLE = False

from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_VERIFY_SERVICE_SID,
    is_twilio_configured,
)
from utils.logger import log_error, log_info, log_warning

USERS_FILE = "users.json"

def _load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

USER_DB = _load_users()


# ==============================
# Local TOTP fallback
# ==============================

def get_current_otp(user_id: str) -> str:
    """
    Generate current OTP (for testing/demo).

    Args:
        user_id (str): User identifier

    Returns:
        str: Current TOTP
    """
    for rfid, data in USER_DB.items():
        if data.get("user_id") == user_id:
            secret = data.get("otp_secret")
            if not secret:
                return ""
            totp = pyotp.TOTP(secret)
            return totp.now()
    return ""


def _verify_otp_local(user_id: str, entered_otp: str) -> bool:
    """
    Fallback: verify OTP using local TOTP if Twilio is not configured.
    """
    for rfid, data in USER_DB.items():
        if data.get("user_id") == user_id:
            secret = data.get("otp_secret")
            if not secret:
                return False
            totp = pyotp.TOTP(secret)
            return totp.verify(entered_otp)
    return False


# ==============================
# Twilio Verify configuration
# ==============================

def _get_twilio_client() -> Any:
    """
    Create a Twilio REST client.
    """
    if not _TWILIO_AVAILABLE:
        raise RuntimeError(
            "Twilio package is not installed. "
            "Install it with 'pip install twilio'."
        )
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_otp(user_id: str) -> bool:
    """
    Send an OTP to the user's phone using Twilio Verify.
    """
    if not is_twilio_configured():
        log_warning("Twilio not configured. OTP will be generated locally.")
        # For local testing, we can just show the OTP
        otp = get_current_otp(user_id)
        if otp:
            log_info(f"LOCAL OTP for {user_id}: {otp}")
            return True
        return False

    phone_number = None
    for rfid, data in USER_DB.items():
        if data.get("user_id") == user_id:
            phone_number = data.get("phone")
            break

    if not phone_number:
        log_error(f"No phone number configured for user_id={user_id}")
        return False

    client = _get_twilio_client()
    try:
        verification = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID).verifications.create(
            to=phone_number, channel="sms"
        )
        log_info(f"Twilio verification sent to {phone_number}, status={verification.status}")
        return verification.status == "pending"
    except Exception as e:
        log_error(f"Twilio API error: {e}")
        return False


def verify_otp(user_id: str, entered_otp: str) -> bool:
    """
    Verify OTP using Twilio or local fallback.
    """
    if not is_twilio_configured():
        return _verify_otp_local(user_id, entered_otp)

    phone_number = None
    for rfid, data in USER_DB.items():
        if data.get("user_id") == user_id:
            phone_number = data.get("phone")
            break

    if not phone_number:
        return False

    client = _get_twilio_client()
    try:
        verification_check = client.verify.v2.services(
            TWILIO_VERIFY_SERVICE_SID
        ).verification_checks.create(to=phone_number, code=entered_otp)
        log_info(f"Twilio verification check for user_id={user_id}, status={verification_check.status}")
        return verification_check.status == "approved"
    except Exception as e:
        log_error(f"Twilio API error on check: {e}")
        return False
