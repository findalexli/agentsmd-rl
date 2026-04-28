# Fix usage of cursor rules by adhering to the proper format

Source: [zauberzeug/nicegui#5310](https://github.com/zauberzeug/nicegui/pull/5310)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/general.mdc`

## What to add / change

### Motivation

`.cursor/rules` must be a directory with `*.mdc` files. See https://cursor.com/docs/context/rules#project-rules.

### Implementation

Simply moved the file to the right location and added the "always" header.

### Progress

- [x] I chose a meaningful title that completes the sentence: "If applied, this PR will..."
- [x] The implementation is complete.
- [x] Pytests are not needed.
- [x] Documentation is not necessary.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
