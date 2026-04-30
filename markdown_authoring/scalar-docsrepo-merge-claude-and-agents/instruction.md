# docs(repo): merge CLAUDE and AGENTS guides

Source: [scalar/scalar#8961](https://github.com/scalar/scalar/pull/8961)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `CLAUDE.md`

## What to add / change

<!-- CURSOR_AGENT_PR_BODY_BEGIN -->
## Problem

Agent guidance existed in both `CLAUDE.md` and `AGENTS.md`, which risked drift and duplicated maintenance.

## Solution

- Merged the two guides into a single canonical `AGENTS.md` while preserving unique content from both files.
- Kept architecture/build/tooling/type-style/testing/OpenAPI terminology guidance from `CLAUDE.md`.
- Kept PR workflow, ticket-linking, changeset, and visual artifact guidance from `AGENTS.md`.
- Replaced `CLAUDE.md` with a symlink to `AGENTS.md` for backward compatibility.

## Testing

- `rg -n "^## (Project Overview|Commands|Architecture|Code Standards|OpenAPI Terminology|PR Requirements|Visual Testing)$|^### (Workspace Layout|Build System|Key Package Relationships|Dependency Versioning|Tooling Split|TypeScript|Vue Components|Biome Lint Rules to Know|Semantic PR titles|Ticket and issue linking|Changesets|Pre-PR command checklist)$" AGENTS.md`
- `test -L CLAUDE.md && test "$(readlink CLAUDE.md)" = "AGENTS.md" && rg -n "^# AGENTS.md - AI Agent Guide for Scalar$" CLAUDE.md`
- `pnpm format`
- `pnpm knip` (fails due to existing unresolved imports in `integrations/nuxt`, unrelated to this docs-only change)
- `pnpm changeset status`

## Checklist

- [x] I explained why the change is needed.
- [ ] I added a changeset. _(Not needed for docs/symlink-only change.)_
- [ ] I added tests. _(Not applicable; verified via doc and symlink checks plus repository checks.)_
- [x] I updated the documentation.
<!-- CURSOR_A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
