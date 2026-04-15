"""
Manual sync script to upload all unsynced logs to AWS.
Run this to backfill existing logs.
"""

from storage.sync import _sync_worker
from utils.logger import log_info

if __name__ == "__main__":
    print("=" * 60)
    print("Manual Cloud Sync - Uploading all unsynced logs")
    print("=" * 60)
    log_info("Starting manual sync...")
    _sync_worker()
    print("=" * 60)
    print("Manual sync complete. Check logs above for results.")
    print("=" * 60)
