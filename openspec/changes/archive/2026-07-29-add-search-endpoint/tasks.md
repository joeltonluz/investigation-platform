## 1. Audit service

- [x] 1.1 Create `src/app/audit/service.py` with `AuditService` that writes a `SearchAuditLog` row via the repository

## 2. Search strategies

- [x] 2.1 Create `src/app/search/strategies/__init__.py` and `src/app/search/strategies/base.py` with `SearchStrategy` abstract interface
- [x] 2.2 Create `src/app/search/strategies/analytics.py` — searches `analytics_reports.content` with ILIKE, returns `{title, summary}`
- [x] 2.3 Create `src/app/search/strategies/investigator.py` — searches `investigator_entities.name` with ILIKE, returns full data
- [x] 2.4 Create `src/app/search/strategies/case_manager.py` — searches `case_manager_cases` where `assigned_to == user_id`, returns metadata only

## 3. Search service

- [x] 3.1 Create `src/app/search/service.py` with `SearchService` (single dispatch and aggregation modes)

## 4. Search router

- [x] 4.1 Create `src/app/search/router.py` with `GET /api/v1/search` endpoint, wired to auth, SearchService, and audit

## 5. Wire into main app

- [x] 5.1 Register the search router in the main FastAPI app

## 6. Tests

- [x] 6.1 Write test (RED): analytics user gets only Analytics data
- [x] 6.2 Implement until test passes (GREEN)
- [x] 6.3 Write test (RED): investigator user gets only Investigator data
- [x] 6.4 Implement until test passes (GREEN)
- [x] 6.5 Write test (RED): user with both permissions gets aggregated results
- [x] 6.6 Implement until test passes (GREEN)
- [x] 6.7 Write test (RED): user without origin app's permission returns 403
- [x] 6.8 Implement until test passes (GREEN)
- [x] 6.9 Write test (RED): search is recorded in audit log
- [x] 6.10 Implement until test passes (GREEN)

## 7. Final verification

- [x] 7.1 Run `ruff check`, `ruff format --check`, and full test suite
