from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.app.core.paths import LOGS_PATH
from backend.app.utils.json_store import append_jsonl, read_jsonl


async def log_event(event_type: str, message: str, **details: Any) -> dict[str, Any]:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "message": message,
        "details": details,
    }
    await append_jsonl(LOGS_PATH, record)
    return record


def list_logs(query: str | None = None, event_type: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
    records = read_jsonl(LOGS_PATH, limit=limit)
    if event_type:
        records = [record for record in records if record.get("type") == event_type]
    if query:
        q = query.lower()
        records = [record for record in records if q in record.get("message", "").lower() or q in str(record.get("details", {})).lower()]
    return records
