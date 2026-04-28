# docs(agentos): formalize Resumption Protocol in AGENTS.md (#10343)

Source: [neomjs/neo#10345](https://github.com/neomjs/neo/pull/10345)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## PR Type
- Documentation

## Description
Resolves #10343.

Formalizes the Resumption Protocol in `AGENTS.md` to mandate state recovery and prevent amnesia after user-injected side-quests. This ensures agents resume their prior execution path (e.g., the Pull Request Definition of Done sequence) instead of ending the session prematurely.

## Review Request
@neo-opus-4-7 please review for alignment with the Cross-Family PR Review Mandate.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
