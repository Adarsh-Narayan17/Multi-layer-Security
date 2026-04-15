"""
Test AWS connectivity and credentials.
Run this to diagnose why logs aren't uploading.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

AWS_REGION = "ap-south-1"
TABLE_NAME = "smart-locker-fog-audit"
BUCKET_NAME = "smart-locker-fog-audit-bucket"

print("=" * 60)
print("AWS Connection Diagnostic Test")
print("=" * 60)

# Test 1: Check credentials
print("\n[1] Checking AWS credentials...")
try:
    session = boto3.Session()
    credentials = session.get_credentials()
    if credentials:
        print(f"[OK] Credentials found: Access Key ID = {credentials.access_key[:10]}...")
    else:
        print("[ERROR] NO CREDENTIALS FOUND!")
        print("  Configure one of:")
        print("    - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars")
        print("    - AWS credentials file (~/.aws/credentials)")
        print("    - IAM role (if running on EC2)")
except Exception as e:
    print(f"[ERROR] Error checking credentials: {e}")

# Test 2: Test DynamoDB
print("\n[2] Testing DynamoDB connection...")
try:
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(TABLE_NAME)
    
    # Try to describe the table
    table.load()
    print(f"[OK] DynamoDB table '{TABLE_NAME}' exists")
    print(f"  Table ARN: {table.table_arn}")
    
    # Try a test write
    import uuid
    from datetime import datetime
    test_item = {
        "log_id": str(uuid.uuid4()),
        "rfid": "TEST-RFID",
        "user_id": "test_user",
        "access_result": "GRANTED",
        "reason": "DIAGNOSTIC_TEST",
        "timestamp": datetime.utcnow().isoformat()
    }
    table.put_item(Item=test_item)
    print("[OK] Test write to DynamoDB SUCCESSFUL!")
    
except NoCredentialsError:
    print("[ERROR] No AWS credentials configured")
except ClientError as e:
    error_code = e.response.get("Error", {}).get("Code", "Unknown")
    error_msg = e.response.get("Error", {}).get("Message", str(e))
    print(f"[ERROR] DynamoDB Error [{error_code}]: {error_msg}")
except EndpointConnectionError:
    print("[ERROR] Cannot reach AWS endpoint (check internet/region)")
except Exception as e:
    print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")

# Test 3: Test S3
print("\n[3] Testing S3 connection...")
try:
    s3 = boto3.client("s3", region_name=AWS_REGION)
    
    # Check if bucket exists
    s3.head_bucket(Bucket=BUCKET_NAME)
    print(f"[OK] S3 bucket '{BUCKET_NAME}' exists and is accessible")
    
    # Try a test upload
    import json
    test_data = {
        "log_id": str(uuid.uuid4()),
        "test": True,
        "timestamp": datetime.utcnow().isoformat()
    }
    test_key = f"test/diagnostic-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=test_key,
        Body=json.dumps(test_data).encode("utf-8"),
        ContentType="application/json"
    )
    print(f"[OK] Test upload to S3 SUCCESSFUL! (key: {test_key})")
    
except NoCredentialsError:
    print("[ERROR] No AWS credentials configured")
except ClientError as e:
    error_code = e.response.get("Error", {}).get("Code", "Unknown")
    error_msg = e.response.get("Error", {}).get("Message", str(e))
    print(f"[ERROR] S3 Error [{error_code}]: {error_msg}")
except EndpointConnectionError:
    print("[ERROR] Cannot reach AWS endpoint (check internet/region)")
except Exception as e:
    print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("Diagnostic complete. Check errors above.")
print("=" * 60)
