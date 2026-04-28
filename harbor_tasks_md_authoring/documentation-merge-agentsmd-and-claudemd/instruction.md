# Merge AGENTS.md and CLAUDE.md

Source: [strapi/documentation#3044](https://github.com/strapi/documentation/pull/3044)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

This PR consolidates CLAUDE.md and AGENTS.md into a single source of truth, and adds Copilot instructions.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
