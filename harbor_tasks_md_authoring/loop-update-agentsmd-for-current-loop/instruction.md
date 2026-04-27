# Update AGENTS.md for current loop workflows

Source: [axeldelafosse/loop#49](https://github.com/axeldelafosse/loop/pull/49)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- correct the `loop` default behavior to reflect paired interactive `--tmux` startup
- document `loop dashboard` as the live panel entrypoint
- add current contributor commands for global install aliases and patch releases
- note the existing `PLAN.md` fallback when options are passed without a prompt

## Testing
- Not run (not requested)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
