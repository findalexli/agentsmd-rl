# docs: improve Libretto skill debugging and pause documentation

Source: [saffron-health/libretto#129](https://github.com/saffron-health/libretto/pull/129)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/libretto/SKILL.md`
- `.claude/skills/libretto/SKILL.md`
- `skills/libretto/SKILL.md`

## What to add / change

## Summary

Improves the Libretto SKILL.md with better debugging and pause documentation:

- **`pause()` signature**: Fixed to show it requires a session ID (`await pause("session-name")`), noted the `"libretto"` import, and documented it as a no-op in production.
- **Session Storage**: Added section documenting `.libretto/sessions/<session>/state.json` and `logs.jsonl` paths.
- **`exec` globals**: Added line listing available globals (`page`, `context`, `browser`, `state`, `networkLog(opts?)`, `actionLog(opts?)`, `fetch`, `Buffer`).
- **`--clear` flag**: Documented on `network` and `actions` commands with examples.
- **`run` visualization**: Added note that ghost cursor + highlights are on by default in headed mode, with `--no-visualize` to disable.
- Removed `--visualize` from `exec` examples.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
