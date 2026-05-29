from __future__ import annotations

from dataclasses import dataclass

from backend.app.agents.base import BuildingType


@dataclass
class ResourceAgent:
    power: float
    water: float
    road_access: float

    name: str = "ResourceAgent"

    def resource_score(self) -> float:
        power_score = min(100, self.power / 10)
        water_score = min(100, self.water / 10)
        road_score = self.road_access * 100
        return round((power_score + water_score + road_score) / 3, 2)

    def can_build(self, building: BuildingType) -> bool:
        costs = self.cost_for(building)
        return self.power >= costs["power"] and self.water >= costs["water"]

    def consume(self, building: BuildingType) -> None:
        costs = self.cost_for(building)
        self.power = max(0, self.power - costs["power"])
        self.water = max(0, self.water - costs["water"])

    @staticmethod
    def cost_for(building: BuildingType) -> dict[str, float]:
        return {
            "residential": {"power": 4, "water": 6},
            "commercial": {"power": 7, "water": 5},
            "industrial": {"power": 11, "water": 8},
        }[building]
