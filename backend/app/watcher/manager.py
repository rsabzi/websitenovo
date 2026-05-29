from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from backend.app.core.events import EventBus
from backend.app.organizer.service import OrganizerService


class AsyncWatchdogHandler(FileSystemEventHandler):
    def __init__(self, loop: asyncio.AbstractEventLoop, callback: Callable[[FileSystemEvent], None]) -> None:
        self.loop = loop
        self.callback = callback

    def on_created(self, event: FileSystemEvent) -> None:
        self.loop.call_soon_threadsafe(self.callback, event)

    def on_modified(self, event: FileSystemEvent) -> None:
        self.loop.call_soon_threadsafe(self.callback, event)

    def on_moved(self, event: FileSystemEvent) -> None:
        self.loop.call_soon_threadsafe(self.callback, event)


class WatcherManager:
    def __init__(self, bus: EventBus, organizer: OrganizerService) -> None:
        self.bus = bus
        self.organizer = organizer
        self.observer = Observer()
        self.watched: set[str] = set()
        self.loop: asyncio.AbstractEventLoop | None = None

    def start(self, folders: list[str]) -> None:
        self.loop = asyncio.get_running_loop()
        for folder in folders:
            self.add_folder(folder)
        if not self.observer.is_alive():
            self.observer.start()

    def stop(self) -> None:
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=5)

    def add_folder(self, folder: str) -> None:
        path = Path(folder).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        key = str(path)
        if key in self.watched:
            return
        handler = AsyncWatchdogHandler(self.loop or asyncio.get_event_loop(), self._handle_event)
        self.observer.schedule(handler, key, recursive=False)
        self.watched.add(key)

    def _handle_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        asyncio.create_task(self._process(event))

    async def _process(self, event: FileSystemEvent) -> None:
        event_type = event.event_type.upper()
        path = Path(getattr(event, "dest_path", None) or event.src_path)
        await self.bus.publish({"type": f"FILE_{event_type}", "path": str(path), "filename": path.name, "operation": event_type})
        if event.event_type in {"created", "moved"}:
            await asyncio.sleep(0.25)
            await self.organizer.organize_file(path)
