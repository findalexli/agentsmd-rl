# Enhance SKILL.md with Java SDK information

Source: [google-gemini/gemini-skills#13](https://github.com/google-gemini/gemini-skills/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/gemini-api-dev/SKILL.md`

## What to add / change

Updated description to include Java SDK details and installation instructions. And missing Go mention in the frontmatter

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
