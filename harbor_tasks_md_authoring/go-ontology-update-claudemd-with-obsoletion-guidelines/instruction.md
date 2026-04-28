# Update CLAUDE.md with obsoletion guidelines

Source: [geneontology/go-ontology#31251](https://github.com/geneontology/go-ontology/pull/31251)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Added guidelines for preserving term_tracker_items and comments during obsoletion.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
