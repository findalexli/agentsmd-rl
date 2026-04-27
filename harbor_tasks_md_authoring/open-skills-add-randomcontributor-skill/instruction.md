# Add random-contributor skill

Source: [besoeasy/open-skills#5](https://github.com/besoeasy/open-skills/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/random-contributor/SKILL.md`

## What to add / change

Adds a skill to select a random contributor from a public GitHub repository (API with pagination + fallback scraping).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
