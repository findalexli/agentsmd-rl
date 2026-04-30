# Add multi-language screenshot support

Source: [ParthJadhav/app-store-screenshots#6](https://github.com/ParthJadhav/app-store-screenshots/pull/6)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/app-store-screenshots/SKILL.md`

## What to add / change

Adds localized screenshot support to SKILL.md:

- New optional question asking if users want screenshots in multiple languages (helps rank in regional App Stores, even for English-only apps)
- Locale tabs in the toolbar for switching between languages
- Folder structure for organizing screenshots by locale
- All slide image srcs use a dynamic base path — no hardcoded paths

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
