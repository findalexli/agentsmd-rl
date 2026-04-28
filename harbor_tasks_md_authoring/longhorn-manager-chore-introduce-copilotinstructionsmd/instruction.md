# chore: introduce copilot-instructions.md

Source: [longhorn/longhorn-manager#4635](https://github.com/longhorn/longhorn-manager/pull/4635)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

#### Which issue(s) this PR fixes:
<!--
Use `Issue #<issue number>` or `Issue longhorn/longhorn#<issue number>` or `Issue (paste link of issue)`. DON'T use `Fixes #<issue number>` or `Fixes (paste link of issue)`, as it will automatically close the linked issue when the PR is merged.
-->
Issue Longhorn/longhorn#12902

#### What this PR does / why we need it:

#### Special notes for your reviewer:

#### Additional documentation or context

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
