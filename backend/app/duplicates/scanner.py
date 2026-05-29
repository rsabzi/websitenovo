from __future__ import annotations

import asyncio
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Literal

from backend.app.logs.activity import log_event
from backend.app.utils.protection import is_protected

CHUNK_SIZE = 1024 * 1024


async def sha256_file(path: Path) -> str:
    def _hash() -> str:
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
                digest.update(chunk)
        return digest.hexdigest()

    return await asyncio.to_thread(_hash)


class DuplicateScanner:
    async def scan(self, folders: list[Path]) -> list[dict]:
        groups: dict[tuple[int, str], list[Path]] = defaultdict(list)
        for folder in folders:
            if not folder.exists():
                continue
            for path in folder.rglob("*"):
                if path.is_file():
                    # Skip protected project files
                    if is_protected(path):
                        continue
                    try:
                        groups[(path.stat().st_size, path.suffix.lower())].append(path)
                    except OSError:
                        continue

        duplicates = []
        for candidates in groups.values():
            if len(candidates) < 2:
                continue
            hash_groups: dict[str, list[Path]] = defaultdict(list)
            for path in candidates:
                try:
                    hash_groups[await sha256_file(path)].append(path)
                except OSError:
                    continue
            for digest, paths in hash_groups.items():
                if len(paths) > 1:
                    files = [self._file_info(path) for path in paths]
                    duplicates.append({"hash": digest, "count": len(paths), "files": files})
                    await log_event("DUPLICATE_DETECTED", f"Detected {len(paths)} duplicate files", hash=digest, files=files)
        return duplicates

    async def resolve(self, files: list[Path], strategy: Literal["delete", "keep_newest", "keep_largest"]) -> list[str]:
        if strategy == "delete":
            targets = files
        elif strategy == "keep_newest":
            keep = max(files, key=lambda path: path.stat().st_mtime)
            targets = [path for path in files if path != keep]
        else:
            keep = max(files, key=lambda path: path.stat().st_size)
            targets = [path for path in files if path != keep]
        deleted = []
        for target in targets:
            if target.exists() and target.is_file():
                target.unlink()
                deleted.append(str(target))
        if deleted:
            await log_event("DUPLICATE_RESOLVED", f"Resolved duplicates using {strategy}", deleted=deleted)
        return deleted

    def _file_info(self, path: Path) -> dict:
        stat = path.stat()
        return {
            "path": str(path),
            "name": path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
        }
