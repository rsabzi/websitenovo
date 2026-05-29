from __future__ import annotations

from pathlib import Path

from backend.app.core.events import EventBus
from backend.app.core.paths import DUPLICATES_PATH
from backend.app.core.settings import Settings, load_settings, save_settings
from backend.app.duplicates.scanner import DuplicateScanner
from backend.app.organizer.safe_ops import SafeFileOperator
from backend.app.organizer.service import OrganizerService
from backend.app.rules.engine import RuleEngine
from backend.app.watcher.manager import WatcherManager
from backend.app.utils.json_store import read_json, write_json


class AppState:
    def __init__(self) -> None:
        self.settings: Settings = load_settings()
        self.bus = EventBus()
        self.rules = RuleEngine()
        self.organizer = OrganizerService(self.settings, self.bus, self.rules)
        self.watcher = WatcherManager(self.bus, self.organizer)
        self.duplicates = DuplicateScanner()
        self.operator = SafeFileOperator()
        self.duplicates_cache: list[dict] = read_json(DUPLICATES_PATH, [])

    def refresh_settings(self, settings: Settings) -> Settings:
        self.settings = save_settings(settings)
        self.organizer.settings = self.settings
        for folder in self.settings.monitored_folders:
            self.watcher.add_folder(folder)
        return self.settings

    async def scan_duplicates(self) -> list[dict]:
        folders = [Path(folder) for folder in self.settings.monitored_folders]
        duplicates = await self.duplicates.scan(folders)
        self.duplicates_cache = duplicates
        write_json(DUPLICATES_PATH, duplicates)
        for duplicate in duplicates:
            await self.bus.publish({"type": "DUPLICATE_ALERT", **duplicate})
        return duplicates
