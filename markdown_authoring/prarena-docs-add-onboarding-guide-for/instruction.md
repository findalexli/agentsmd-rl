# docs: add onboarding guide for new agents

Source: [aavetis/PRarena#59](https://github.com/aavetis/PRarena/pull/59)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- add a repository-wide AGENTS.md that documents the complete onboarding checklist for tracking new coding agents
- capture required GitHub queries, data pipeline updates, template changes, and regeneration steps to avoid regressions when adding agents such as Jules

## Testing
- not run (docs only)


------
https://chatgpt.com/codex/tasks/task_b_68e30d57a6b88332814b6e96211bb30a

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
