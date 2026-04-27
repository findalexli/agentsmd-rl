# improve clickhouse-system-queries skill structure

Source: [FrankChen021/datastoria#135](https://github.com/FrankChen021/datastoria/pull/135)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `resources/skills/clickhouse-system-queries/SKILL.md`

## What to add / change

hey @FrankChen021, thanks for building datastoria. really like the structured approach to ClickHouse observability with dedicated system table skills. Kudos on the project! I've just starred it.

ran your clickhouse-system-queries skill through agent evals and spotted a few quick wins that took it from `~70%` to `~100%` performance:

- rewrote description with concrete trigger terms like _system tables, query_log, cluster status, slow queries_ + explicit Use when clause

- added concrete SQL examples for map vs flattened ProfileEvents access + time-bucketed aggregation pattern

- added explicit tool routing guidance for _search_query_log_ vs _execute_sql_ with examples

these were easy changes to bring the skill in line with what **performs well against Anthropic's best practices**. honest disclosure, I work at tessl.io where we build tooling around this. not a pitch, just fixes that were straightforward to make! happy to answer any questions on the changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
