## Why

The repo has only specs (`PROJECT.md`) and agent instructions — no runnable code, no build config, no container setup. Before any domain feature can be built, there must be a minimal skeleton: package layout, dependency manifest, FastAPI app factory with a health endpoint, DB container, and a passing TDD cycle.

## What Changes

- Create `pyproject.toml` with locked deps from `PROJECT.md` §3 + ruff config + pytest config
- Create `src/app/` package with `__init__.py`, `main.py` (FastAPI app factory + GET /health), `config.py` (pydantic-settings from env)
- Create empty packages `src/app/auth/`, `src/app/search/`, `src/app/audit/`, `src/app/db/` each with `__init__.py`
- Create `docker-compose.yml` with Postgres 16 only (no Keycloak)
- Create `README.md` stub (non-technical, plain language per PROJECT.md §11)
- First TDD cycle: write failing test for `/health` → see it fail (RED) → implement → see it pass (GREEN)
- No models, no migrations, no auth, no search, no audit, no Keycloak

## Capabilities

### New Capabilities

_(none — this is infrastructure/setup, no domain capabilities are introduced)_

### Modified Capabilities

_(none)_

## Impact

- New files: `pyproject.toml`, `docker-compose.yml`, `README.md`, `src/app/**`
- New dev dependency: `pydantic-settings` (implied by PROJECT.md but not listed in §3 table — only `pydantic v2` is listed; `pydantic-settings` is the standard companion for env-driven config)
- No existing code affected (repo is empty)
