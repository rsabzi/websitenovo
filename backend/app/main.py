from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.core.simulation import Simulation

simulation = Simulation()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await simulation.start()
    yield
    await simulation.stop()


app = FastAPI(title="Neural City Architect API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConfigPatch(BaseModel):
    weights: dict[str, float] | None = None
    tick_interval_seconds: float | None = None
    meta_interval_ticks: int | None = None
    max_buildings: int | None = None


@app.get("/grid")
def get_grid() -> dict:
    return simulation.grid()


@app.get("/agents")
def get_agents() -> list[dict[str, str]]:
    return simulation.agents()


@app.get("/metrics")
def get_metrics() -> dict[str, Any]:
    return simulation.metrics()


@app.post("/config/update")
def update_config(patch: ConfigPatch) -> dict:
    data = patch.model_dump(exclude_none=True)
    config = simulation.update_config(data)
    return {"ok": True, "config": config.model_dump()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    queue = simulation.subscribe()
    try:
        await websocket.send_json({"type": "SNAPSHOT", "grid": simulation.grid(), "metrics": simulation.metrics()})
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        simulation.unsubscribe(queue)
