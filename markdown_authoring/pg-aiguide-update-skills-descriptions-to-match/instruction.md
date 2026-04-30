# Update skills descriptions to match Claude best practices

Source: [timescale/pg-aiguide#75](https://github.com/timescale/pg-aiguide/pull/75)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/design-postgres-tables/SKILL.md`
- `skills/find-hypertable-candidates/SKILL.md`
- `skills/migrate-postgres-tables-to-hypertables/SKILL.md`
- `skills/pgvector-semantic-search/SKILL.md`
- `skills/postgres-hybrid-text-search/SKILL.md`
- `skills/setup-timescaledb-hypertables/SKILL.md`

## What to add / change

# Skill Descriptions Update

This PR improves skill descriptions to increase trigger accuracy and ensure Claude selects the appropriate skill for user requests.

## Summary of Changes

- Added explicit "Trigger when user asks to:" conditions for all skills
- Added keyword lists matching user vocabulary
- Added disambiguation ("Do NOT use for:") where skills overlap
- Added prerequisites and cross-references between related skills
- Standardized description format across all skills

---

## Updated Descriptions

### 1. `setup-timescaledb-hypertables`

**Old:**
```
Step-by-step instructions for designing table schemas and setting up TimescaleDB with hypertables, indexes, compression, retention policies, and continuous aggregates. Instructions for selecting: partition columns, segment_by columns, order_by columns, chunk time interval, real-time aggregation.
```

**New:**
```
Use this skill when creating database schemas or tables for TimescaleDB, TigerData, or Tiger Cloud, especially for time-series, IoT, metrics, events, or log data.

**Trigger when user asks to:**
- Create or design SQL schemas/tables AND TimescaleDB/TigerData/Tiger Cloud is available
- Set up hypertables, compression, retention policies, or continuous aggregates
- Configure partition columns, segment_by, order_by, or chunk intervals
- Optimize time-series database performance or storage
- Create tables for sensors, metrics, telemetry, events, or transaction logs

**Keywords:*

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
