# chore: Adding AGENTS.md

Source: [databricks/dbt-databricks#1183](https://github.com/databricks/dbt-databricks/pull/1183)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

### Description

Adds AGENTS.md to improve developing this project with AI

### Checklist

- [ ] I have run this code in development and it appears to resolve the stated issue
- [ ] This PR includes tests, or tests are not required/relevant for this PR
- [ ] I have updated the `CHANGELOG.md` and added information about my change to the "dbt-databricks next" section.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
