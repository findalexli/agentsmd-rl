# Add ip-lookup skill

Source: [besoeasy/open-skills#9](https://github.com/besoeasy/open-skills/pull/9)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ip-lookup/SKILL.md`

## What to add / change

Adds a reusable skill to aggregate IP geolocation and metadata from multiple public sources and return a best-match summary.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
