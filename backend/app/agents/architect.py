from __future__ import annotations

from backend.app.agents.base import BuildingType


class ArchitectAgent:
    name = "ArchitectAgent"

    def choose_building(self, x: int, z: int, pollution: float, accessibility: float) -> BuildingType:
        if pollution < 35 and accessibility > 65:
            return "commercial"
        if pollution > 55 or (x + z) % 7 == 0:
            return "industrial"
        return "residential"
