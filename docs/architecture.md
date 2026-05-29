# Architecture

## Backend

The backend is a FastAPI app with an application lifespan-managed `Simulation`. The simulation owns static agent instances, bounded config, grid state, metrics, and WebSocket subscribers.

### Agents

- `CityPlannerAgent`: receives candidate cells, applies the configured scoring function, and chooses the highest scoring location.
- `ArchitectAgent`: maps local conditions to one of three fixed building types.
- `ResourceAgent`: tracks power, water, road access, checks build feasibility, and consumes resources.

No agent is created dynamically at runtime.

### Scoring

The fixed formula is:

```text
Score = (accessibility_weight × Accessibility)
      + (resources_weight × Resources)
      - (pollution_weight × Pollution)
```

Weights are read from `config.json`, normalized before use, and can be updated through `POST /config/update`.

### MetaOptimizer safety boundary

`MetaOptimizer` runs every `meta_interval_ticks`. It can only:

1. Analyze metrics.
2. Suggest future static agent types as text.
3. Apply new numeric scoring weights to `config.json`.

It cannot execute generated code, write Python/TypeScript modules, import user-provided logic, or instantiate new agent classes.

## Frontend

The frontend is a Next.js app using Three.js through React Three Fiber and Drei.

- WebSocket events append buildings without a full scene refresh.
- Buildings are rendered with `InstancedMesh` so 500+ buildings remain practical.
- A transparent heatmap overlays the grid: green means favorable, red means risky.
- Clicking an instance opens its score, agent, and build reason in the side panel.

## Runtime flow

1. Simulation tick samples open cells.
2. Planner ranks cells by score.
3. Architect chooses building type.
4. Resource agent validates/consumes resources.
5. Simulation records the building and metrics.
6. WebSocket broadcasts the build event.
7. Frontend appends the building to the instanced city scene.
