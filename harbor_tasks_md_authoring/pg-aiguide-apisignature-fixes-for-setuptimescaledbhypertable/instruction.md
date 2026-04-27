# API/Signature fixes for setup-timescaledb-hypertables

Source: [timescale/pg-aiguide#69](https://github.com/timescale/pg-aiguide/pull/69)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/setup-timescaledb-hypertables/SKILL.md`

## What to add / change

This PR addresses multiple issues encountered while using `setup-timescaledb-hypertables` 

## Approach

Attempt to complete tasks at https://github.com/timescale/TigerData-Workshops/tree/main/Agentic-Postgres-Workshop 

Prompt to uncover the issues:

```
Goal for this session is to debug Tiger skills and make sure it returns accurate results.

I want you to remember what SQL queries you created and ran and why. If the query was invalid, trace
the invalid syntax to the source (either your own knowledge or data received from the skill). My goal is
to make sure the skill contains the relevant and correct information.

use skill at skills/setup-timescaledb-hypertables/SKILL.md

  1. Look at the two CSV files in this directory
  2. Use Tiger service postgres://tsdbadmin:XXXXXXX@mxdjwp5a5k.ocssgijfrc.tsdb.cloud.timescale.com:35695/tsdb?sslmode=require
  3. Using Tiger best practices, create an optimized schema for the data
  4. Save the schema to `schema.sql`
  5. Apply schema to the newly created database
  6. Load data from CSV files
```

## Issues Encountered and Resolutions

### Issue 1: Incorrect API Signature for add_continuous_aggregate_policy
**Source**: Tiger skill documentation (setup-timescaledb-hypertables/SKILL.md:263-275)

**Tiger Skill Suggested**:
```sql
SELECT add_continuous_aggregate_policy('sensor_data_hourly',
    end_offset => INTERVAL '15 minutes',
    schedule_interval => INTERVAL '15 minutes');
```

**Error Encountered**

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
