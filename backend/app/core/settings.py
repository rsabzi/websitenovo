from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from backend.app.core.paths import SETTINGS_PATH
from backend.app.utils.json_store import read_json, write_json


class Settings(BaseModel):
    monitored_folders: list[str] = Field(default_factory=list)
    auto_organize: bool = True
    duplicate_scan_frequency_minutes: int = Field(default=60, ge=1, le=10080)
    theme: Literal["dark", "light"] = "dark"
    notifications_enabled: bool = True
    organize_root: str | None = None
    max_file_size_large_mb: int = Field(default=100, ge=1)

    @field_validator("monitored_folders")
    @classmethod
    def normalize_folders(cls, folders: list[str]) -> list[str]:
        return [str(Path(folder).expanduser().resolve()) for folder in folders]


def load_settings() -> Settings:
    return Settings.model_validate(read_json(SETTINGS_PATH, Settings().model_dump()))


def save_settings(settings: Settings) -> Settings:
    write_json(SETTINGS_PATH, settings.model_dump())
    return settings
