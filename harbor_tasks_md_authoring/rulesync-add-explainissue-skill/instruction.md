# Add explain-issue skill

Source: [dyoshikawa/rulesync#1441](https://github.com/dyoshikawa/rulesync/pull/1441)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.rulesync/skills/explain-issue/SKILL.md`

## What to add / change

## Summary
- add a new `explain-issue` official skill under `.rulesync/skills/`
- guide agents to explain issue background and proposed solutions from issue details and comments
- handle missing issue arguments and unspecified solutions explicitly

## Test plan
- `pnpm cicheck`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
