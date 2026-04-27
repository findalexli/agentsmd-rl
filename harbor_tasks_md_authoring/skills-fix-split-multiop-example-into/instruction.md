# fix: split multi-op example into one-op-per-file

Source: [apollographql/skills#46](https://github.com/apollographql/skills/pull/46)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/apollo-mcp-server/SKILL.md`

## What to add / change

The apollo-mcp-server SKILL.md had an example showing two operations (a query and a mutation) in a single `.graphql` file. The server requires exactly one operation per file and rejects files with multiple operations with a "Too many operations" error. This split the example into two separate files (`GetUser.graphql` and `CreateUser.graphql`) and added an explicit note about the one-operation-per-file constraint so users don't hit the same error.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
