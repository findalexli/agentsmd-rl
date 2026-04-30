# fix: add trigger phrases to skill descriptions per Anthropic's official guide

Source: [databricks-solutions/ai-dev-kit#317](https://github.com/databricks-solutions/ai-dev-kit/pull/317)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `databricks-skills/databricks-config/SKILL.md`
- `databricks-skills/databricks-docs/SKILL.md`
- `databricks-skills/databricks-lakebase-autoscale/SKILL.md`
- `databricks-skills/databricks-lakebase-provisioned/SKILL.md`
- `databricks-skills/databricks-spark-structured-streaming/SKILL.md`

## What to add / change

## Summary

- Add "Use when" clauses and specific trigger keywords to 5 skill descriptions that were missing them
- Follows the `[What it does] + [When to use it] + [trigger phrases]` structure recommended by [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) (p.10-12)
- Consistent with well-structured descriptions already in the repo (e.g., `databricks-iceberg`, `databricks-app-python`, `databricks-spark-declarative-pipelines`)

### Skills updated

| Skill | Change |
|-------|--------|
| `databricks-docs` | Added "Use when" with scenarios (lookup unfamiliar features, docs on APIs) |
| `databricks-config` | Added trigger keywords ("switch workspace", "databrickscfg", "databricks auth") |
| `databricks-spark-structured-streaming` | Added specific keywords (Kafka, RTM, watermark, checkpoint, triggers) |
| `databricks-lakebase-autoscale` | Added "Use when" with scenarios (projects, branching, scale-to-zero, reverse ETL) |
| `databricks-lakebase-provisioned` | Added "Use when" with scenarios (instances, Apps, reverse ETL, agent memory) |

Closes #316

## Test plan

- [x] All descriptions under 1024 character limit
- [x] Consistent with existing description patterns across the repo
- [ ] Verify skill triggering on relevant queries

This pull request was AI-assisted by Claude Code.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
