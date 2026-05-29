from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from backend.app.core.settings import Settings
from backend.app.rules.models import RuleAction, RuleCondition


class SettingsPatch(BaseModel):
    monitored_folders: list[str] | None = None
    auto_organize: bool | None = None
    duplicate_scan_frequency_minutes: int | None = None
    theme: Literal["dark", "light"] | None = None
    notifications_enabled: bool | None = None
    organize_root: str | None = None
    max_file_size_large_mb: int | None = None

    def apply(self, settings: Settings) -> Settings:
        data = settings.model_dump()
        data.update(self.model_dump(exclude_none=True))
        return Settings.model_validate(data)


class RuleCreate(BaseModel):
    name: str
    condition: RuleCondition
    action: RuleAction


class ResolveDuplicatesRequest(BaseModel):
    files: list[str]
    strategy: Literal["delete", "keep_newest", "keep_largest"]


class RollbackRequest(BaseModel):
    transaction_id: str
