from __future__ import annotations

import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.app.core.paths import RULES_PATH
from backend.app.rules.models import Rule, RuleAction, RuleCondition
from backend.app.utils.json_store import read_json, write_json

DEFAULT_RULES = {
    "rules": [
        {"id": "archives", "name": "Archives", "condition": {"extension": ".zip"}, "action": {"type": "move", "move_to": "Archives"}},
        {"id": "pdf-documents", "name": "PDF Documents", "condition": {"extension": ".pdf"}, "action": {"type": "move", "move_to": "Documents"}},
        {"id": "python-code", "name": "Python Code", "condition": {"extension": ".py"}, "action": {"type": "move", "move_to": "Code"}},
    ]
}

CATEGORY_EXTENSIONS = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".heic"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".m4a"},
    "Code": {".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".java", ".cpp", ".c", ".html", ".css", ".json", ".yaml", ".yml"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".appimage"},
}


class RuleEngine:
    def __init__(self) -> None:
        self.rules = self.load_rules()

    def load_rules(self) -> list[Rule]:
        payload = read_json(RULES_PATH, DEFAULT_RULES)
        return [Rule.model_validate(rule) for rule in payload.get("rules", [])]

    def save_rules(self, rules: list[Rule] | None = None) -> list[Rule]:
        if rules is not None:
            self.rules = rules
        write_json(RULES_PATH, {"rules": [rule.model_dump() for rule in self.rules]})
        return self.rules

    def add_rule(self, name: str, condition: RuleCondition, action: RuleAction) -> Rule:
        rule = Rule(id=str(uuid4()), name=name, condition=condition, action=action)
        self.rules.append(rule)
        self.save_rules()
        return rule

    def delete_rule(self, rule_id: str) -> None:
        self.rules = [rule for rule in self.rules if rule.id != rule_id]
        self.save_rules()

    def match(self, path: Path) -> Rule | None:
        for rule in self.rules:
            if rule.enabled and self._matches(rule.condition, path):
                return rule
        return None

    def category_for(self, path: Path, large_threshold_mb: int = 100) -> str:
        try:
            if path.stat().st_size >= large_threshold_mb * 1024 * 1024:
                return "Large Files"
        except FileNotFoundError:
            return "Misc"
        matched = self.match(path)
        if matched and matched.action.type == "move" and matched.action.move_to:
            return matched.action.move_to
        suffix = path.suffix.lower()
        for category, extensions in CATEGORY_EXTENSIONS.items():
            if suffix in extensions:
                return category
        return "Misc"

    def _matches(self, condition: RuleCondition, path: Path) -> bool:
        try:
            stat = path.stat()
        except FileNotFoundError:
            return False
        if condition.extension and path.suffix.lower() != condition.extension.lower():
            return False
        if condition.min_size is not None and stat.st_size < condition.min_size:
            return False
        if condition.max_size is not None and stat.st_size > condition.max_size:
            return False
        if condition.filename_contains and condition.filename_contains.lower() not in path.name.lower():
            return False
        created = datetime.fromtimestamp(stat.st_ctime, timezone.utc)
        if condition.created_before and created >= condition.created_before:
            return False
        if condition.created_after and created <= condition.created_after:
            return False
        if condition.file_type:
            guessed, _ = mimetypes.guess_type(path)
            if not guessed or condition.file_type.lower() not in guessed.lower():
                return False
        return True
