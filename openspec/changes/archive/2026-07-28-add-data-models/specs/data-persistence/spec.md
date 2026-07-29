## ADDED Requirements

### Requirement: System persists analytics reports
The system SHALL store analytics reports in an `analytics_reports` table with columns `id` (UUID PK, server-generated via `gen_random_uuid()`), `title` (text), `content` (text), and `created_at` (timestamptz, server-default `now()`).

#### Scenario: Create and retrieve an analytics report
- **WHEN** a new report is created with title and content
- **THEN** the returned row has a non-null UUID `id` and a non-null `created_at` timestamp

### Requirement: System persists investigator entities
The system SHALL store investigator entities in an `investigator_entities` table with columns `id` (UUID PK), `type` (native ENUM: `person`, `company`, `transaction`, `document`), `name` (text), `data` (JSONB), and `created_at` (timestamptz).

#### Scenario: Create and retrieve an investigator entity with JSONB data
- **WHEN** a new entity is created with type, name, and a dict in `data`
- **THEN** the returned row preserves the dict structure and values in `data`

#### Scenario: Invalid enum type is rejected
- **WHEN** an entity is created with `type` not in `{person, company, transaction, document}`
- **THEN** the database raises an integrity error

### Requirement: System persists case manager cases
The system SHALL store cases in a `case_manager_cases` table with columns `id` (UUID PK), `title` (text), `assigned_to` (text), `status` (native ENUM: `open`, `in_progress`, `closed`), and `created_at` (timestamptz).

#### Scenario: Create and retrieve a case
- **WHEN** a new case is created with title, assigned_to, and status
- **THEN** the returned row matches the input data

### Requirement: System persists search audit log entries
The system SHALL store audit log entries in a `search_audit_log` table with columns `id` (UUID PK), `user_id` (text), `app` (text), `query` (text), and `timestamp` (timestamptz).

#### Scenario: Create and retrieve an audit log entry
- **WHEN** a new audit log entry is created with user_id, app, and query
- **THEN** the returned row matches the input data

### Requirement: Data access goes through repositories
Each table SHALL have a corresponding repository class providing `add()`, `get()`, and `list()` methods. Routes and services MUST NOT access models or sessions directly.

#### Scenario: Repository add returns the persisted object
- **WHEN** a model instance is passed to a repository's `add()` method
- **THEN** the returned object has a non-null UUID `id`

### Requirement: All tables are created via Alembic migration
The initial migration SHALL create all four tables, their ENUM types, and indexes. Indexes: `investigator_entities` on `type` and `name`; `case_manager_cases` on `assigned_to`; `search_audit_log` on `user_id` and `app`; `analytics_reports` btree on `title`.

#### Scenario: Migration creates all objects
- **WHEN** the migration is applied to an empty database
- **THEN** all four tables, two ENUM types, and the specified indexes exist
