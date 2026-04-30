# Create SKILL.md for capemon-developer documentation

Source: [kevoreilly/capemon#120](https://github.com/kevoreilly/capemon/pull/120)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.gemini/skills/capemon-developer/SKILL.md`

## What to add / change

Added detailed documentation for the capemon-developer skill, outlining its capabilities in malware monitoring and analysis.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
