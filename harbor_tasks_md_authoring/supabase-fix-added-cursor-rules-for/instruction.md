# fix: added cursor rules for use static event effect

Source: [supabase/supabase#41993](https://github.com/supabase/supabase/pull/41993)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/studio-useStaticEffectEvent.mdc`

## What to add / change

## I have read the [CONTRIBUTING.md](https://github.com/supabase/supabase/blob/master/CONTRIBUTING.md) file.

YES

## What kind of change does this PR introduce?

Added use static effect rule, idea is to have code rabbit also pick this up in reviews

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
