# sqlparser: document codegen in AGENTS.md

Source: [vitessio/vitess#19764](https://github.com/vitessio/vitess/pull/19764)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `go/vt/sqlparser/AGENTS.md`

## What to add / change

## Description

Documents the codegen commands and generated file mapping in the sqlparser `AGENTS.md` so AI agents (and humans) know which files are generated, what generates them, and which `make` target to run.

## Related Issue(s)

N/A

## Checklist

- [x] "Backport to:" labels have been added if this change should be back-ported to release branches
- [x] If this change is to be back-ported to previous releases, a justification is included in the PR description
- [x] Tests were added or are not required
- [x] Did the new or modified tests pass consistently locally and on CI?
- [x] Documentation was added or is not required

## Deployment Notes

None.

### AI Disclosure

Written by Claude Code.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
