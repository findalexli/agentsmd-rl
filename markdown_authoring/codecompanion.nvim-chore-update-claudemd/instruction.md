# chore: update CLAUDE.md

Source: [olimorris/codecompanion.nvim#2171](https://github.com/olimorris/codecompanion.nvim/pull/2171)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Description

Cleaning it up.

## Checklist

- [x] I've read the [contributing](https://github.com/olimorris/codecompanion.nvim/blob/main/CONTRIBUTING.md) guidelines and have adhered to them in this PR
- [ ] I've added [test](https://github.com/olimorris/codecompanion.nvim/blob/main/CONTRIBUTING.md#testing) coverage for this fix/feature
- [ ] I've run `make all` to ensure docs are generated, tests pass and my formatting is applied
- [ ] _(optional)_ I've updated `CodeCompanion.has` in the [init.lua](https://github.com/olimorris/codecompanion.nvim/blob/main/lua/codecompanion/init.lua#L239) file for my new feature
- [ ] _(optional)_ I've updated the README and/or relevant docs pages

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
