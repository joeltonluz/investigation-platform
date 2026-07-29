## 1. DB layer foundation

- [x] 1.1 Create `src/app/db/base.py` with shared `DeclarativeBase`
- [x] 1.2 Create `src/app/db/session.py` with engine, `SessionLocal`, and `get_db` dependency
- [x] 1.3 Create `src/app/db/models.py` with all four models, ENUMs, UUID PKs, JSONB, timestamps

## 2. Repositories

- [x] 2.1 Create `src/app/db/repositories/__init__.py` and four repo modules (add/get/list only)

## 3. TDD cycle — round-trip test

- [x] 3.1 Write failing test that round-trips one row of each model against Postgres (RED)
- [x] 3.2 Implement until test passes (GREEN); ruff clean

## 4. Alembic

- [x] 4.1 Create `alembic.ini` and `alembic/env.py` wired to `Base.metadata` and `Settings.database_url`
- [x] 4.2 Autogenerate initial migration, review by hand, then apply
- [x] 4.3 Run test suite to confirm migration is compatible

## 5. Seed data

- [x] 5.1 Create seed script inserting 10 rows per domain table

## 6. Final verification

- [x] 6.1 Run `ruff check`, `ruff format --check`, and full test suite
