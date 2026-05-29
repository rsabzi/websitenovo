from __future__ import annotations

from pathlib import Path

from backend.app.core.events import EventBus
from backend.app.core.settings import Settings
from backend.app.logs.activity import log_event
from backend.app.organizer.safe_ops import SafeFileOperator
from backend.app.rules.engine import RuleEngine
from backend.app.utils.protection import is_protected


class OrganizerService:
    def __init__(self, settings: Settings, bus: EventBus, rules: RuleEngine | None = None) -> None:
        self.settings = settings
        self.bus = bus
        self.rules = rules or RuleEngine()
        self.operator = SafeFileOperator()

    async def organize_file(self, path: Path) -> dict | None:
        if not self.settings.auto_organize or not path.exists() or not path.is_file():
            return None
            
        # Skip protected project files
        if is_protected(path):
            return None
            
        category = self.rules.category_for(path, self.settings.max_file_size_large_mb)
        if category == "Misc" and path.name.startswith("."):
            return None
        root = Path(self.settings.organize_root).expanduser().resolve() if self.settings.organize_root else path.parent
        rule = self.rules.match(path)
        if rule and rule.action.type == "ignore":
            await log_event("RULE_IGNORED", f"Ignored {path.name} by rule {rule.name}", rule_id=rule.id)
            await self.bus.publish({"type": "RULE_IGNORED", "filename": path.name, "path": str(path), "rule": rule.name})
            return None
        transaction = await self.operator.move(path, root / category)
        event = {
            "type": "FILE_MOVED",
            "filename": path.name,
            "from": str(path.parent),
            "to": transaction.destination,
            "category": category,
            "transaction_id": transaction.id,
            "rule": rule.name if rule else "default-category-map",
        }
        await self.bus.publish(event)
        if rule:
            await log_event("RULE_TRIGGERED", f"Rule {rule.name} moved {path.name}", rule_id=rule.id, action=rule.action.model_dump())
            await self.bus.publish({"type": "RULE_TRIGGERED", "filename": path.name, "rule": rule.name})
        return event
