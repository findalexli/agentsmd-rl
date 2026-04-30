# chore: add AGENTS.md symlink to CLAUDE.md

Source: [leanprover/lean4#13461](https://github.com/leanprover/lean4/pull/13461)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This PR adds an `AGENTS.md` symlink to `.claude/CLAUDE.md` so Codex-style repository instructions can resolve to the same checked-in guidance Claude Code already uses.

This keeps the repository's agent-facing instructions in one place instead of maintaining separate copies for different tools. Previous Codex runs did not automatically pick up the existing `.claude/CLAUDE.md` guidance, which caused avoidable drift in PR formatting and workflow behavior.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
