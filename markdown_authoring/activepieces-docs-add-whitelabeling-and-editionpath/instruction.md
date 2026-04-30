# docs: add white-labeling and edition-path testing guidance (ENG-331)

Source: [activepieces/activepieces#12565](https://github.com/activepieces/activepieces/pull/12565)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Add a new "White-Labeling & Edition Paths" section to CLAUDE.md/AGENTS.md documenting requirements for white-labeled UI, testing across all edition paths (CE, EE, Cloud), appearance edition-gating rules, and the feature gating pattern used on backend and frontend.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
