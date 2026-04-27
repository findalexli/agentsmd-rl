# Use `af` cli in skills

Source: [astronomer/agents#108](https://github.com/astronomer/agents/pull/108)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/airflow/SKILL.md`
- `skills/authoring-dags/SKILL.md`
- `skills/checking-freshness/SKILL.md`
- `skills/debugging-dags/SKILL.md`
- `skills/testing-dags/SKILL.md`
- `skills/tracing-downstream-lineage/SKILL.md`
- `skills/tracing-upstream-lineage/SKILL.md`

## What to add / change

Updates references to airflow mcp tools in airflow skills to reference `af` cli instead.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
