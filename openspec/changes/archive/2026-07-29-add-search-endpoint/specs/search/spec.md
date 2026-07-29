## ADDED Requirements

### Requirement: Unified search endpoint

The system SHALL expose `GET /api/v1/search?q=<query>` as a single endpoint shared by all three applications. The endpoint SHALL use the JWT's `azp` claim to determine the origin app and the flattened permission set to enforce authorization.

#### Scenario: Analytics user searches
- **WHEN** a user with `azp=analytics-api`, permission `analytics:search`, and `q=report` hits the endpoint
- **THEN** the response SHALL contain only Analytics report data matching the query

#### Scenario: Investigator user searches
- **WHEN** a user with `azp=investigator-api`, permission `investigator:search`, and `q=company-x` hits the endpoint
- **THEN** the response SHALL contain only Investigator entity data matching the query

#### Scenario: User with both permissions searches aggregated
- **WHEN** a user with both `analytics:search` and `investigator:search` permissions and `q=test` hits the endpoint
- **THEN** the response SHALL contain results from both Analytics and Investigator grouped by app

#### Scenario: User without the origin app's search permission
- **WHEN** a user with `azp=analytics-api` but without `analytics:search` hits the endpoint
- **THEN** the system SHALL return HTTP 403

### Requirement: Search audit logging

Every search executed through the endpoint SHALL be recorded in `search_audit_log` with `user_id`, `app`, `query`, and `timestamp`.

#### Scenario: Search is recorded
- **WHEN** a user executes a search
- **THEN** a row SHALL exist in `search_audit_log` with the user's ID, the origin app, and the query string

### Requirement: Analytics search strategy

The Analytics strategy SHALL search `analytics_reports` by matching `content` with ILIKE and SHALL return only aggregated data (no sensitive detail).

#### Scenario: Matches by content
- **WHEN** the query matches the content of an analytics report
- **THEN** the strategy SHALL return report entries with `title` and `summary` fields only

### Requirement: Investigator search strategy

The Investigator strategy SHALL search `investigator_entities` by matching `name` with ILIKE and SHALL return full entity data.

#### Scenario: Matches by name
- **WHEN** the query matches the name of an investigator entity
- **THEN** the strategy SHALL return full entity entries including type, name, and data

### Requirement: Case Manager search strategy

The Case Manager strategy SHALL search only cases assigned to the current user (`assigned_to == user.user_id`) and SHALL return metadata only (no content search).

#### Scenario: Returns assigned cases
- **WHEN** a case manager user searches
- **THEN** the strategy SHALL return case entries with `id`, `title`, and `status` where `assigned_to` matches the user's ID

#### Scenario: Ignores unassigned cases
- **WHEN** a case exists but is assigned to a different user
- **THEN** that case SHALL NOT appear in the results
