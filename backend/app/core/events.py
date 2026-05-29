from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue] = set()
        self.recent: list[dict[str, Any]] = []

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=500)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self._subscribers.discard(queue)

    async def publish(self, event: dict[str, Any]) -> dict[str, Any]:
        payload = {"timestamp": datetime.now(timezone.utc).isoformat(), **event}
        self.recent.append(payload)
        self.recent = self.recent[-300:]
        for queue in list(self._subscribers):
            if queue.full():
                _ = queue.get_nowait()
            queue.put_nowait(payload)
        return payload
