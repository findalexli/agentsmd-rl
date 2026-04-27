# Add blueprint skill for template-based DAG authoring

Source: [astronomer/agents#150](https://github.com/astronomer/agents/pull/150)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/blueprint/SKILL.md`

## What to add / change

## Summary

- Adds new `blueprint` skill for working with the [airflow-blueprint](https://github.com/astronomer/blueprint) package
- Enables platform teams to define reusable Airflow task group templates with Pydantic validation
- Supports composing DAGs from YAML without writing Airflow code

## References

- Blueprint repo: https://github.com/astronomer/blueprint
- Docs PR: https://github.com/astronomer/docs/pull/6339

## Test plan

- [ ] Verify skill loads correctly with `claude plugin install`
- [ ] Test skill triggers on relevant user queries
- [ ] Validate CLI commands work as documented

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
