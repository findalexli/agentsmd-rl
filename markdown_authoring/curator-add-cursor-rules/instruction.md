# Add Cursor rules

Source: [NVIDIA-NeMo/Curator#1294](https://github.com/NVIDIA-NeMo/Curator/pull/1294)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/coding-standards.mdc`
- `.cursor/rules/composite-stage-patterns.mdc`
- `.cursor/rules/executors.mdc`
- `.cursor/rules/modality-structure.mdc`
- `.cursor/rules/pipeline-structure.mdc`
- `.cursor/rules/processing-stage-patterns.mdc`
- `.cursor/rules/resources-configuration.mdc`
- `.cursor/rules/task-patterns.mdc`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
