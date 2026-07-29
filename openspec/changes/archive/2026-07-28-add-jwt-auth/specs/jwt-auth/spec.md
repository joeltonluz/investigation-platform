## ADDED Requirements

### Requirement: Token validation

The system SHALL validate RS256 JWTs against a public RSA key. Validation SHALL check the signature and the `exp` claim. An invalid signature or expired token SHALL result in a 401 response. A missing `Authorization` header SHALL also result in a 401 response.

#### Scenario: Valid token is accepted
- **WHEN** a valid RS256-signed JWT with a future `exp` is presented
- **THEN** the system extracts `sub`, `azp`, and `resource_access` from the payload

#### Scenario: Invalid signature returns 401
- **WHEN** a JWT signed with a different key is presented
- **THEN** the system returns HTTP 401

#### Scenario: Expired token returns 401
- **WHEN** a JWT with `exp` in the past is presented
- **THEN** the system returns HTTP 401

#### Scenario: Malformed token returns 401
- **WHEN** a non-JWT string is presented in the Authorization header
- **THEN** the system returns HTTP 401

#### Scenario: Missing Authorization header returns 401
- **WHEN** no `Authorization` header is sent
- **THEN** the system returns HTTP 401

### Requirement: Permission flattening

The system SHALL flatten `resource_access.<client_id>.roles` into a set of `"<app>:<action>"` strings. The client-id-to-app-prefix mapping SHALL be:
- `analytics-api` → `analytics`
- `investigator-api` → `investigator`
- `case-manager-api` → `case-manager`

A role named `"search"` under `analytics-api` SHALL produce `"analytics:search"`.

#### Scenario: Single app, single role
- **WHEN** `resource_access` contains `{"analytics-api": {"roles": ["search"]}}`
- **THEN** the flattened set contains `"analytics:search"`

#### Scenario: Multiple apps and roles
- **WHEN** `resource_access` contains `{"analytics-api": {"roles": ["search", "export"]}, "investigator-api": {"roles": ["search"]}}`
- **THEN** the flattened set contains `"analytics:search"`, `"analytics:export"`, `"investigator:search"`

#### Scenario: Unknown client is ignored
- **WHEN** `resource_access` contains an unknown client id (not in the mapping)
- **THEN** no permissions are produced for that client

#### Scenario: Empty roles produces no permissions
- **WHEN** `resource_access` contains a client with an empty `roles` array
- **THEN** no permissions are produced for that client

### Requirement: Permission check on routes

The system SHALL provide a `require_permission(permission: str)` dependency factory. When the user's permission set contains the required permission, the request proceeds. When it does not, the system returns HTTP 403.

#### Scenario: Permission present passes
- **WHEN** a user with `"analytics:search"` in their permissions hits a route requiring `"analytics:search"`
- **THEN** the request is allowed to proceed

#### Scenario: Permission absent returns 403
- **WHEN** a user without `"analytics:search"` in their permissions hits a route requiring `"analytics:search"`
- **THEN** the system returns HTTP 403

### Requirement: Expected JWT structure documented

The system SHALL document the expected JWT payload structure in a docstring at `app/auth/`.

#### Scenario: Docstring exists
- **WHEN** inspecting the `app/auth/` package
- **THEN** there SHALL be a docstring describing the expected JWT claims: `sub`, `azp`, `resource_access`, `exp`, `iat`
