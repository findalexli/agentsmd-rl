# chore: update CLAUDE.md and AGENTS.md

Source: [olimorris/codecompanion.nvim#2956](https://github.com/olimorris/codecompanion.nvim/pull/2956)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

<!-- Please do not alter the structure of this PR template -->

## Description

Update the CLAUDE.md file to point to the AGENTS.md file. This makes CodeCompanion more accessible for users of Opencode etc.

## AI Usage

None

## Related Issue(s)

<!--
  If this PR fixes any issues, please link to the issue here.
  - Fixes #<issue_number>
-->

## Screenshots

<!-- Add screenshots of the changes if applicable, to help visualize the change. -->

## Checklist

- [x] I've read the [contributing](https://github.com/olimorris/codecompanion.nvim/blob/main/CONTRIBUTING.md) guidelines and have adhered to them in this PR
- [x] I confirm that this PR has been majority created by me, and not AI (unless stated in the "AI Usage" section above)
- [x] I've run `make all` to ensure docs are generated, tests pass and [StyLua](https://github.com/JohnnyMorganz/StyLua) has formatted the code
- [ ] _(optional)_ I've added [test](https://github.com/olimorris/codecompanion.nvim/blob/main/CONTRIBUTING.md#testing) coverage for this fix/feature
- [ ] _(optional)_ I've updated the README and/or relevant docs pages

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
