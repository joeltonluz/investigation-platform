## Context

The platform has three FastAPI apps (Analytics, Investigator, Case Manager) that share a single Keycloak realm (`plataforma`) with one client per app. Tokens are RS256-signed JWTs. Currently no auth layer exists — any request reaches any endpoint.

The auth layer must be testable without a real Keycloak. ADR-007 mandates a local RSA keypair for signing/verifying test tokens, keeping the code path identical to production (only the key source changes).

## Goals / Non-Goals

**Goals:**
- Validate RS256 JWTs (signature, expiry) using a public key
- Extract `user_id` (`sub`), `app_client_id` (`azp`), and permissions (`resource_access.<client>.roles`)
- Expose a `get_current_user` FastAPI dependency returning a dataclass with those fields
- Expose a `require_permission(permission: str)` dependency factory (returns 403 if missing)
- Flatten `resource_access` into a set of `"<app>:<action>"` strings via an explicit mapping
- Document the expected JWT structure in a docstring at `app/auth/`

**Non-Goals:**
- No search endpoint
- No changes to DB models, repositories, or migrations
- No audit-writing logic (audit will be added in a later change)
- No JWKS key rotation or real Keycloak integration

## Decisions

1. **Token validation in a single module `token.py`.** Encapsulates `jose.jwt.decode()` with RS256 algorithm, public key, and expiry check. Raises a custom `InvalidTokenError` on any failure, which `get_current_user` catches and converts to HTTP 401.

2. **Permission flattening in a dedicated module `permissions.py`.** A dict maps client IDs to app prefixes (e.g., `"analytics-api" → "analytics"`). The flattening iterates `resource_access[client].roles` and prefixes each role with the mapped app prefix. This keeps the mapping explicit and centralized.

3. **`get_current_user` as a `fastapi.Depends` callable.** Reads `Authorization: Bearer <token>`, passes the token to the validator, constructs a `User` dataclass, and returns it. On any error (missing header, invalid token, expired), raises `HTTPException(401)`.

4. **`require_permission` as a dependency factory.** Takes a permission string, returns a dependency that calls `get_current_user` first (via `Depends`), then checks membership in the user's permission set. On missing permission, raises `HTTPException(403)`.

5. **Test RSA keypair in `conftest.py`.** Generated once per test session via `cryptography`'s `rsa.generate_private_key()`. The public key is PEM-encoded for the validator; the private key signs tokens in the token factory.

6. **Token factory fixture.** Accepts `sub`, `azp`, `resource_access`, and `exp` (with a default far-future expiry). Signs the payload with the private key using RS256 and returns a ready-to-use JWT string.

## Risks / Trade-offs

- **Token structure dependency.** The exact claim layout mirrors the current Keycloak mapper convention. If the real Keycloak uses a different structure (e.g., a custom `permissions` claim instead of `resource_access`), the extraction logic must change. Mitigation: the expected structure is documented in a docstring, making the assumption explicit and easy to update.
- **Static client→app mapping.** Adding a new app requires editing the mapping dict. Acceptable for the current three-app scope. Mitigation: the mapping is centralized in one place.
- **No JWKS caching.** The validator loads a single public key. For production with Keycloak, a JWKS endpoint with caching would be needed. This is deferred to later.
