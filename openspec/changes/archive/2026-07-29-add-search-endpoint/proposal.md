## Why

The platform has three apps (Analytics, Investigator, Case Manager) that all need a unified search endpoint, but no search infrastructure exists yet. The endpoint must dispatch to the correct search strategy per origin app, enforce app-specific permissions, and audit every search.

## What Changes

- Add `GET /api/v1/search?q=<query>` endpoint shared by all three apps
- Add `app/search/strategies/` with one `SearchStrategy` per app (analytics, investigator, case-manager)
- Add `SearchService` in `app/search/service.py` to dispatch and aggregate results
- Wire auth dependencies: `get_current_user`, `require_permission("<app>:search")`, and azp-to-app mapping
- Write every search to `search_audit_log` via the existing repository
- Add AuditService for audit-write logic
- Tests: 5 required endpoint tests per spec, plus strategy unit tests

## Capabilities

### New Capabilities
- `search`: Unified search endpoint with per-app strategies, permission enforcement, and audit logging

### Modified Capabilities

None.

## Impact

- New `app/search/strategies/` package with three strategy modules
- New or updated `app/search/router.py`, `app/search/service.py`
- New or updated `app/audit/service.py` for audit-write
- No new dependencies
- No changes to existing models or database schema
