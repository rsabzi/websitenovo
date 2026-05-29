from __future__ import annotations

from backend.app.core.config import Config, Weights


class MetaOptimizer:
    """Safe optimizer: proposes and applies only config weight changes, never code changes."""

    def analyze(self, config: Config, metrics: dict) -> dict:
        weights = config.weights.normalized()
        avg_score = metrics.get("average_score", 0)
        pollution = metrics.get("average_pollution", 0)
        if pollution > 55:
            suggestion = "Reduce pollution impact by selecting cleaner, resource-aware sites."
            new_weights = Weights(accessibility=weights.accessibility, resources=min(0.45, weights.resources + 0.05), pollution=min(0.45, weights.pollution + 0.05)).normalized()
        elif avg_score < 45:
            suggestion = "Increase accessibility weight to improve clustering around successful districts."
            new_weights = Weights(accessibility=min(0.7, weights.accessibility + 0.1), resources=max(0.15, weights.resources - 0.05), pollution=weights.pollution).normalized()
        else:
            suggestion = "Current growth is stable; keep weights near their present balance."
            new_weights = weights
        return {
            "suggestion": suggestion,
            "new_weights": new_weights.model_dump(),
            "suggested_agent_types": ["TransitAgent", "ZoningAgent"] if avg_score < 50 else [],
        }
