from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import aiofiles


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(default, indent=2))
        return default
    return json.loads(path.read_text() or json.dumps(default))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str) + "\n")


async def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(path, "a") as file:
        await file.write(json.dumps(record, default=str) + "\n")


def read_jsonl(path: Path, limit: int = 500) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text().splitlines()[-limit:]
    return [json.loads(line) for line in lines if line.strip()]
