# chore: Update cursor rules

Source: [getsentry/spotlight#1193](https://github.com/getsentry/spotlight/pull/1193)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/.cursor/rules/routing.mdc`
- `.cursor/rules/general-guidelines.mdc`
- `packages/spotlight/.cursor/rules/overview.mdc`
- `packages/spotlight/src/electron/.cursor/rules/electron.mdc`
- `packages/spotlight/src/server/.cursor/rules/server.mdc`
- `packages/spotlight/src/server/cli/.cursor/rules/cli.mdc`
- `packages/spotlight/src/server/mcp/.cursor/rules/mcp.mdc`
- `packages/spotlight/src/ui/.cursor/rules/ui.mdc`
- `packages/website/.cursor/rules/website.mdc`

## What to add / change

Our cursor rules were outdated.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
