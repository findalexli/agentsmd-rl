# docs: add AGENTS.md for AI contributor onboarding

Source: [TooTallNate/nx.js#206](https://github.com/TooTallNate/nx.js/pull/206)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds an `AGENTS.md` file documenting codebase patterns, conventions, and architecture so that AI agents (sub-agents, copilots, etc.) can quickly get up to speed when contributing.

Covers:
- Native module pattern (C side + JS side)
- Async work queue pattern
- Build system & cross-compilation notes
- Changeset rules (patch only, no semver yet)
- Example app structure
- Common pitfalls

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
