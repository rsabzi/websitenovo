from pathlib import Path

from backend.app.rules.engine import RuleEngine
from backend.app.rules.models import Rule, RuleAction, RuleCondition


def test_rule_engine_matches_extension(tmp_path: Path):
    file = tmp_path / "archive.zip"
    file.write_text("data")
    engine = RuleEngine()
    engine.rules = [Rule(id="r1", name="Zip", condition=RuleCondition(extension=".zip"), action=RuleAction(type="move", move_to="Archives"))]
    assert engine.match(file).name == "Zip"
    assert engine.category_for(file) == "Archives"


def test_default_category_code(tmp_path: Path):
    file = tmp_path / "script.py"
    file.write_text("print('hi')")
    engine = RuleEngine()
    engine.rules = []
    assert engine.category_for(file) == "Code"
