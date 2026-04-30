# Add dashboard catalog and schema params to asset-bundles skill

Source: [databricks-solutions/ai-dev-kit#40](https://github.com/databricks-solutions/ai-dev-kit/pull/40)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `databricks-skills/asset-bundles/SKILL.md`

## What to add / change

- Add support for [dashboard catalog and schema parameterization](https://docs.databricks.com/aws/en/dev-tools/bundles/examples#dashboard-dataset), which is available starting in [CLI 0.281.0](https://github.com/databricks/cli/releases/tag/v0.281.0).
- Include note in skill indicating starting version.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
