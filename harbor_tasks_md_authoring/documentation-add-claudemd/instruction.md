# Add CLAUDE.MD

Source: [strapi/documentation#3033](https://github.com/strapi/documentation/pull/3033)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

This PR initializes a CLAUDE.MD file which contains all the relevant information for Claude Code, now that the Docs AI toolchain is complete.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
