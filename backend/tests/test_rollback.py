from pathlib import Path

import pytest

from backend.app.organizer.safe_ops import SafeFileOperator


@pytest.mark.asyncio
async def test_safe_move_and_rollback(tmp_path: Path):
    source_dir = tmp_path / "inbox"
    target_dir = tmp_path / "organized"
    source_dir.mkdir()
    file = source_dir / "report.pdf"
    file.write_text("report")
    operator = SafeFileOperator()
    tx = await operator.move(file, target_dir)
    assert Path(tx.destination).exists()
    rollback = await operator.rollback(tx.id)
    assert Path(rollback.destination).exists()
