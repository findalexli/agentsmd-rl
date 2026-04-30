# Add CLAUDE.md symlink, use mise, and simplify AGENTS.md

Source: [pulumi/pulumi#22228](https://github.com/pulumi/pulumi/pull/22228)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `pkg/AGENTS.md`
- `sdk/go/AGENTS.md`
- `sdk/nodejs/AGENTS.md`
- `sdk/python/AGENTS.md`

## What to add / change

## Summary
- Symlink `CLAUDE.md` → `AGENTS.md` so Claude Code picks up agent instructions
- Prefix all `make` commands with `mise exec --` to ensure correct tool versions from `.mise.toml` are used
- Apply progressive disclosure: move SDK-specific and pkg-specific instructions into subdirectory `AGENTS.md` files (`pkg/`, `sdk/nodejs/`, `sdk/python/`, `sdk/go/`)

## Test plan
- [x] Verify `CLAUDE.md` symlink resolves correctly
- [x] Confirm Claude Code loads instructions from `CLAUDE.md`
- [x] Spot-check that `mise exec -- make build` works as documented

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
