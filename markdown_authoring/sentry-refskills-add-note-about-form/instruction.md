# ref(skills) add note about form search

Source: [getsentry/sentry#109370](https://github.com/getsentry/sentry/pull/109370)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/migrate-frontend-forms/SKILL.md`

## What to add / change

Add form search instructions to form migration.

@TkDodo I didn't want to add this to the general form skill because I think it really only applies to settings, and I don't want anyone going and using it outside of that area

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
