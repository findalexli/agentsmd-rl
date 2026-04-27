# Added skill `busybox-on-windows`

Source: [sickn33/antigravity-awesome-skills#26](https://github.com/sickn33/antigravity-awesome-skills/pull/26)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/busybox-on-windows/SKILL.md`

## What to add / change

Allows running many of the standard UNIX commands on Windows by installing a self-contained BusyBox executable.

I found this small utility skill very useful for my Windows work, since the current AI models are not good at using the Windows command line, which results in a lot of failed commands and retries.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
