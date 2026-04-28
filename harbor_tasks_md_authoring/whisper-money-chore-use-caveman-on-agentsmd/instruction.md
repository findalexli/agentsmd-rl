# chore: Use caveman on AGENTS.md

Source: [whisper-money/whisper-money#305](https://github.com/whisper-money/whisper-money/pull/305)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- add concise caveman-mode communication rules at top of `AGENTS.md`
- keep existing agent guidance intact while making terse-response behavior explicit

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
