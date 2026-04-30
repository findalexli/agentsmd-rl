# add ast grep to claude.md

Source: [flowglad/flowglad#396](https://github.com/flowglad/flowglad/pull/396)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `claude.md`
- `platform/flowglad-next/claude.md`

## What to add / change

<!-- This is an auto-generated description by cubic. -->

## Summary by cubic
Add ast-grep CLI tips to claude.md and platform/flowglad-next/claude.md. This gives a quick reminder and short explanation for structural search and replace to speed up large code edits.

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
