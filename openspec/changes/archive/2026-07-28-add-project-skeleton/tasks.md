## 1. Non-testable setup (config and structure)

- [x] 1.1 Create `pyproject.toml` with deps from PROJECT.md §3 (including `pydantic-settings`),
      ruff config, and pytest config (`pytest-asyncio` enabled)
- [x] 1.2 Create `src/app/__init__.py` only (empty package — NO `main.py` yet)
- [x] 1.3 Create empty packages: `src/app/auth/__init__.py`, `src/app/search/__init__.py`,
      `src/app/audit/__init__.py`, `src/app/db/__init__.py`
- [x] 1.4 Create `docker-compose.yml` with Postgres 16 service only

## 2. TDD cycle for /health (the first red-green)

- [x] 2.1 Write failing test `tests/test_health.py` for `GET /health` → 200 `{"status": "ok"}`.
      Run it and verify it fails — expect a collection/import error because `app.main` and
      `create_app()` do not exist yet (RED). → **suggested-commit checkpoint (`test:`)**
- [x] 2.2 Create `src/app/config.py` with pydantic-settings `Settings` reading `DATABASE_URL`
      from env (minimal — only what the app factory needs to import cleanly)
- [x] 2.3 Create `src/app/main.py` with `create_app()` factory and the `GET /health` route,
      just enough to make the test pass. Run it and verify GREEN.
- [x] 2.4 Run `ruff check` and `ruff format --check`; fix until clean.
      → **suggested-commit checkpoint (`feat:`)**

## 3. Documentation

- [x] 3.1 Create `README.md` stub: plain-language description (what the platform is) plus how
      to run (`docker-compose up`, install deps, `pytest`), per PROJECT.md §11.
      → **suggested-commit checkpoint (`docs:`)**

## Notes

- The test in 2.1 must fail for the *right* reason: the app factory genuinely does not exist
  yet. A test that passes immediately (or errors on something unrelated) means the RED step
  proved nothing — fix the test, not the app, in that case.
- `config.py` is created in 2.2 (not step 1) because `main.py` imports it; it is part of what
  makes the health test go green, so it belongs inside the TDD cycle, not the setup phase.
- Do not create any model, migration, auth, search, audit code, or Keycloak service. Those
  belong to later changes.