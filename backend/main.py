from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import create_router
from backend.app.core.app_state import AppState

state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.watcher.start(state.settings.monitored_folders)
    yield
    state.watcher.stop()


app = FastAPI(title="AI File Organizer API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(create_router(state), prefix="/api")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    queue = state.bus.subscribe()
    try:
        await websocket.send_json({"type": "SNAPSHOT", "events": state.bus.recent, "settings": state.settings.model_dump()})
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        state.bus.unsubscribe(queue)
