## Context

The platform has three apps (Analytics, Investigator, Case Manager) sharing one FastAPI process. Each app has its own search behavior but all use a single endpoint. Auth is in place (JWT, permissions). DB models and repositories exist. No search logic or endpoint exists yet.

## Goals / Non-Goals

**Goals:**
- `GET /api/v1/search?q=<query>` shared endpoint
- Per-app `SearchStrategy` with the same `search(query, user) -> results` interface
- `SearchService` dispatching to the right strategy based on the origin app (`azp`)
- Aggregated mode: user with permissions on multiple apps gets combined results grouped by app
- Permission check: `require_permission("<app>:search")` per the origin app
- Every search written to `search_audit_log` via the repository
- All DB access through repositories; no raw queries in routers/services

**Non-Goals:**
- No full-text search / ranking — basic ILIKE/filter is sufficient
- No changes to models, DB schema, or migrations
- No new dependencies

## Decisions

1. **`SearchStrategy` interface.** Each strategy implements `search(query: str, user: User) -> list[dict]`. Strategies are stateless and receive a repository via constructor injection.

2. **SearchService as the orchestrator.** Receives the `SearchStrategy` instance (single-app mode) or a list of strategies (aggregated mode). Calls each strategy and groups results by app prefix in an envelope: `[{"app": "...", "results": [...]}]`.

3. **Router maps azp to strategy.** `GET /api/v1/search` reads `q` from query params, resolves the strategy from `azp` via the same `CLIENT_TO_APP` mapping, calls `SearchService`, writes the audit log, and returns results. The router owns the permission check via `require_permission`.

4. **Analytics strategy.** Searches `analytics_reports` where `content ILIKE '%<query>%'`. Returns only `{"title", "summary"}` — no sensitive content. `summary` is a computed/placeholder field from `content[:200]` since the model has no dedicated summary column.

5. **Investigator strategy.** Searches `investigator_entities` where `name ILIKE '%<query>%'`. Returns full entity data.

6. **Case Manager strategy.** Searches `case_manager_cases` where `assigned_to == user.user_id`. Returns only `{"id", "title", "status"}` — metadata only, no content search.

7. **AuditService.** Simple wrapper: receives a session, builds a `SearchAuditLog` row, and calls `SearchAuditLogRepository.add()`. If the write fails, the exception propagates (no silent swallow).

8. **Endpoint test approach.** Use `httpx.AsyncClient` + `ASGITransport` against a FastAPI app wired with real dependencies (session, repositories, strategies). Seed test data, mint RSA-signed tokens per test case.

## Risks / Trade-offs

- **Analytics `summary` field.** The model has `title`, `content`, and `created_at` but no `summary`. Using `content[:200]` as a pseudo-summary is pragmatic but fragile. Mitigation: this is a deliberate decision; a `summary` field can be added later.
- **Case manager no content search.** The spec says only search by `assigned_to`, no content filtering. This may feel incomplete but matches the requirements. Mitigation: documented in strategy.
- **Audit write failures are real errors.** The requirement says audit-write exceptions must propagate and not be swallowed. This is consistent with the existing ADR-007 error principle.
