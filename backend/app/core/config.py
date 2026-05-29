from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT / "config.json"


class Weights(BaseModel):
    accessibility: float = Field(ge=0, le=1)
    resources: float = Field(ge=0, le=1)
    pollution: float = Field(ge=0, le=1)

    @field_validator("pollution")
    @classmethod
    def _validate_sum(cls, value: float, info: Any) -> float:
        data = info.data
        total = data.get("accessibility", 0) + data.get("resources", 0) + value
        if total <= 0:
            raise ValueError("weight total must be positive")
        return value

    def normalized(self) -> "Weights":
        total = self.accessibility + self.resources + self.pollution
        return Weights(
            accessibility=round(self.accessibility / total, 4),
            resources=round(self.resources / total, 4),
            pollution=round(self.pollution / total, 4),
        )


class Config(BaseModel):
    grid_size: int = Field(default=32, ge=8, le=128)
    tick_interval_seconds: float = Field(default=0.35, ge=0.05, le=5)
    meta_interval_ticks: int = Field(default=25, ge=5, le=500)
    max_buildings: int = Field(default=900, ge=1, le=5000)
    weights: Weights
    initial_resources: dict[str, float]


def load_config(path: Path = CONFIG_PATH) -> Config:
    return Config.model_validate(json.loads(path.read_text()))


def save_config(config: Config, path: Path = CONFIG_PATH) -> None:
    path.write_text(json.dumps(config.model_dump(), indent=2) + "\n")
