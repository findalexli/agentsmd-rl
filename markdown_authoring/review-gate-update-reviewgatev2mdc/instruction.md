# Update ReviewGateV2.mdc

Source: [LakshmanTurlapati/Review-Gate#47](https://github.com/LakshmanTurlapati/Review-Gate/pull/47)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `V2/ReviewGateV2.mdc`

## What to add / change

Force review gate in every chat, regardless of whether the agent deems this as a task or regular conversation. In my tests in many chats, just having a regular conversation like Hey or other greetings the agent never calls review gate and ends up wasting credits this check Insurance that review gate will be triggered, regardless of whether the agent deems it suitable or not

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
