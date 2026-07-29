# AGENTS.md — investigation-platform

Rules the agent MUST follow in this repository. These override any default behavior.
This file holds the **unbreakable rules** (always loaded). The full rationale, exact
versions, and detailed domain rules live in `PROJECT.md` — read it before any non-trivial
task. When a rule here points to a `PROJECT.md` section, the rule is binding; the section
explains *why*.

## Repository state

This repo is **pre-implementation**: no source code, no `pyproject.toml`, no build/lint
config, and (initially) no commits yet exist. Everything is created from scratch following
`PROJECT.md`. Do not assume any scaffolding is present — check first, then create it as part
of a scoped change.

## Workflow (OpenSpec via OpenCode)

Work proceeds one small change at a time through the OpenSpec commands:
`/opsx-propose` (create a change: proposal, design, tasks) → human reviews and edits the
artifacts → `/opsx-apply` (implement the tasks) → `/opsx-verify` (check it holds) →
`/opsx-archive` (move the completed change to history). Never jump straight to implementation
without a reviewed proposal. One change = one coherent feature.

## Hard boundaries (never violate)

- **NEVER run git write commands.** No `git add`, `git commit`, `git push`, `git reset`,
  `git rebase`, or any state-changing git command. The human stages and commits by hand,
  and only when they decide to. You may print a *suggested* commit command — never execute it.
- **TDD is mandatory.** No production code without a failing test first: write the test →
  see it fail (RED) → write the minimum code to pass (GREEN) → refactor. If there is no
  failing test for the code you are about to write, STOP and write the test first.
- **One change = one coherent feature.** Do not implement auth, search, and auditing in the
  same change. If a task spans several features, stop and ask to split it.
- **Never invent scope.** No endpoints, fields, config, or dependencies that were not asked
  for. If a requirement is ambiguous, ask.

## Binding rules (short form — full detail in PROJECT.md)

These are the rules that must stay in force even if `PROJECT.md` is not reloaded. They are
intentionally terse; the cited sections carry the reasoning and specifics.

- **Stack is locked** (see `PROJECT.md` §3). Python 3.12 · FastAPI · Pydantic v2 ·
  SQLAlchemy 2.0 (`Mapped`/`mapped_column`) · Alembic · PostgreSQL 16 (psycopg v3) ·
  python-jose (RS256) · pytest + pytest-asyncio · httpx · ruff. Never substitute a version
  or swap a library. **Do not add any dependency** not listed there without human approval.
- **Postgres everywhere, no SQLite** (see `PROJECT.md` §4) — including tests. Never add a
  SQLite path "just for tests".
- **Architecture: thin layers, Repository + Strategy** (see `PROJECT.md` §5). Request flow:
  route → auth dependency → `require_permission` → SearchService → per-app SearchStrategy →
  Repository → AuditService. All DB access goes through a repository; routes/services never
  run raw queries or touch a Session directly. Adding a 4th app must not require editing the
  endpoint core. No full Clean/Hexagonal architecture.
- **Error handling, never happy-path only** (see `PROJECT.md` §8). No bare `except`. Correct
  HTTP codes: 401 (no/invalid token), 403 (authenticated but lacks permission), 422 (invalid
  input — let Pydantic handle it), 404, 500 only for genuine unexpected failures. Consistent
  error envelope. Never leak stack traces or SQL. Audit-write failures are real errors — log
  them, never silently drop the trail.
- **Language:** all code, comments, identifiers, and commit messages in English.
  Reviewer-facing docs (`DECISIONS.md`) may be in Portuguese.

## Commit message convention (for suggestions only — you do not commit)

Conventional Commits, in English: `type: short imperative description`.
Types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `build`, `ci`.
The failing-test commit precedes the implementation commit, e.g.:
- `test: add failing test for search 403 without permission`
- `feat: add require_permission auth dependency`

### Suggested-commit checkpoints (you propose, the human commits)

At the end of each meaningful TDD step, STOP and surface a checkpoint instead of moving on:

1. When a new test is written and confirmed **failing (RED)**, stop. Print:
   - a one-line summary of what the test covers and that it fails as expected,
   - a fenced block with the exact suggested command, listing the specific files, e.g.
     ```
     git add <files> && git commit -m "test: add failing test for app factory"
     ```
2. When the implementation makes that test **pass (GREEN)** and `ruff` is clean, stop again
   and print the same kind of block, e.g.
     ```
     git add <files> && git commit -m "feat: add FastAPI app factory"
     ```
3. Do NOT run the command yourself — only print it. Wait for the human to say they have
   committed (or to give the next instruction) before continuing to the next step.
4. List the specific files to stage in the `git add` — never suggest `git add .` or `-A`.
5. Only reach a checkpoint when the repo is in a runnable state (suite green, except the one
   intentionally-red new test in step 1). Never checkpoint on half-written code.

## Tooling notes

- `ruff` config does not exist yet; it must be created (e.g. in `pyproject.toml`) as part of
  the skeleton change before "ruff is clean" can be enforced.
- Run `ruff` (format + lint) before proposing any GREEN checkpoint.

## Definition of done

A feature is done only when its tests are green AND `ruff` is clean. Comment only
non-obvious decisions (explain *why*, not *what*). If you get stuck, document what you
tried — that is worth points.