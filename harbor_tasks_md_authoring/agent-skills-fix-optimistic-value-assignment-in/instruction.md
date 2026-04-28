# Fix optimistic value assignment in SKILL.md

Source: [remix-run/agent-skills#2](https://github.com/remix-run/agent-skills/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/react-router-data-mode/SKILL.md`

## What to add / change

The inline mutation snippet computes optimistic as fetcher.formData?.get("favorite") === "true" ?? isFavorite; (.claude/skills/react-router-data-mode/SKILL.md:74-79). 

Because === "true" yields a boolean, the ?? isFavorite fallback never triggers (booleans are never null/undefined), so when formData is missing this always becomes false, not isFavorite. 

This will cause copy/paste bugs in apps following the skill.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
