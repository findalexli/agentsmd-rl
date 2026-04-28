# [docs] Add AGENTS.md for AI coding agents

Source: [cloudflare/workers-sdk#11716](https://github.com/cloudflare/workers-sdk/pull/11716)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Creates AGENTS.md with comprehensive guidance for AI coding agents working in this repository:
- Build/test/lint commands including single test execution
- Updated architecture overview with current package list
- Code style rules from ESLint config
- Testing strategy and changeset requirements

Simplifies CLAUDE.md to reference AGENTS.md, making the guidance agent-agnostic.

---

- Tests
  - [ ] Tests included/updated
  - [x] Tests not necessary because: documentation only
- Public documentation
  - [ ] Cloudflare docs PR(s):
  - [x] Documentation not necessary because: internal developer guidance only
- Wrangler V3 Backport
  - [ ] Wrangler PR:
  - [x] Not necessary because: not a Wrangler change

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
