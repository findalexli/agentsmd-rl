# feat: Add AGENTS.md for project context

Source: [kwaroran/Risuai#1054](https://github.com/kwaroran/Risuai/pull/1054)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

# PR Checklist
- [ ] Have you checked if it works normally in all models? *Ignore this if it doesn't use models.*
- [ ] Have you checked if it works normally in all web, local, and node hosted versions? If it doesn't, have you blocked it in those versions?
- [ ] Have you added type definitions?

# Description
This PR adds an AGENTS.md file to provide context and instructions for code agents working on this project.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
