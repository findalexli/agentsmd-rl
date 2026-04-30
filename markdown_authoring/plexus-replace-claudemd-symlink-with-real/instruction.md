# Replace CLAUDE.md symlink with real file pointing to AGENTS.md

Source: [mcowger/plexus#288](https://github.com/mcowger/plexus/pull/288)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `CLAUDE.md`

## What to add / change

The symlink caused claude-code-action to fail during its security
restore step (ENOENT when recreating the symlink on the runner).

https://claude.ai/code/session_01LMDo1cgVuUia2whpSYuFSP

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
