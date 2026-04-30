# Fix `cosmos-dbt-core/SKILL.md`

Source: [astronomer/agents#122](https://github.com/astronomer/agents/pull/122)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/cosmos-dbt-core/SKILL.md`

## What to add / change

Fix incorrect statements and improve existing descriptions.

The main issues:
- The containerised approaches do not require `manifest.json`
- The first step should be to set the path to the user's dbt project. Parsing it is a second step.
- Watcher also supports dbt Fusion
- Missing `WATCHER_KUBERNETES`
- Missing a common use case of instantiating Cosmos operators directly

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
