## Context

Repo is empty — no `pyproject.toml`, no `src/`, no `docker-compose.yml`, no test infrastructure. The authoritative spec (`PROJECT.md`) defines the stack and architecture but hasn't been materialized into code.

## Goals / Non-Goals

**Goals:**
- Create a runnable Python project with `uv`/`pip` install
- FastAPI app factory (`create_app()`) with a single `GET /health` endpoint
- Config loaded from env via `pydantic-settings`
- Docker Compose with Postgres 16 only
- Package structure mirroring `PROJECT.md` §5 directory layout
- First RED→GREEN TDD cycle for `/health`
- `ruff` config in `pyproject.toml` so `ruff check` and `ruff format` work immediately

**Non-Goals:**
- No SQLAlchemy models, Alembic migrations, or DB schema
- No auth, search, audit logic
- No Keycloak container or JWT wiring
- No test coverage beyond the health-check cycle

## Decisions

1. **`pydantic-settings` for config.** Not in the PROJECT.md §3 table, but it's the standard companion to Pydantic v2 for env-driven settings and the project already requires `pydantic v2`. Adding it is a natural extension, not a new dependency.

2. **`src/` layout with `src/app/` as the top-level package.** Matches PROJECT.md §5. Avoids `PYTHONPATH` hacks because `pyproject.toml` will use `[project.urls]` or tool-specific config to point pytest at `src/`.

3. **pytest config in `pyproject.toml`.** Keeps everything in one file. `pythonpath = ["src"]` so imports like `from app.main import create_app` work without env manipulation.

4. **Postgres 16 in Docker Compose only.** No app container — the skeleton is meant to be run locally with `uv run` or `pip install -e .` + `uvicorn`. The DB is the only external service needed.

5. **Test DB = ephemeral Docker Postgres.** Test fixtures will start/stop via a test container or assume a running Postgres on `localhost:5432`. The config reads `DATABASE_URL` from env, defaulting to `postgres+psycopg://postgres:postgres@localhost:5432/investigation_test`.

## Risks / Trade-offs

- **[Low] `pydantic-settings` not explicitly allowed.** Mitigation: it's a thin wrapper over Pydantic v2 by the same author, used in every FastAPI project for env config. Defensible.
- **[Low] No DB connection at `/health`.** The endpoint only checks that the app boots. DB health checks will come with the first feature that uses the DB.
