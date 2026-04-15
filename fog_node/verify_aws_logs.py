"""
Verify that test logs are actually stored in AWS DynamoDB and S3.
"""

import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

AWS_REGION = "ap-south-1"
TABLE_NAME = "smart-locker-fog-audit"
BUCKET_NAME = "smart-locker-fog-audit-bucket"

print("=" * 70)
print("VERIFICATION: Checking AWS for Test Logs")
print("=" * 70)

# Initialize clients
try:
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(TABLE_NAME)
    s3 = boto3.client("s3", region_name=AWS_REGION)
except Exception as e:
    print(f"[ERROR] Failed to initialize AWS clients: {e}")
    exit(1)

# Check DynamoDB
print("\n[1] Checking DynamoDB table...")
try:
    # Scan for recent items (last 5 minutes)
    cutoff_time = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
    
    response = table.scan()
    items = response.get("Items", [])
    
    # Filter recent items
    recent_items = [
        item for item in items
        if item.get("timestamp", "") >= cutoff_time
    ]
    
    print(f"   Total items in table: {len(items)}")
    print(f"   Recent items (last 5 min): {len(recent_items)}")
    
    if recent_items:
        print("\n   Recent log entries:")
        for item in sorted(recent_items, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]:
            rfid = item.get("rfid", "N/A")
            user_id = item.get("user_id", "N/A")
            result = item.get("access_result", "N/A")
            reason = item.get("reason", "N/A")
            timestamp = item.get("timestamp", "N/A")[:19]  # Truncate to seconds
            print(f"     - {timestamp} | {result:7} | RFID: {rfid:15} | User: {user_id:6} | Reason: {reason}")
    else:
        print("   [WARNING] No recent items found in DynamoDB")
        
except ClientError as e:
    print(f"   [ERROR] DynamoDB error: {e}")
except Exception as e:
    print(f"   [ERROR] Unexpected error: {type(e).__name__}: {e}")

# Check S3
print("\n[2] Checking S3 bucket...")
try:
    # List objects from today
    today = datetime.utcnow().strftime("%Y-%m-%d")
    prefix = f"logs/{today}/"
    
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    
    if "Contents" in response:
        objects = response["Contents"]
        print(f"   Objects in 'logs/{today}/': {len(objects)}")
        
        # Show recent objects
        recent_objects = sorted(
            objects,
            key=lambda x: x["LastModified"],
            reverse=True
        )[:10]
        
        print("\n   Recent S3 objects:")
        for obj in recent_objects:
            key = obj["Key"]
            size = obj["Size"]
            modified = obj["LastModified"].strftime("%H:%M:%S")
            print(f"     - {modified} | {size:5} bytes | {key}")
            
        # Also check test folder
        test_prefix = "test/"
        test_response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=test_prefix)
        if "Contents" in test_response:
            test_objects = test_response["Contents"]
            print(f"\n   Test objects: {len(test_objects)}")
    else:
        print(f"   [WARNING] No objects found in 'logs/{today}/'")
        
        # Check if bucket has any objects at all
        all_objects = s3.list_objects_v2(Bucket=BUCKET_NAME, MaxKeys=10)
        if "Contents" in all_objects:
            print(f"   [INFO] Bucket has {len(all_objects['Contents'])} total objects")
        else:
            print("   [WARNING] Bucket appears to be empty")
            
except ClientError as e:
    print(f"   [ERROR] S3 error: {e}")
except Exception as e:
    print(f"   [ERROR] Unexpected error: {type(e).__name__}: {e}")

# Summary
print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\nIf you see recent items above, the logs are being saved correctly!")
print("If not, check:")
print("  1. AWS credentials are configured")
print("  2. Sync completed (run manual_sync.py if needed)")
print("  3. Check timestamps - logs might be older than 5 minutes")
