# Rename CLAUDE.md to AGENTS.md with Symlink

## Problem

The Next.js repository currently has a `CLAUDE.md` file containing agent instructions. However, some agent tools look for `AGENTS.md` instead. Both files need to work correctly:
- Tools looking for `AGENTS.md` should find the full agent instructions
- Tools looking for `CLAUDE.md` should still work (backwards compatibility)

Additionally, both filenames need to be ignored by the alex lint tool to avoid linting issues.

## Expected Behavior

After the change:
- `AGENTS.md` should exist as a regular file containing the full agent instructions
- `CLAUDE.md` should still be readable and return the same content as `AGENTS.md`
- `.alexignore` should list both `AGENTS.md` and `CLAUDE.md`

## Verification

The agent instructions file should contain these sections:
- "# Next.js Development Guide" header
- "Git Workflow" section
- "Build Commands" section
- "Testing" section
- "Linting and Types" section

The file should be substantial (more than 5000 characters).

`.alexignore` should contain the strings `AGENTS.md` and `CLAUDE.md` on separate lines.

## Files to Look At

- `CLAUDE.md` — currently contains the full agent instructions
- `.alexignore` — currently only ignores `CLAUDE.md`

The content that needs to be preserved is the full content currently in `CLAUDE.md`.