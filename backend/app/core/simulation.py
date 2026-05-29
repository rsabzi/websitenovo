from __future__ import annotations

import asyncio
import math
import random
from dataclasses import asdict, dataclass
from typing import Any

from backend.app.agents.architect import ArchitectAgent
from backend.app.agents.base import BuildDecision
from backend.app.agents.planner import CityPlannerAgent
from backend.app.agents.resource import ResourceAgent
from backend.app.core.config import Config, load_config, save_config
from backend.app.core.meta import MetaOptimizer
from backend.app.core.scoring import score_cell


@dataclass
class Building:
    id: int
    x: int
    z: int
    building: str
    score: float
    agent: str
    reason: str
    tick: int


class Simulation:
    def __init__(self, config: Config | None = None, persist_config: bool = True):
        self.config = config or load_config()
        self.persist_config = persist_config
        self.planner = CityPlannerAgent()
        self.architect = ArchitectAgent()
        self.resource_agent = ResourceAgent(**self.config.initial_resources)
        self.meta = MetaOptimizer()
        self.tick_count = 0
        self.buildings: list[Building] = []
        self.logs: list[str] = []
        self.latest_meta: dict[str, Any] | None = None
        self._occupied: set[tuple[int, int]] = set()
        self._subscribers: set[asyncio.Queue] = set()
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        random.seed(42)

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=200)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self._subscribers.discard(queue)

    async def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self.run())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def run(self) -> None:
        while True:
            await self.tick()
            await asyncio.sleep(self.config.tick_interval_seconds)

    async def tick(self) -> BuildDecision | None:
        async with self._lock:
            if len(self.buildings) >= self.config.max_buildings:
                self.tick_count += 1
                return None
            candidates = self._candidate_cells(limit=80)
            if not candidates:
                return None
            cell, reason = self.planner.choose_cell(candidates, self.config.weights)
            building_type = self.architect.choose_building(cell["x"], cell["z"], cell["pollution"], cell["accessibility"])
            if not self.resource_agent.can_build(building_type):
                self._replenish_resources()
                return None
            score = score_cell(cell["accessibility"], cell["resources"], cell["pollution"], self.config.weights)
            self.resource_agent.consume(building_type)
            self.tick_count += 1
            building = Building(
                id=len(self.buildings) + 1,
                x=cell["x"],
                z=cell["z"],
                building=building_type,
                score=score,
                agent=self.planner.name,
                reason=reason,
                tick=self.tick_count,
            )
            self.buildings.append(building)
            self._occupied.add((building.x, building.z))
            decision = BuildDecision(building.x, building.z, building_type, self.planner.name, score, reason)
            event = {"type": "BUILD", **asdict(decision), "id": building.id, "tick": self.tick_count, "metrics": self.metrics()}
            self.logs.append(f"Tick {self.tick_count}: {building_type} at ({building.x},{building.z}) score={score}")
            self.logs = self.logs[-100:]
            if self.tick_count % self.config.meta_interval_ticks == 0:
                self.latest_meta = self.meta.analyze(self.config, self.metrics())
                self.config.weights = self.config.weights.model_validate(self.latest_meta["new_weights"])
                if self.persist_config:
                    save_config(self.config)
                event["meta"] = self.latest_meta
            await self._broadcast(event)
            return decision

    def _candidate_cells(self, limit: int) -> list[dict[str, float]]:
        cells = []
        size = self.config.grid_size
        attempts = 0
        while len(cells) < limit and attempts < limit * 10:
            attempts += 1
            x = random.randrange(size)
            z = random.randrange(size)
            if (x, z) in self._occupied:
                continue
            cells.append(self.cell_features(x, z))
        return cells

    def cell_features(self, x: int, z: int) -> dict[str, float]:
        center = (self.config.grid_size - 1) / 2
        distance_to_center = math.dist((x, z), (center, center))
        accessibility = max(0, 100 - distance_to_center * 5)
        if self.buildings:
            nearest = min(math.dist((x, z), (b.x, b.z)) for b in self.buildings)
            accessibility = min(100, accessibility + max(0, 35 - nearest * 6))
        resource_score = self.resource_agent.resource_score()
        industrial_neighbors = sum(1 for b in self.buildings if b.building == "industrial" and math.dist((x, z), (b.x, b.z)) < 5)
        pollution = min(100, 12 + industrial_neighbors * 18 + ((x * 13 + z * 7) % 18))
        return {"x": x, "z": z, "accessibility": accessibility, "resources": resource_score, "pollution": pollution}

    def grid(self) -> dict:
        return {
            "size": self.config.grid_size,
            "buildings": [asdict(b) for b in self.buildings],
            "heatmap": [self.cell_features(x, z) for x in range(self.config.grid_size) for z in range(self.config.grid_size)],
        }

    def agents(self) -> list[dict[str, str]]:
        return [
            {"name": self.planner.name, "role": "Scores cells and selects the best build location."},
            {"name": self.architect.name, "role": "Chooses residential, commercial, or industrial building type."},
            {"name": self.resource_agent.name, "role": "Tracks power, water, and road access constraints."},
        ]

    def metrics(self) -> dict[str, Any]:
        scores = [b.score for b in self.buildings]
        pollution_values = [self.cell_features(b.x, b.z)["pollution"] for b in self.buildings[-50:]] or [0]
        return {
            "tick": self.tick_count,
            "building_count": len(self.buildings),
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "average_pollution": round(sum(pollution_values) / len(pollution_values), 2),
            "resources": {"power": round(self.resource_agent.power, 2), "water": round(self.resource_agent.water, 2), "road_access": self.resource_agent.road_access},
            "weights": self.config.weights.normalized().model_dump(),
            "logs": self.logs[-30:],
            "meta": self.latest_meta,
        }

    def update_config(self, patch: dict) -> Config:
        data = self.config.model_dump()
        if "weights" in patch:
            data["weights"] = {**data["weights"], **patch["weights"]}
        for key in ["tick_interval_seconds", "meta_interval_ticks", "max_buildings"]:
            if key in patch:
                data[key] = patch[key]
        self.config = Config.model_validate(data)
        if self.persist_config:
            save_config(self.config)
        return self.config

    def _replenish_resources(self) -> None:
        self.resource_agent.power += 20
        self.resource_agent.water += 20

    async def _broadcast(self, event: dict) -> None:
        for queue in list(self._subscribers):
            if queue.full():
                _ = queue.get_nowait()
            queue.put_nowait(event)
