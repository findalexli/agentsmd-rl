# Add agent integration section to SKILL.md

Source: [profbernardoj/everclaw-community-branches#6](https://github.com/profbernardoj/everclaw-community-branches/pull/6)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary
- Adds documentation for how to integrate the Morpheus proxy with OpenClaw agents
- Covers provider configuration, fallback chain setup, and proxy routing details

## Test plan
- [ ] Review SKILL.md for accuracy against current proxy behavior

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
