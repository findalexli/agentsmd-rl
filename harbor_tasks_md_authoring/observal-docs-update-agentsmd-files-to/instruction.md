# docs: update AGENTS.md files to reflect current codebase

Source: [BlazeUp-AI/Observal#505](https://github.com/BlazeUp-AI/Observal/pull/505)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `ee/AGENTS.md`
- `web/AGENTS.md`

## What to add / change

## Purpose / Description
The root `AGENTS.md`, `web/AGENTS.md`, and `ee/AGENTS.md` were outdated or missing. Additionally, there was no `web/ee/` directory to house enterprise-only frontend code, despite 8+ backend enterprise features with no frontend UI.

## Fixes
* N/A — housekeeping

## Approach

### AGENTS.md updates

**Root AGENTS.md** (284 → 372 lines):
- Docker services: 7 → 11 (added init, lb, prometheus, grafana)
- Tests: 526 across 18 files → 1,429 across 52 files
- Web route groups: 3 → 4 (added `(user)` for user-scoped trace views)
- Added 6 missing API routes, 5 models, 18 services, 2 CLI commands
- Added implementation notes for alerts/webhooks, JWT/JWKS, secrets redaction, endpoint discovery
- Updated IDE support to explicitly list all 8 IDEs

**web/AGENTS.md** (6 → 88 lines):
- Was just a Next.js agent-rules warning banner — now documents the full frontend stack, route group tree, component directories, all lib/hooks files, commands, and conventions

**ee/AGENTS.md** (new, 88 lines):
- Enterprise edition context: how it loads, config validation, audit logging (8 event types, ClickHouse storage, query + CSV export endpoints), SAML/SCIM stubs, plugin placeholder, full directory layout

### web/ee/ scaffold (new)

Created `web/ee/` mirroring the backend `ee/` pattern:
- `LICENSE` — same Observal Enterprise License terms, scoped to `web/ee/`
- `README.md` — documents what belongs here vs core, planned features, constraints
- `AGENTS.md` — maps 8 backend enterprise

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
