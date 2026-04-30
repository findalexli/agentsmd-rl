# Update AGENTS.md

Source: [slint-ui/slint#11365](https://github.com/slint-ui/slint/pull/11365)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Simplify some text to save some tokens


I asked Claude to simplify the AGENTS.md (that file is always loaded so it uses token)
it also contains some more info which i had in my local MEMORY.

BTW, by default, claude doesn't load AGENTS.md, it needs to be configured specially to do that. It only loads CLAUDE.md


I haven't tried or noticed any difference, this is just guts feeling from my side.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
