# feat: add snowflake-development for Snowflake SQL, pipelines, Cortex AI, and Snowpark

Source: [sickn33/antigravity-awesome-skills#395](https://github.com/sickn33/antigravity-awesome-skills/pull/395)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/snowflake-development/SKILL.md`

## What to add / change

## Summary

Adds a comprehensive Snowflake development skill covering:

- **SQL best practices** — snake_case conventions, stored procedure colon-prefix rule (common "invalid identifier" fix), semi-structured data patterns, MERGE upserts
- **Data pipelines** — Dynamic Tables vs Streams+Tasks decision framework, DT creation syntax and constraints, Snowpipe, pipeline debugging queries
- **Cortex AI** — Function reference with deprecated name warnings, TO_FILE two-argument rule, AI_CLASSIFY vs AI_COMPLETE guidance, Cortex Search, Cortex Agent spec structure
- **Snowpark Python** — Session setup, lazy DataFrames, vectorized UDFs for ML workloads
- **dbt on Snowflake** — Dynamic table materialization, incremental models, Snowflake-specific configs
- **Performance** — Cluster keys, search optimization, warehouse sizing, cost estimation
- **Security** — RBAC patterns, network policies, masking policies, ACCOUNTADMIN auditing
- **Common error patterns** — Quick reference table for the most frequent Snowflake errors and fixes

Risk level: `safe` (read-only development guidance, no system modifications).

No existing skills were modified. No generated registry artifacts included.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

None.

## Quality Bar Checklist ✅

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (check

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
