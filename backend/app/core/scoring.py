from __future__ import annotations

from backend.app.core.config import Weights


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def score_cell(accessibility: float, resources: float, pollution: float, weights: Weights) -> float:
    """Score a cell on a 0-100 scale using configurable bounded weights."""
    normalized = weights.normalized()
    score = (
        normalized.accessibility * clamp(accessibility)
        + normalized.resources * clamp(resources)
        - normalized.pollution * clamp(pollution)
    )
    return round(clamp(score), 2)
