# Update AGENTS.md with test command and repo workflows

Source: [axeldelafosse/loop#27](https://github.com/axeldelafosse/loop/pull/27)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- add `bun test` to the quick commands list
- document current repo workflows for `PLAN.md`, live panel mode, `--tmux` / `--worktree`, and manual updates
- keep the AGENTS guidance aligned with implemented CLI behavior

## Testing
- Not run (not requested)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
