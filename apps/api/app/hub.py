from __future__ import annotations

import asyncio
import json
from collections import defaultdict


class Hub:
    def __init__(self) -> None:
        self._subs: dict[str, list[asyncio.Queue]] = defaultdict(list)

    def subscribe(self, event_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=200)
        self._subs[event_id].append(queue)
        return queue

    def unsubscribe(self, event_id: str, queue: asyncio.Queue) -> None:
        listeners = self._subs.get(event_id, [])
        if queue in listeners:
            listeners.remove(queue)

    async def publish(self, event_id: str, payload: dict) -> None:
        body = json.dumps(payload, default=str)
        for queue in list(self._subs.get(event_id, [])):
            try:
                queue.put_nowait(body)
            except asyncio.QueueFull:
                pass


hub = Hub()
