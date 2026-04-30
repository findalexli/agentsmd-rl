# chore(ai): add python/ui code style claude rules

Source: [jentic/jentic-mini#283](https://github.com/jentic/jentic-mini/pull/283)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`
- `.claude/rules/python-code-style.md`
- `.claude/rules/ui-code-style.md`

## What to add / change

## Summary
- Extract Python and UI code-style guidance from `.claude/CLAUDE.md` into two path-scoped rule files under `.claude/rules/`.
- `python-code-style.md` triggers on `**/*.py` — anchors formatting in PEP 8 (via `ruff format`), cites the enforced ruff rule subset from `pyproject.toml`, and flags PEP 585 / PEP 604 for modern type syntax.
- `ui-code-style.md` triggers on `ui/**/*.ts(x)` — groups rules by Components / Styling / Imports / Generated code, each traceable to an ESLint rule in `ui/eslint.config.js` or a convention already in `CLAUDE.md`.
- `CLAUDE.md` keeps architecture and reference content (component inventory, codegen workflow, token recipe); style rules (what to do / avoid) now live in the rule files so they auto-surface only when editing matching files.

## Test plan
- [x] Open a `.py` file and confirm `python-code-style.md` loads into Claude's context
- [x] Open a file under `ui/**/*.ts` or `ui/**/*.tsx` and confirm `ui-code-style.md` loads
- [x] Skim `CLAUDE.md` end-to-end to verify no dangling references to removed sections

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
