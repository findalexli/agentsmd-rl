# feat(skills): Update testing-dags to use af CLI

Source: [astronomer/agents#75](https://github.com/astronomer/agents/pull/75)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/testing-dags/SKILL.md`

## What to add / change

## Summary

Migrates the `testing-dags` skill from MCP tool syntax to the `af` CLI, maintaining consistency with the `airflow` skill.

## Changes

- **Add CLI preamble**: New "Running the CLI" section with `uvx --from astro-airflow-mcp@latest af` instruction
- **Replace MCP tools with `af` commands**:
  | MCP Tool | `af` Command |
  |----------|--------------|
  | `trigger_dag_and_wait()` | `af runs trigger-wait` |
  | `trigger_dag()` | `af runs trigger` |
  | `get_dag_run()` | `af runs get` |
  | `diagnose_dag_run()` | `af runs diagnose` |
  | `get_task_logs()` | `af tasks logs` |
  | `list_import_errors` | `af dags errors` |
  | `get_dag_details()` | `af dags get` |
  | `explore_dag()` | `af dags explore` |
  | `list_connections` | `af config connections` |
  | `list_variables` | `af config variables` |
- **Remove obsolete sections**: "CLI vs MCP Quick Reference" warning section removed (no longer relevant)
- **Rename reference table**: "MCP Tools Quick Reference" → "CLI Quick Reference"
- **Update all code examples**: Changed from MCP function syntax to bash commands

## Design Rationale

The MCP server is being phased out in favor of the `af` CLI which provides the same functionality with better UX (no MCP configuration needed, just `uvx`). This change aligns the testing-dags skill with the already-updated airflow skill.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
