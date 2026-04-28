# docs: add commit message convention to AGENTS.md

Source: [mizdra/eslint-interactive#411](https://github.com/mizdra/eslint-interactive/pull/411)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Add commit message convention section to AGENTS.md
- Document that commit messages follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) with allowed type prefixes: feat, fix, docs, refactor, test, chore, deps

## Test plan
- [x] Verify the added section is correctly formatted in AGENTS.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
