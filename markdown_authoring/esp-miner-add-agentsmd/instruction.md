# Add AGENTS.md

Source: [bitaxeorg/ESP-Miner#1656](https://github.com/bitaxeorg/ESP-Miner/pull/1656)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Mostly build instructions, some agents struggle with sourcing ESP-IDF environment or how to run certain npm steps.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
