# docs: update AGENTS.md to reflect current project state (Vibe Kanban)

Source: [BloopAI/vibe-kanban#2768](https://github.com/BloopAI/vibe-kanban/pull/2768)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `frontend/AGENTS.md`

## What to add / change

## Summary

The root `AGENTS.md` (and its mirror `CLAUDE.md`) had drifted from the actual project state — missing crates, undocumented type generation pipelines, and no references to sub-directory agent guides. This PR brings the documentation in sync and adds a formatting directive for AI agents.

## Changes

### Project structure accuracy
- Added 3 missing crates to the project structure: `git` (Git operations), `api-types` (shared API types for local + remote), `review` (PR review tool)
- Updated `shared/` description to include `remote-types.ts` and `schemas/` directory

### Sub-directory guide references
- Added links to `docs/AGENTS.md` (Mintlify writing guidelines) and `frontend/AGENTS.md` (design system styling)
- Renamed `frontend/CLAUDE.md` → `frontend/AGENTS.md` for consistency with other sub-directory guides (`docs/AGENTS.md`, `crates/remote/AGENTS.md`)

### Remote type generation pipeline
- Documented `pnpm run remote:generate-types` for regenerating `shared/remote-types.ts`, alongside the existing local type generation docs

### Build commands & task completion
- Added `pnpm run format` and `pnpm run lint` to the build commands section (previously undocumented)
- Added a new "Before Completing a Task" section requiring agents to run `pnpm run format` before finishing work

## Why

AI coding agents rely on `AGENTS.md` / `CLAUDE.md` to understand the project structure and workflows. Outdated documentation leads to agents missing crates, not knowing about the remot

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
