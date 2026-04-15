# fog_node/storage/sync.py

import threading

from cloud.dynamodb_client import push_access_log
from storage.local_store import fetch_unsynced_logs, mark_as_synced
from utils.logger import log_info, log_warning


def _sync_worker():
    """Background worker to sync logs to AWS. Catches all exceptions to prevent crashes."""
    try:
        logs = fetch_unsynced_logs()

        if not logs:
            log_info("No unsynced logs to upload.")
            return

        log_info(f"Found {len(logs)} unsynced log(s) to upload.")

        for log in logs:
            local_id = log.get("local_id")
            log_info(f"Starting cloud sync for local_id={local_id}...")

            try:
                success = push_access_log(log)

                if success:
                    mark_as_synced(local_id)
                    log_info(f"Cloud sync successful for local_id={local_id}.")
                else:
                    # Do not block other logs or fog access; leave as unsynced for retry.
                    log_warning(
                        f"Cloud sync failed for local_id={local_id}; "
                        f"will retry on next sync trigger."
                    )
            except Exception as exc:
                # Catch any unexpected exceptions in push_access_log
                from utils.logger import log_error
                log_error(
                    f"Exception during sync for local_id={local_id}: "
                    f"{type(exc).__name__}: {exc}"
                )
    except Exception as exc:
        # Catch exceptions in fetch_unsynced_logs or mark_as_synced
        from utils.logger import log_error
        log_error(f"Fatal error in sync worker: {type(exc).__name__}: {exc}")


def trigger_sync():
    """
    Trigger background synchronization of any unsynced logs.

    This is non-blocking with respect to the fog access flow.
    """
    thread = threading.Thread(target=_sync_worker, daemon=True)
    thread.start()