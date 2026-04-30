# chore: optimize CLAUDE.md

Source: [CartoDB/analytics-toolbox-core#596](https://github.com/CartoDB/analytics-toolbox-core/pull/596)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/bigquery.md`
- `.claude/rules/ci-cd.md`
- `.claude/rules/cloud-sql-testing.md`
- `.claude/rules/databricks.md`
- `.claude/rules/extending-clouds.md`
- `.claude/rules/function-dev.md`
- `.claude/rules/gateway.md`
- `.claude/rules/oracle.md`
- `.claude/rules/packaging.md`
- `.claude/rules/postgres.md`
- `.claude/rules/redshift.md`
- `.claude/rules/snowflake.md`
- `.claude/rules/testing.md`
- `.claude/rules/versioning.md`
- `CLAUDE.md`

## What to add / change

# Description

Trim CLAUDE.md from ~1300 to 57 lines by extracting detailed content into 13 path-scoped rule files in .claude/rules/ that load on demand.

New rule files:
- Cloud-specific: bigquery, snowflake, redshift, postgres, databricks, oracle
- Cross-cutting: cloud-sql-testing, versioning, testing, function-dev, gateway, ci-cd, extending-clouds

Oracle rule enriched with PL/SQL patterns, type mapping, and native H3 function details from design docs.

## Type of change

- Refactor
- Documentation

# Basic checklist

- Good PR name
- Shortcut link
- Just one issue per PR
- GitHub labels
- Proper status & reviewers
- Tests
- Documentation

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
