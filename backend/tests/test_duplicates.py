from pathlib import Path

import pytest

from backend.app.duplicates.scanner import DuplicateScanner


@pytest.mark.asyncio
async def test_duplicate_scanner_detects_exact_matches(tmp_path: Path):
    (tmp_path / "a.txt").write_text("same")
    (tmp_path / "b.txt").write_text("same")
    (tmp_path / "c.txt").write_text("different")
    duplicates = await DuplicateScanner().scan([tmp_path])
    assert len(duplicates) == 1
    assert duplicates[0]["count"] == 2
