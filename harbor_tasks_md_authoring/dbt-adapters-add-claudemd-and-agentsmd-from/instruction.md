# Add CLAUDE.md and AGENTS.md from skills files

Source: [dbt-labs/dbt-adapters#1790](https://github.com/dbt-labs/dbt-adapters/pull/1790)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary

- Adds `CLAUDE.md` — a comprehensive reference guide distilled from all 7 adapter skills files (base framework, postgres, redshift, snowflake, bigquery, spark, athena), covering monorepo structure, dev workflow, testing patterns, per-adapter features, and catalog integration
- Adds `AGENTS.md` — an operational guide for AI coding agents covering environment setup, build/test commands, where to make changes, macro conventions, security rules, and a PR checklist

## Test plan

- [ ] Review `CLAUDE.md` covers key information from all 7 source skills files
- [ ] Review `AGENTS.md` provides actionable guidance for agent-driven development
- [ ] Confirm no credentials or secrets are included

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
