from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from backend.app.api.models import ResolveDuplicatesRequest, RollbackRequest, RuleCreate, SettingsPatch
from backend.app.core.app_state import AppState
from backend.app.logs.activity import list_logs


def create_router(state: AppState) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict:
        return {"ok": True, "watched_folders": list(state.watcher.watched)}

    @router.get("/settings")
    def get_settings() -> dict:
        return state.settings.model_dump()

    @router.post("/settings")
    def update_settings(patch: SettingsPatch) -> dict:
        settings = state.refresh_settings(patch.apply(state.settings))
        return {"ok": True, "settings": settings.model_dump()}

    @router.post("/folders")
    def add_folder(folder: str = Query(...)) -> dict:
        data = state.settings.model_dump()
        folders = set(data["monitored_folders"])
        folders.add(str(Path(folder).expanduser().resolve()))
        data["monitored_folders"] = sorted(folders)
        settings = state.refresh_settings(state.settings.model_validate(data))
        return {"ok": True, "settings": settings.model_dump()}

    @router.get("/events")
    def recent_events() -> list[dict]:
        return state.bus.recent

    @router.get("/rules")
    def list_rules() -> list[dict]:
        return [rule.model_dump() for rule in state.rules.rules]

    @router.post("/rules")
    def create_rule(payload: RuleCreate) -> dict:
        rule = state.rules.add_rule(payload.name, payload.condition, payload.action)
        return rule.model_dump()

    @router.delete("/rules/{rule_id}")
    def delete_rule(rule_id: str) -> dict:
        state.rules.delete_rule(rule_id)
        return {"ok": True}

    @router.post("/organize")
    async def organize(path: str) -> dict:
        try:
            event = await state.organizer.organize_file(Path(path))
            return {"ok": True, "event": event}
        except Exception as exc:  # API boundary converts operational errors to HTTP errors.
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/duplicates")
    async def get_duplicates() -> list[dict]:
        return state.duplicates_cache

    @router.post("/duplicates/scan")
    async def scan_duplicates() -> list[dict]:
        return await state.scan_duplicates()

    @router.post("/duplicates/resolve")
    async def resolve_duplicates(payload: ResolveDuplicatesRequest) -> dict:
        deleted = await state.duplicates.resolve([Path(path) for path in payload.files], payload.strategy)
        return {"ok": True, "deleted": deleted}

    @router.get("/history")
    def history() -> list[dict]:
        return state.operator.history()

    @router.post("/rollback")
    async def rollback(payload: RollbackRequest) -> dict:
        try:
            transaction = await state.operator.rollback(payload.transaction_id)
            await state.bus.publish({"type": "ROLLBACK", "transaction_id": payload.transaction_id, "destination": transaction.destination})
            return {"ok": True, "transaction": transaction.__dict__}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/logs")
    def logs(query: str | None = None, event_type: str | None = None) -> list[dict]:
        return list_logs(query=query, event_type=event_type)

    return router
