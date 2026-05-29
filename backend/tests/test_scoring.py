from backend.app.core.config import Weights
from backend.app.core.scoring import score_cell


def test_score_formula_uses_weights():
    score = score_cell(accessibility=80, resources=60, pollution=20, weights=Weights(accessibility=0.5, resources=0.3, pollution=0.2))
    assert score == 54


def test_score_is_clamped():
    assert score_cell(1000, 1000, -100, Weights(accessibility=0.5, resources=0.3, pollution=0.2)) == 80
