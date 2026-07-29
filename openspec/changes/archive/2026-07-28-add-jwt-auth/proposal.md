## Why

The platform has three apps (Analytics, Investigator, Case Manager) that need authenticated access, but there is no auth layer yet. Every endpoint is currently open. This change adds the JWT authentication and permission-based authorization so endpoints can require a valid token and specific permissions.

## What Changes

- Add `app/auth/` module with:
  - Token validation (RS256 signature, expiry) via python-jose
  - Permission flattening helper: `resource_access.<client>.roles` → `{"<app>:<action>"}` set
  - `get_current_user` FastAPI dependency (returns user identity + permissions, 401 on invalid token)
  - `require_permission(permission)` dependency factory (403 when authenticated but lacking permission)
- Test infrastructure: local RSA keypair fixture, token-factory fixture
- Tests: token validation, permission flattening, `get_current_user` (positive + error), `require_permission` (pass + 403)
- Document expected JWT structure in a docstring at `app/auth/`

No models, no DB, no audit, no search endpoint — pure auth layer.

## Capabilities

### New Capabilities
- `jwt-auth`: JWT token validation, identity extraction, and permission-based authorization dependency for FastAPI routes

### Modified Capabilities

None.

## Impact

- New `app/auth/` package with 3–4 modules
- No new dependencies (python-jose already in `pyproject.toml`)
- No changes to existing models, repos, or database
- No search endpoint or audit-writing logic
