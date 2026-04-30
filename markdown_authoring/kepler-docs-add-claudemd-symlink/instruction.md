# docs: add CLAUDE.md symlink

Source: [sustainable-computing-io/kepler#2364](https://github.com/sustainable-computing-io/kepler/pull/2364)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Creates a symbolic link CLAUDE.md pointing to the AGENT.md to enable CLAUDE.md references in Claude code.

Claude code specifically looks for CLAUDE.md file, and using a symlin avoids content duplication whole keeping AGENTS.md as the source of truth.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
