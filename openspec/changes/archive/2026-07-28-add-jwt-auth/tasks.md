## 1. Auth package structure and wiring

- [x] 1.1 Create `src/app/auth/` package with `__init__.py` and docstring documenting expected JWT structure

## 2. Token validation

- [x] 2.1 Create `src/app/auth/token.py` with `InvalidTokenError` and `validate_token(token: str, public_key: str) -> dict` using python-jose RS256 decoding
- [x] 2.2 Write test (RED): valid token with correct key returns decoded payload
- [x] 2.3 Implement `validate_token` until test passes (GREEN)
- [x] 2.4 Write test (RED): invalid signature raises `InvalidTokenError`
- [x] 2.5 Implement signature check until test passes (GREEN)
- [x] 2.6 Write test (RED): expired token raises `InvalidTokenError`
- [x] 2.7 Implement expiry check until test passes (GREEN)
- [x] 2.8 Write test (RED): malformed token raises `InvalidTokenError`
- [x] 2.9 Implement malformed token handling until test passes (GREEN)

## 3. Permission flattening

- [x] 3.1 Create `src/app/auth/permissions.py` with `flatten_permissions(resource_access: dict) -> set[str]` and the client-to-app mapping
- [x] 3.2 Write test (RED): single app, single role produces `"analytics:search"`
- [x] 3.3 Implement flattening until test passes (GREEN)
- [x] 3.4 Write test (RED): multiple apps and roles produce correct set
- [x] 3.5 Implement until test passes (GREEN)
- [x] 3.6 Write test (RED): unknown client produces no permissions
- [x] 3.7 Implement until test passes (GREEN)

## 4. User dataclass and token factory

- [x] 4.1 Create `src/app/auth/models.py` with `User` dataclass (`user_id`, `app_client_id`, `permissions`)
- [x] 4.2 Create test RSA keypair fixture in `tests/conftest.py` (session-scoped)
- [x] 4.3 Create `create_token` factory fixture (accepts `sub`, `azp`, `resource_access`, uses RSA private key to sign RS256 JWT)

## 5. FastAPI dependencies

- [x] 5.1 Create `src/app/auth/dependencies.py` with `get_current_user` and `require_permission`
- [x] 5.2 Write test (RED): `get_current_user` with valid token returns `User` with correct fields
- [x] 5.3 Implement `get_current_user` until test passes (GREEN)
- [x] 5.4 Write test (RED): `get_current_user` with missing/invalid/expired token returns 401
- [x] 5.5 Implement error handling until test passes (GREEN)
- [x] 5.6 Write test (RED): `require_permission` passes when permission present
- [x] 5.7 Implement `require_permission` until test passes (GREEN)
- [x] 5.8 Write test (RED): `require_permission` returns 403 when permission absent
- [x] 5.9 Implement 403 handling until test passes (GREEN)

## 6. Final verification

- [x] 6.1 Run `ruff check`, `ruff format --check`, and full test suite
