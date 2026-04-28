# [AI] Improve `AGENTS.md` configuration

Source: [WordPress/wordpress-playground#3275](https://github.com/WordPress/wordpress-playground/pull/3275)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `packages/php-wasm/compile/AGENTS.md`

## What to add / change

## Motivation for the change, related issues
Improve the setup of this repository to enable easier agentic development.

## Implementation details
This PR includes the following changes:
- Rename `CLAUDE.md` to `AGENTS.md`, preserving import from `CLAUDE.md`
- Fix heading, remove stale hardcoded values (version, Node.js/npm requirements)
- Document all top-level package directories and missing NX executors
- Clarify test runner situation (Vitest + Jest) and default branch (`trunk`)
- Add missing entries to Key Files & Directories
- Clean up formatting in Common Commands
- Add nested `AGENTS.md` for `packages/php-wasm/compile/` (build pipeline guidance)
- Add nested `AGENTS.md` for `packages/playground/blueprints/` (step registration pattern)
- Note in root that packages may have their own `AGENTS.md`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
