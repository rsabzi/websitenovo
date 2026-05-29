# AI File Organizer

A production-oriented desktop application that monitors folders in real time, organizes files automatically, detects duplicates, applies configurable rules, records safe operation history, and provides rollback from a polished Electron + React dashboard.

## Features

- Real-time multi-folder monitoring with Python `watchdog`.
- FastAPI REST API and WebSocket live event stream.
- Smart categorization into Images, Videos, Documents, Archives, Audio, Code, Installers, Large Files, and Misc.
- JSON-backed custom rule engine with extension, size, filename, date, and MIME/file-type conditions.
- SHA256 duplicate detection with keep-newest / keep-largest / delete resolution strategies.
- Transaction-like safe moves with collision-safe renaming and rollback history.
- Activity logs for moves, rule triggers, duplicate alerts, rollback events, and errors.
- Electron desktop app with React, TailwindCSS, Zustand, and Framer Motion.
- Local-first optional AI direction: natural-language rule generation can be added without cloud APIs by extending the rule engine.

## Architecture

```text
ai-file-organizer/
├── backend/
│   ├── app/
│   │   ├── api/          REST models and routes
│   │   ├── core/         settings, paths, app state, event bus
│   │   ├── watcher/      watchdog integration
│   │   ├── organizer/    categorization orchestration and safe operations
│   │   ├── duplicates/   SHA256 duplicate scanner/resolver
│   │   ├── rules/        configurable JSON rule engine
│   │   ├── logs/         activity logging
│   │   └── utils/        JSON/JSONL persistence helpers
│   ├── tests/
│   ├── config/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── store/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── animations/
│   │   └── styles/
│   ├── electron/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Development setup

### Backend

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765
```

### Frontend desktop app

```bash
cd frontend
npm install
npm run dev
```

The Electron main process also attempts to start the Python backend on port `8765`. During backend development, you can run the backend manually and use `npm run dev:ui` for UI-only work.

## Production build

### Windows executable

```bash
cd frontend
npm install
npm run package:win
```

The Windows installer is emitted to `frontend/release/` using Electron Builder NSIS config.

## API documentation

Start the backend and open:

- Swagger UI: <http://127.0.0.1:8765/docs>
- OpenAPI JSON: <http://127.0.0.1:8765/openapi.json>

Key endpoints:

- `GET /api/health`
- `GET /api/settings`
- `POST /api/settings`
- `POST /api/folders?folder=/path/to/folder`
- `GET /api/rules`
- `POST /api/rules`
- `GET /api/duplicates`
- `POST /api/duplicates/resolve`
- `GET /api/history`
- `POST /api/rollback`
- `GET /api/logs`
- `WS /ws`

Example WebSocket payload:

```json
{
  "type": "FILE_MOVED",
  "filename": "report.pdf",
  "from": "Downloads",
  "to": "Documents",
  "timestamp": "2026-05-29T10:00:00Z"
}
```

## Testing

Backend:

```bash
pytest backend
```

Frontend:

```bash
cd frontend
npm test
```

Coverage areas include rule engine behavior, duplicate detection, rollback support, API endpoints, WebSocket snapshots, Zustand state, and React component rendering.

## Troubleshooting

- **Backend does not start in Electron:** install backend dependencies first with `pip install -r backend/requirements.txt`, or set `PYTHON=/path/to/python` before launching Electron.
- **No file events:** confirm the monitored folder exists and that OS permissions allow file-system notifications.
- **Files are renamed during moves:** this is expected collision protection to prevent overwrites.
- **Duplicate delete actions:** use duplicate resolution intentionally; destructive operations should be exposed only behind UI confirmation.
- **Large folders:** scanning 100k+ files is batched through filesystem iteration and async hashing dispatch; avoid scanning network drives without first testing performance.

## Security model

- Path inputs are resolved and validated before file operations.
- Move collisions are auto-renamed; existing files are not overwritten.
- Rollback history is stored as JSONL transaction records.
- Dangerous duplicate deletion is available only through explicit API/UI actions.
- No cloud API is required by default.
