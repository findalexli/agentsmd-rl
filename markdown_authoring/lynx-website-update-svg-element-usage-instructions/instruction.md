# Update svg element usage instructions in AGENTS.md

Source: [lynx-family/lynx-website#658](https://github.com/lynx-family/lynx-website/pull/658)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/public/AGENTS.md`

## What to add / change

Clarified usage of the svg element with content and src attributes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
