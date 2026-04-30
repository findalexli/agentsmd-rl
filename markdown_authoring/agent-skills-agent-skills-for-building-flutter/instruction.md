# Agent Skills for building flutter web with AI Logic

Source: [firebase/agent-skills#78](https://github.com/firebase/agent-skills/pull/78)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/firebase-ai-logic-basics/SKILL.md`
- `skills/firebase-ai-logic-basics/references/flutter_setup.md`
- `skills/firebase-auth-basics/SKILL.md`

## What to add / change

Tested with vibe coded text generated apps

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
