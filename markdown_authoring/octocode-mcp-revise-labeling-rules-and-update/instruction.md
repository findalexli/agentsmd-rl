# Revise labeling rules and update guidelines for findings

Source: [bgauryy/octocode-mcp#386](https://github.com/bgauryy/octocode-mcp/pull/386)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/octocode-pull-request-reviewer/SKILL.md`

## What to add / change

Updated guidelines to prohibit using '#' notation for findings in PR review

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
