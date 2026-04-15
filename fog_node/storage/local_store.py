# fog_node/storage/local_store.py

import json
import uuid

from utils.timezone import now_ist_iso

LOCAL_LOG_FILE = "fog_logs.jsonl"


def store_log(log: dict):
    log_entry = {
        "local_id": str(uuid.uuid4()),
        "synced": False,
        "timestamp": now_ist_iso(),
        **log
    }

    with open(LOCAL_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def fetch_unsynced_logs():
    logs = []
    try:
        with open(LOCAL_LOG_FILE, "r") as f:
            for line in f:
                record = json.loads(line)
                if not record.get("synced"):
                    logs.append(record)
    except FileNotFoundError:
        pass
    return logs


def mark_as_synced(local_id: str):
    records = []
    with open(LOCAL_LOG_FILE, "r") as f:
        for line in f:
            record = json.loads(line)
            if record["local_id"] == local_id:
                record["synced"] = True
            records.append(record)

    with open(LOCAL_LOG_FILE, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")