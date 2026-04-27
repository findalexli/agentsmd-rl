# Fix airflow-adapter skill frontmatter

Source: [astronomer/agents#147](https://github.com/astronomer/agents/pull/147)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `astro-airflow-mcp/.claude/skills/airflow-adapter/SKILL.md`

## What to add / change

## Summary

The [Claude skill spec](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) requires `name` and `description` fields in SKILL.md frontmatter. The existing airflow-adapter skill had an unsupported `globs` field and was missing `name`.

**Before:**
```yaml
description: Airflow adapter pattern for v2/v3 API compatibility
globs:
  - src/astro_airflow_mcp/adapters/**
  - src/astro_airflow_mcp/server.py
```

**After:**
```yaml
name: airflow-adapter
description: Airflow adapter pattern for v2/v3 API compatibility. Use when working with adapters, version detection, or adding new API methods that need to work across Airflow 2.x and 3.x.
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
