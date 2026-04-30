# Apply safeguards and versioning to Agent Skills

Source: [oracle/netsuite-suitecloud-sdk#1011](https://github.com/oracle/netsuite-suitecloud-sdk/pull/1011)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/agent-skills/netsuite-ai-connector-instructions/SKILL.md`
- `packages/agent-skills/netsuite-sdf-roles-and-permissions/SKILL.md`
- `packages/agent-skills/netsuite-uif-spa-reference/SKILL.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
