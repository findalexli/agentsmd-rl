# docs(agents): fix incoherences in AGENTS.md

Source: [DataDog/dd-trace-py#16574](https://github.com/DataDog/dd-trace-py/pull/16574)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- Moved "Check and remove unexpected prints" from the `Never` list to the `Always` list (item 7), where it logically belongs
- Fixed the `Initial Setup for AI Assistants` numbered list that incorrectly started at `2.` instead of `1.`
- Added missing `releasenote` skill documentation to match the available skills

## Test plan

- [ ] No code changes — documentation-only fix
- [ ] Verify AGENTS.md reads consistently end-to-end

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
