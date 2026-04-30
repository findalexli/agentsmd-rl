# Add URL quoting reminder to SKILL.md

Source: [firecrawl/cli#13](https://github.com/firecrawl/cli/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/firecrawl-cli/SKILL.md`

## What to add / change

URLs with `?` and `&` need quoting to avoid shell glob/special character interpretation.

Without the reminder, Claude Code sometimes fails on URLs with query params:

```
⏺ Bash(firecrawl scrape https://docs.datadoghq.com/integrations/sql-server/?tab=host -o .firecrawl/datadog-sql-server-integration.md)
  ⎿  Error: Exit code 1
     (eval):1: no matches found: https://docs.datadoghq.com/integrations/sql-server/?tab=host
```

After quoting it works:

```
⏺ Bash(firecrawl scrape "https://docs.datadoghq.com/integrations/sql_server/?tab=host" -o .firecrawl/datadog-sql-server-integration.md)
  ⎿  (No content)
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
