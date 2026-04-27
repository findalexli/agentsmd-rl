# Skill: Airflow HITL

Source: [astronomer/agents#95](https://github.com/astronomer/agents/pull/95)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/airflow-hitl/SKILL.md`

## What to add / change

New Skill: 
 - airflow-hitl: Human-in-the-loop operators (ApprovalOperator, HITLOperator, HITLBranchOperator, HITLEntryOperator) for Airflow 3.1+

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
