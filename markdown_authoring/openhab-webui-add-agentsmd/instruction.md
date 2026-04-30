# Add AGENTS.md

Source: [openhab/openhab-webui#4070](https://github.com/openhab/openhab-webui/pull/4070)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `bundles/org.openhab.ui/AGENTS.md`

## What to add / change

This adds a root AGENTS.md as well as a Main UI AGENTS.md for AI coding agents.
See https://agents.md/ for more information.

The root AGENTS.md is based on the one from openhab-addons.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
