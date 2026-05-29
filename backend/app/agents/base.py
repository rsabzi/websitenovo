from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BuildingType = Literal["residential", "commercial", "industrial"]


@dataclass(frozen=True)
class BuildDecision:
    x: int
    z: int
    building: BuildingType
    agent: str
    score: float
    reason: str
