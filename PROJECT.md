# Project: investigation-platform

## 1. What this is

Backend for a distributed, on-premises **investigative intelligence platform** used by
oversight bodies, corporate compliance, and financial investigation teams.

The platform is composed of three applications that share one backend:

1. **Analytics** — analytical reports, dashboards, exports.
2. **Investigator** — relationship graphs, timelines, link analysis.
3. **Case Manager** — investigative case management, task assignment, workflow.

A single unified endpoint (`/api/v1/search`) is shared by all three apps but behaves
differently depending on which app made the request and which permissions the user holds.

> This file is the **source of truth** for how the AI agent must build and reason about
> this project. When code and this file disagree, this file wins — update it deliberately,
> never silently.

---

## 2. Golden rules for the AI agent (read first)

These rules override any default behavior. Follow them literally.

1. **TDD is mandatory. No production code without a failing test first.**
   The order for every unit of work is: write the test → run it → see it fail (RED) →
   write the minimum code to pass (GREEN) → refactor. If you are about to write
   implementation code and there is no failing test for it, STOP and write the test first.

2. **NEVER run `git commit`, `git add`, `git push`, or any git-writing command on your own.**
   The human decides when to commit. You may *suggest* a commit message, but you must not
   execute it. Staging and committing are done by the human, by hand. This is non-negotiable.

3. **Keep every change tightly scoped.** One OpenSpec change = one coherent feature.
   Do not implement authentication, search, and auditing in the same change. If a task
   seems to touch several features, stop and ask the human to split it.

4. **Favor the simplest implementation that satisfies the spec.** Add complexity only when
   the spec requires it. This project is evaluated on *pragmatism*, not cleverness.

5. **Never invent scope.** If a requirement is ambiguous, ask. Do not add endpoints,
   fields, config, or dependencies that were not requested.

6. **Comment only non-obvious decisions.** Explain *why*, not *what*. No noise comments.

7. **All code, comments, commit messages, and identifiers are in English.**
   Documentation meant for the human/reviewer may be in Portuguese where noted.

---

## 3. Tech stack (locked versions — do not substitute)

| Concern            | Choice                          | Notes                                             |
|--------------------|---------------------------------|---------------------------------------------------|
| Language           | Python 3.12                     | Do not use 3.13-only or 3.11-removed syntax.      |
| Web framework      | FastAPI ^0.115                  | Use `Depends()` for DI, like Nest providers/guards.|
| ASGI server        | uvicorn ^0.32                   | Dev + container entrypoint.                        |
| Validation/schemas | Pydantic v2 (^2.9)              | v2 API only (`model_config`, `model_validate`).   |
| Settings           | pydantic-settings ^2.5          | Env-driven `Settings`; `BaseSettings` moved out of Pydantic core in v2. |
| ORM                | SQLAlchemy 2.0 (^2.0)           | 2.0 style (`Mapped`, `mapped_column`), no legacy. |
| Migrations         | Alembic ^1.13                   | Autogenerate reviewed by hand, never trusted raw. |
| Database           | PostgreSQL 16                   | Same engine in tests and prod. No SQLite fallback.|
| DB driver          | psycopg (v3) ^3.2               | Use `psycopg`, not `psycopg2`.                     |
| JWT                | python-jose[cryptography] ^3.3  | RS256. Keycloak is mocked via a local RSA keypair.|
| Tests              | pytest ^8.3 + pytest-asyncio    | httpx `AsyncClient` for endpoint tests.           |
| HTTP test client   | httpx ^0.27                     | `ASGITransport` against the FastAPI app.          |
| Lint/format        | ruff ^0.7                       | Format + lint. Run before suggesting a commit.    |
| Package manager    | uv (preferred) or pip           | `pyproject.toml` is the single source for deps.    |

**Do not add any dependency not listed here without the human approving it first.**

---

## 4. Database rationale (why Postgres from day 1)

We use PostgreSQL from the very first test, not SQLite, because:

- `investigator_entities.data` is a JSON column → we rely on Postgres **JSONB** semantics.
- The spec requires **indexes** in the migration; index behavior differs between engines.
- Testing on the same engine as production removes an entire class of "works on my machine"
  failures that would surface during the live demo.

Tests run against a disposable Postgres (Docker container). Never introduce a SQLite path
"just for tests" — that would defeat the reason above.

---

## 5. Architecture & design patterns

Thin layers. Do **not** build full Clean/Hexagonal architecture — it is over-engineering
for this scope and reads as a lack of pragmatism.

Request flow for `/api/v1/search`:

```
FastAPI route
  → auth dependency        (get_current_user: validates JWT, extracts identity)
  → authz dependency       (require_permission: checks the app-specific permission)
  → SearchService          (dispatches to the right strategy per app)
      → SearchStrategy      (one per app: Analytics / Investigator / Case Manager)
          → Repository      (data access for that app's table)
  → AuditService           (records the search in search_audit_log)
```

Patterns and rules:

- **Repository pattern.** All database access goes through a repository class. A route or
  service **must never** run raw queries or touch a SQLAlchemy `Session` directly. This is
  strictly enforced.
- **Strategy pattern.** Each application implements a `SearchStrategy` with the same
  interface (`search(query, user) -> results`). The endpoint orchestrates; it contains no
  app-specific branching beyond selecting the strategy. Adding a 4th app must not require
  editing the endpoint's core logic.
- **Dependency Injection via FastAPI `Depends()`.** Auth, authz, DB session, and services
  are injected. Mirror the Nest mental model: `Depends` ≈ providers/guards, Pydantic
  models ≈ DTOs.
- **Service layer** holds business logic. Routes stay thin: parse input, call a service,
  shape the response.

### Directory layout

```
investigation-platform/
├── openspec/
├── src/app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory, router registration
│   ├── config.py            # Settings via pydantic-settings (env-driven)
│   ├── db.py                # engine, session factory, get_db dependency
│   ├── auth/                # JWT dependency, claim extraction, permission checks
│   ├── search/
│   │   ├── router.py        # /api/v1/search
│   │   ├── service.py       # SearchService (dispatch + aggregation)
│   │   └── strategies/      # analytics.py, investigator.py, case_manager.py
│   ├── models/              # SQLAlchemy 2.0 models
│   ├── repositories/        # one repository per table
│   └── audit/               # AuditService + audit repository
├── tests/
├── alembic/
├── docker-compose.yml
├── DECISIONS.md             # engineering rationale (reviewer-facing, may be in PT)
└── README.md
```

---

## 6. Domain rules (from the assignment — implement exactly)

### Tables

- `analytics_reports(id, title, content, created_at)`
- `investigator_entities(id, type, name, data, created_at)` — `data` is **JSONB**;
  `type` ∈ {person, company, transaction, document}.
- `case_manager_cases(id, title, assigned_to, status, created_at)`
- `search_audit_log(id, user_id, app, query, timestamp)`

### Search behavior per app

| App          | Permission             | Searches in                          | Returns                                  |
|--------------|------------------------|--------------------------------------|------------------------------------------|
| Analytics    | `analytics:search`     | report content                       | aggregated data, no sensitive detail     |
| Investigator | `investigator:search`  | entities (person/company/txn/doc)    | full data                                |
| Case Manager | `case-manager:search`  | only cases assigned to the user      | metadata only (no content search)        |

- A user with **multiple** permissions gets an **aggregated** result across the allowed apps.
- A user with **no** relevant permission for a requested app gets **HTTP 403**.
- **Every** search is written to `search_audit_log`, including which app it targeted.

---

## 7. Authentication & authorization

Realm decision (see `DECISIONS.md` for full rationale): **single Keycloak realm
(`plataforma`) with one client per app**. This is what makes SSO work; multiple realms
would break single sign-on, which is the primary requirement.

JWT handling:

- Tokens are **RS256**, validated against a public key.
- In tests, Keycloak is **mocked**: a local RSA keypair signs test tokens; the auth
  dependency validates against the corresponding public key. Same code path as production —
  only the key source differs (local key in tests, Keycloak JWKS in the running stack).
- The auth dependency extracts: `user_id` (`sub`), `app_client_id` (`azp` — identifies
  which app/client), and `permissions` (from client roles / `realm_access` or a
  `permissions` claim — document the exact shape in `auth/`).
- Authorization is a separate dependency (`require_permission("analytics:search")`) so the
  permission check is declarative at the route and independently testable.

Document the **expected JWT structure** in a docstring/README fragment near the auth code.

---

## 8. Error handling (never ship happy-path only)

The assignment explicitly rewards robust error handling. Enforce:

- **No bare `except:`.** Catch specific exceptions. Never swallow errors silently.
- Map errors to correct HTTP status: `401` (no/invalid token), `403` (authenticated but
  lacks permission), `422` (invalid input — let Pydantic do this), `404` (missing resource),
  `500` only for genuinely unexpected failures.
- Return a **consistent error envelope** (e.g. `{"detail": "..."}` — FastAPI's default is
  fine; be consistent). No leaking stack traces or SQL to clients.
- Validate all inbound query/body params with Pydantic. Reject empty or malformed search
  queries with `422`, not a 500.
- Auditing must not break the request path silently: if writing the audit log fails, that is
  a real error — log it; do not pretend the search "succeeded cleanly" while losing the trail.
- Database access uses context-managed sessions; always roll back on failure.

---

## 9. Testing rules

- Framework: `pytest` + `pytest-asyncio`. Endpoint tests use httpx `AsyncClient` with
  `ASGITransport` against the app.
- Tests run against a **real Postgres** (throwaway container / test database), created and
  torn down per session; each test gets a clean transaction (rollback after).
- Minimum required tests (from the assignment) — all must exist:
  1. User with `analytics:search` searches → receives only Analytics data.
  2. User with `investigator:search` searches → receives Investigator data.
  3. User with both permissions → receives aggregated results.
  4. User without permission → receives **HTTP 403**.
  5. A search is recorded in the audit log.
- Test tokens are minted in a fixture using the local RSA private key. Never call a real
  Keycloak in tests.
- A feature is "done" only when its tests are green **and** `ruff` is clean.

---

## 10. Git & commit conventions

- **The agent never commits.** Never run `git add`, `git commit`, `git push`, `git reset`,
  or any state-changing git command. Only the human commits, and only when they decide to.
  The agent may, at most, *print a suggested commit message* for the human to copy.
- **Conventional Commits, in English.** Format: `type: short imperative description`.
  Allowed types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `build`, `ci`.
  Examples:
  - `test: add failing test for search 403 without permission`
  - `feat: add require_permission auth dependency`
  - `feat: implement analytics search strategy`
  - `refactor: extract SearchService dispatch logic`
  - `docs: document expected JWT structure`
- Commits should tell the TDD story: the failing-test commit precedes the implementation
  commit. Small, ordered commits over one giant commit.

---

## 11. Documentation expectations

- `DECISIONS.md` (repo root, **not** the README) holds the engineering rationale in an
  ADR-like format: the realm decision, Postgres-from-day-1, patterns chosen and rejected.
  This file is reviewer-facing and may be written in Portuguese.
- `README.md` explains, for a **non-technical reader**, what the platform does and how to
  run it (`docker-compose up`, run tests). Plain language.
- Non-obvious code decisions get a short `why` comment inline.
- If you get stuck, document what you tried — that is explicitly worth points.