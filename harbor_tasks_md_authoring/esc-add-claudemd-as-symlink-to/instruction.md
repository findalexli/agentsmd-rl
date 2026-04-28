# Add CLAUDE.md as symlink to AGENTS.md

Source: [pulumi/esc#636](https://github.com/pulumi/esc/pull/636)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds `CLAUDE.md` as a symlink to the existing `AGENTS.md`.
- Claude Code only reads `CLAUDE.md` natively ([docs](https://code.claude.com/docs/en/memory.md#agents-md)), so without this file Claude Code sessions miss the repo's agent context.
- Symlinking (vs. duplicating or using an `@AGENTS.md` import file) keeps the two files in lockstep with no maintenance overhead.

## Test plan
- [x] Confirm `CLAUDE.md` resolves to `AGENTS.md` content (`cat CLAUDE.md`).
- [x] Open the repo in Claude Code and verify the agent picks up `AGENTS.md` instructions via `CLAUDE.md`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
