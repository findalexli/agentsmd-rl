# Added AGENTS.md

Source: [OWASP/Nettacker#1128](https://github.com/OWASP/Nettacker/pull/1128)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Proposed change

Adding AGENTS.md file - new standard file  to provide the context and instructions to help AI coding agents (such as OpenAI Code, Google Jules, Cursor) to work on the project. See https://agents.md

## Type of change

<!--
  Type of change you want to introduce. Please, check one (1) box only!
  If your PR requires multiple boxes to be checked, most likely it needs to
  be split into multiple PRs.
-->

- [ ] New core framework functionality
- [ ] Bugfix (non-breaking change which fixes an issue)
- [ ] Code refactoring without any functionality changes
- [ ] New or existing module/payload change
- [ ] Documentation/localization improvement
- [ ] Test coverage improvement
- [ ] Dependency upgrade
- [x] Other improvement (best practice, cleanup, optimization, etc)

## Checklist

- [x] I've followed the [contributing guidelines][contributing-guidelines]
- [x] I've run `make pre-commit`, it didn't generate any changes
- [x] I've run `make test`, all tests passed locally

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
