from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = ROOT / "backend" / "config"
DATA_DIR = CONFIG_DIR / "data"
SETTINGS_PATH = CONFIG_DIR / "settings.json"
RULES_PATH = CONFIG_DIR / "rules.json"
HISTORY_PATH = DATA_DIR / "history.jsonl"
LOGS_PATH = DATA_DIR / "activity.jsonl"
DUPLICATES_PATH = DATA_DIR / "duplicates.json"
TAGS_PATH = DATA_DIR / "tags.json"

for directory in (CONFIG_DIR, DATA_DIR):
    directory.mkdir(parents=True, exist_ok=True)
