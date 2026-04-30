# docs: update CLAUDE.md to match current project state

Source: [slopus/happy#406](https://github.com/slopus/happy/pull/406)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Update Expo SDK from 53 to 54
- Update Expo Router from v5 to v6
- Change test framework from Jest to Vitest
- Update encryption library from tweetnacl to libsodium
- Add LiveKit for real-time voice communication
- Update supported languages from 4 to 9 (en, ru, pl, es, ca, it, pt, ja, zh-Hans)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
