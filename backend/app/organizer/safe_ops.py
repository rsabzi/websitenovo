from __future__ import annotations

import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.app.core.paths import HISTORY_PATH
from backend.app.logs.activity import log_event
from backend.app.utils.json_store import append_jsonl, read_jsonl


@dataclass
class FileTransaction:
    id: str
    operation: str
    source: str
    destination: str
    timestamp: str
    status: str = "completed"


def validate_safe_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if ".." in resolved.parts:
        raise ValueError("Unsafe path traversal detected")
    return resolved


def collision_safe_destination(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        return destination
    stem, suffix = destination.stem, destination.suffix
    counter = 1
    while True:
        candidate = destination.with_name(f"{stem} ({counter}){suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


class SafeFileOperator:
    async def move(self, source: Path, destination_dir: Path) -> FileTransaction:
        src = validate_safe_path(source)
        if not src.exists() or not src.is_file():
            raise FileNotFoundError(str(src))
        dest_dir = validate_safe_path(destination_dir)
        destination = collision_safe_destination(dest_dir / src.name)
        shutil.move(str(src), str(destination))
        transaction = FileTransaction(
            id=str(uuid4()),
            operation="move",
            source=str(src),
            destination=str(destination),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await append_jsonl(HISTORY_PATH, asdict(transaction))
        await log_event("FILE_MOVED", f"Moved {src.name}", source=str(src), destination=str(destination))
        return transaction

    async def rollback(self, transaction_id: str) -> FileTransaction:
        records = read_jsonl(HISTORY_PATH, limit=10000)
        match = next((record for record in reversed(records) if record.get("id") == transaction_id), None)
        if not match:
            raise KeyError(f"Transaction {transaction_id} not found")
        current = Path(match["destination"])
        original = collision_safe_destination(Path(match["source"]))
        if not current.exists():
            raise FileNotFoundError(str(current))
        shutil.move(str(current), str(original))
        rollback = FileTransaction(
            id=str(uuid4()),
            operation="rollback",
            source=str(current),
            destination=str(original),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await append_jsonl(HISTORY_PATH, asdict(rollback))
        await log_event("ROLLBACK", f"Rolled back {transaction_id}", source=str(current), destination=str(original))
        return rollback

    def history(self, limit: int = 500) -> list[dict]:
        return read_jsonl(HISTORY_PATH, limit=limit)
