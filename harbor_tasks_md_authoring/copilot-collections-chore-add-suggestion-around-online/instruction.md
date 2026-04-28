# chore: add suggestion around online indexing

Source: [TheSoftwareHouse/copilot-collections#19](https://github.com/TheSoftwareHouse/copilot-collections/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/sql-and-database/SKILL.md`

## What to add / change

## Summary

  - Add guidance on using non-blocking index operations (CONCURRENTLY in PostgreSQL, online indexing in other engines) to the SQL & Database skill
  - Covers syntax examples, migration framework gotchas, failure handling, and when it's safe to skip

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
