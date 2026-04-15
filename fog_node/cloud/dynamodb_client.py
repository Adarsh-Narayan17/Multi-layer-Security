"""
dynamodb_client.py
------------------
Handles communication between fog node and AWS DynamoDB.
Cloud is used ONLY for persistence & audit.
"""

import json
import uuid

import boto3
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    PartialCredentialsError,
)

from utils.logger import log_info, log_warning, log_error
from utils.timezone import now_ist_iso

# ======================
# Configuration
# ======================

# Region must match Terraform deployment.
AWS_REGION = "ap-south-1"

# Must match your Terraform-created resources.
ACCESS_LOGS_TABLE = "smart-locker-fog-audit"
S3_AUDIT_BUCKET = "smart-locker-fog-audit-bucket"


# ======================
# AWS Clients
# ======================

try:
    _session = boto3.session.Session(region_name=AWS_REGION)
    
    # Check credentials before creating clients
    credentials = _session.get_credentials()
    if not credentials:
        log_error(
            "AWS credentials not found! Configure credentials using: "
            "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables, "
            "or ~/.aws/credentials file, or IAM role (if on EC2)."
        )
        dynamodb = None
        access_logs_table = None
        s3_client = None
    else:
        dynamodb = _session.resource("dynamodb")
        access_logs_table = dynamodb.Table(ACCESS_LOGS_TABLE)
        s3_client = _session.client("s3")
        log_info(
            f"Initialized AWS clients for region={AWS_REGION}, "
            f"table={ACCESS_LOGS_TABLE}, bucket={S3_AUDIT_BUCKET}"
        )
except (NoCredentialsError, PartialCredentialsError) as exc:
    log_error(
        f"AWS credentials error: {exc}. "
        "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
    )
    dynamodb = None
    access_logs_table = None
    s3_client = None
except Exception as exc:  # pragma: no cover - defensive init
    log_error(f"Failed to initialize AWS clients: {type(exc).__name__}: {exc}")
    dynamodb = None
    access_logs_table = None
    s3_client = None


# ======================
# Cloud Write Operations
# ======================

def push_access_log(log: dict) -> bool:
    """
    Push access log to DynamoDB.
    This function MUST NOT affect fog authentication flow.

    Args:
        log (dict): Access log data

    Returns:
        bool: True if uploaded, False if failed
    """
    if not access_logs_table and not s3_client:
        log_warning("AWS clients not initialized; skipping cloud sync.")
        return False

    log_id = str(uuid.uuid4())
    timestamp = now_ist_iso()

    item = {
        "log_id": log_id,
        "rfid": log.get("rfid"),
        "user_id": log.get("user_id"),
        "access_result": log.get("access_result"),
        "anomaly": log.get("anomaly", True),
        "reason": log.get("reason", ""),
        "timestamp": timestamp,
    }

    success_dynamo = False
    success_s3 = False

    # ----------------------
    # DynamoDB write
    # ----------------------
    if access_logs_table is not None:
        try:
            log_info("Uploading audit log to DynamoDB...")
            access_logs_table.put_item(Item=item)
            log_info("DynamoDB upload successful.")
            success_dynamo = True
        except NoCredentialsError:
            log_error(
                "DynamoDB: No AWS credentials. "
                "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
            )
        except EndpointConnectionError:
            log_warning("DynamoDB endpoint unreachable; device may be offline.")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            log_error(f"DynamoDB Error [{error_code}]: {error_msg}")
        except Exception as exc:  # pragma: no cover - defensive
            log_error(f"Unexpected DynamoDB error: {type(exc).__name__}: {exc}")

    # ----------------------
    # S3 write (JSON object)
    # ----------------------
    if s3_client is not None:
        try:
            log_info("Uploading audit log to S3...")
            key = f"logs/{timestamp[:10]}/{log_id}.json"
            s3_client.put_object(
                Bucket=S3_AUDIT_BUCKET,
                Key=key,
                Body=json.dumps(item).encode("utf-8"),
                ContentType="application/json",
            )
            log_info("S3 upload successful.")
            success_s3 = True
        except NoCredentialsError:
            log_error(
                "S3: No AWS credentials. "
                "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
            )
        except EndpointConnectionError:
            log_warning("S3 endpoint unreachable; device may be offline.")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            log_error(f"S3 upload error [{error_code}]: {error_msg}")
        except Exception as exc:  # pragma: no cover - defensive
            log_error(f"Unexpected S3 error: {type(exc).__name__}: {exc}")
    return success_dynamo or success_s3