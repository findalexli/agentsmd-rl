# feat: add clickhouse migration guide to AGENT.md

Source: [PostHog/posthog#39624](https://github.com/PostHog/posthog/pull/39624)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `posthog/clickhouse/migrations/AGENTS.md`

## What to add / change

## Problem

`ON CLAUSE` is causing issues, let's clean the database of it

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
