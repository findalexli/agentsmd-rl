# docs(repo): use symbolic links for AGENTS.md files

Source: [taikoxyz/taiko-mono#20251](https://github.com/taikoxyz/taiko-mono/pull/20251)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `Agents.md`
- `packages/protocol/AGENTS.md`
- `packages/protocol/Agents.md`

## What to add / change

## Summary
- Convert `Agents.md` files from redirect files to symbolic links pointing to `CLAUDE.md`
- Eliminates redundant content and maintenance overhead
- Maintains compatibility for tools expecting either filename

## Changes
- Root: `Agents.md` → `AGENTS.md` (symbolic link to `CLAUDE.md`)  
- Protocol: `packages/protocol/Agents.md` → `packages/protocol/AGENTS.md` (symbolic link to `CLAUDE.md`)

## Test plan
- [x] Verify symbolic links work correctly
- [x] Confirm both `AGENTS.md` and `CLAUDE.md` provide same content
- [x] Test file access in both directories

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
