"""
config.py
---------
Central configuration for the fog node.

This module currently focuses on Twilio credentials used for
OTP / security verification.

Usage
=====
- Set the following environment variables on the host running the fog node:
  - TWILIO_ACCOUNT_SID
  - TWILIO_AUTH_TOKEN
  - TWILIO_VERIFY_SERVICE_SID
"""

import os
from pathlib import Path


def _load_local_env_file() -> None:
    """
    Optional helper: load Twilio env vars from a local os.env file
    if they are not already set in the process environment.

    This allows running the app without manually exporting variables
    every time in PowerShell.
    """
    base_dir = Path(__file__).resolve().parent
    env_path = base_dir / "os.env"

    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Support lines like:
        #   setx TWILIO_ACCOUNT_SID "ACxxxx"
        # We only care about the key and value.
        parts = line.split()
        if len(parts) < 3:
            continue

        # Example: ["setx", "TWILIO_ACCOUNT_SID", "\"ACxxxx\""]
        key = parts[1]
        value = " ".join(parts[2:]).strip().strip('"')

        # Only set if not already present
        if key not in os.environ and value:
            os.environ[key] = value


# Load from os.env (if present) before reading the variables
_load_local_env_file()


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")


def is_twilio_configured() -> bool:
    """
    Returns True if all required Twilio settings are present.
    """
    return all(
        [
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN,
            TWILIO_VERIFY_SERVICE_SID,
        ]
    )

