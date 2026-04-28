# 🤖 Fix broken symlinks for AGENTS.md and CLAUDE.md

Source: [coder/mux#66](https://github.com/coder/mux/pull/66)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Both `AGENTS.md` and `CLAUDE.md` symlinks in the root were pointing to `docs/src/AGENTS.md` which doesn't exist. This caused the symlinks to be broken.

This PR updates both symlinks to correctly point to `docs/AGENTS.md` where the actual agent instructions file is located.

**Changes:**
- Fixed `AGENTS.md` symlink: `docs/src/AGENTS.md` → `docs/AGENTS.md`
- Fixed `CLAUDE.md` symlink: `docs/src/AGENTS.md` → `docs/AGENTS.md`

_Generated with `cmux`_

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
