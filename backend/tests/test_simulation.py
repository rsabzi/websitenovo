import pytest

from backend.app.core.config import Config, Weights
from backend.app.core.simulation import Simulation


@pytest.mark.asyncio
async def test_simulation_tick_stability():
    config = Config(
        grid_size=16,
        tick_interval_seconds=0.05,
        meta_interval_ticks=10,
        max_buildings=100,
        weights=Weights(accessibility=0.5, resources=0.3, pollution=0.2),
        initial_resources={"power": 1000, "water": 1000, "road_access": 1.0},
    )
    sim = Simulation(config=config, persist_config=False)
    for _ in range(30):
        await sim.tick()
    metrics = sim.metrics()
    assert metrics["tick"] == 30
    assert metrics["building_count"] > 0
    assert metrics["building_count"] <= 30
