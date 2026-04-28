# chore: add .cursor/rules files from PR #123

Source: [pdpipe/pdpipe#144](https://github.com/pdpipe/pdpipe/pull/144)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/always.mdc`
- `.cursor/rules/dev_test_and_build.mdc`
- `.cursor/rules/python.mdc`

## What to add / change

Split from #123.

This PR includes only the .cursor/rules additions:
- .cursor/rules/always.mdc
- .cursor/rules/dev_test_and_build.mdc
- .cursor/rules/python.mdc

All other #123 changes are intentionally excluded.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
