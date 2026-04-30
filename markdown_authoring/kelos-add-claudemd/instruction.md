# Add CLAUDE.md

Source: [kelos-dev/kelos#30](https://github.com/kelos-dev/kelos/pull/30)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!-- This is an auto-generated description by cubic. -->
## Summary by cubic
Added CLAUDE.md to document assistant conventions and standard Makefile targets for builds, tests, and CI. This reduces guesswork and keeps changes minimal and consistent.

<sup>Written for commit f443a8e92e5b69fff540ccc4cf6294b92b8cb112. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
