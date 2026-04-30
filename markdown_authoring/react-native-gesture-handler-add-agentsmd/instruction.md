# Add `AGENTS.md`

Source: [software-mansion/react-native-gesture-handler#4085](https://github.com/software-mansion/react-native-gesture-handler/pull/4085)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Description

I've noticed that sometimes agents struggle to check whether apps build correctly, run tests or some other minor things. This PR adds `AGENTS.md` file, along with `CLAUDE.md` (which is a symlink to `AGENTS.md`).

Let me know if you think that anything else is necessary.

## Test plan

I've told agents to check android and iOS builds. Works well with Claude, copilot (GPT-5.2) was struggling 😞

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
