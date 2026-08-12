---
name: backend-conventions
description: Python/FastAPI coding conventions for the O-Suivi backend. Invoke before writing or reviewing backend code.
---

# Backend Conventions (Python / FastAPI)

## Architecture patterns

- **Class-based domain logic**: prefer classes over loose functions for domain logic. One class per file, one responsibility per file.
- **Service layer separation**: business logic lives in service classes, never in routers. Routers only handle HTTP concerns (parsing requests, returning responses).
- **Repository pattern**: data access is encapsulated in repository classes (`repositories/`). Repositories handle JSON file I/O and return typed objects.
- **Dependency Injection via FastAPI `Depends`**: auth dependency lives in `dependencies.py`. Routers receive dependencies through `Depends()`.

## Module structure

The backend code lives under `backend/src/app/` with a flat layered structure:

| Directory | Role |
|-----------|------|
| `routers/` | HTTP endpoints (thin — delegate to services) |
| `services/` | Business logic orchestration |
| `domain/` | Pure domain logic, state reconstruction, calculations |
| `repositories/` | Data access (JSON file I/O, CRUD) |
| `schemas/` | Pydantic models (request/response, domain types) |
| `websocket/` | WebSocket connection management |
| `main.py` | FastAPI app entrypoint |
| `config.py` | Settings (JWT, paths) |
| `dependencies.py` | Auth dependency (`get_current_user`) |

## Data models

- **Pydantic models only** — never raw `dict`, never `dataclasses`.
- Use proper field validation where applicable.
- Schemas are grouped by domain in `schemas/` (e.g., `events.py`, `logs.py`, `results.py`).

## Storage

- **JSON files** — no relational database. Data lives in `backend/data/`.
- `users.json` for user storage.
- One JSON file per template in `templates/`.
- One folder per event in `events/` (containing `event.json` + `logs/`).
- Event sourcing for logs: append-only log entries, state reconstructed from logs.

## Type safety

- Complete type annotations on all functions (parameters + return types).
- No `Any` types.
- No untyped `dict` — use Pydantic models or `TypedDict`.
- No missing return type annotations.

## Naming

- Comprehensive, explicit variable and function names.
- No clever shortcuts or abbreviations.
- A new developer should understand the code without comments.
- Files: `snake_case`.
- Classes: `PascalCase`.

## Code style

- Reuse existing patterns before introducing new abstractions.
- Write minimal, focused code — no features beyond what the task requires.
- No broad refactors unless required by the task.
- No dead code, no commented-out code.
- If a file grows beyond ~150 lines, consider splitting.

## Testing

- Framework: **pytest** with **pytest-asyncio** and **httpx**
- Run: `cd backend && uv run --group dev pytest tests`
- Use the shared `client` fixture from `tests/conftest.py` — never recreate it.
- Tests must be independent, fast, and deterministic.
- Unit tests for all new domain logic.
- Integration tests for critical paths (API endpoints).
- Use `monkeypatch` for test-specific configuration.
- Test data resources live in `tests/resources/data/`.
- Use proper typing in test code too.
