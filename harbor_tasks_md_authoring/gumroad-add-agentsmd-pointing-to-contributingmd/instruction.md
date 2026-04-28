# Add AGENTS.md pointing to CONTRIBUTING.md

Source: [antiwork/gumroad#4685](https://github.com/antiwork/gumroad/pull/4685)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

AGENTS.md is the universal standard read by Codex, Cursor, Copilot, and other coding agents. Points to CONTRIBUTING.md so all agents automatically follow the same guidelines.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
