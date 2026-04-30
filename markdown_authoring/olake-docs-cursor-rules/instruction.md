# docs: cursor rules

Source: [datazip-inc/olake#822](https://github.com/datazip-inc/olake/pull/822)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/olake.mdc`

## What to add / change

# Description

Adds a comprehensive Cursor AI rules file (`.cursor/rules/olake.mdc`) that provides project context, coding conventions, and end-to-end testing guidance for the OLake codebase. This enables Cursor to understand the project architecture and automatically validate any code change through a documented e2e test procedure.

Key contents:
- Project overview, repository layout, and package map
- Iceberg destination write modes (legacy vs arrow) and JAR detection/staleness warnings
- Build & run instructions (`build.sh`, `go build`, Makefile)
- Coding conventions (formatting, logging, error handling, concurrency patterns)
- **Full end-to-end testing procedure** — Postgres source → Iceberg destination (JDBC catalog on MinIO), with Spark verification
- File-change-to-test mapping table so Cursor knows what to test for any given change
- Integration test commands per driver

## Type of change

- [x] New feature (non-breaking change which adds functionality)

# How Has This Been Tested?

The e2e testing instructions in the rules file were validated end-to-end:

- [x] **Full-load sync (Postgres → Iceberg):** Created Postgres container with WAL logical replication, 5-row test table, ran `discover` → `sync` (full_refresh) → queried Iceberg via `spark-sql`. Verified 5 rows with correct data (Alice, Bob, Charlie, Diana, Eve).
- [x] **CDC sync (Postgres → Iceberg):** Switched `sync_mode` to `cdc`, ran sync with `--timeout 30`. Backfill completed + WAL repli

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
