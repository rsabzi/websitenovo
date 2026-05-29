from __future__ import annotations

from backend.app.core.config import Weights
from backend.app.core.scoring import score_cell


class CityPlannerAgent:
    name = "CityPlannerAgent"

    def choose_cell(self, cells: list[dict], weights: Weights) -> tuple[dict, str]:
        ranked = sorted(
            cells,
            key=lambda c: score_cell(c["accessibility"], c["resources"], c["pollution"], weights),
            reverse=True,
        )
        chosen = ranked[0]
        reason = (
            f"Highest weighted score from accessibility={chosen['accessibility']:.1f}, "
            f"resources={chosen['resources']:.1f}, pollution={chosen['pollution']:.1f}."
        )
        return chosen, reason
