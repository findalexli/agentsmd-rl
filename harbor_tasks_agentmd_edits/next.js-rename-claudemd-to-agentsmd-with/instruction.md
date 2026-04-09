# Rename CLAUDE.md to AGENTS.md with Symlink

## Problem

The Next.js repository currently uses `CLAUDE.md` as the main agent instruction file. However, we want to:
1. Rename it to `AGENTS.md` to benefit more coding agents (not just Claude)
2. Keep `CLAUDE.md` as a symlink to `AGENTS.md` for backwards compatibility with Claude Code

Additionally, both files need to be added to `.alexignore` to avoid linting issues.

## Expected Behavior

After the change:
- `AGENTS.md` should exist with the full agent instructions content
- `CLAUDE.md` should be a symbolic link pointing to `AGENTS.md`
- `.alexignore` should include both `AGENTS.md` and `CLAUDE.md`

## Files to Look At

- `CLAUDE.md` — currently contains the full agent instructions (will become a symlink)
- `.alexignore` — currently only ignores `CLAUDE.md`, needs to also ignore `AGENTS.md`
- Need to create `AGENTS.md` with the content from the original `CLAUDE.md`

## Implementation Notes

- On Unix systems, use `ln -s AGENTS.md CLAUDE.md` to create the symlink
- The symlink must correctly resolve (e.g., `cat CLAUDE.md` should show the same content as `AGENTS.md`)
- `.alexignore` should list both files on separate lines
