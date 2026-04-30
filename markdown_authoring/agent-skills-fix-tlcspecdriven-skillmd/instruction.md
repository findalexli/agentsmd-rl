# Fix tlc-spec-driven SKILL.md

Source: [tech-leads-club/agent-skills#37](https://github.com/tech-leads-club/agent-skills/pull/37)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/skills-catalog/skills/(development)/tlc-spec-driven/SKILL.md`

## What to add / change

Fix error:
<img width="1598" height="662" alt="CleanShot 2026-02-11 at 20 05 43@2x" src="https://github.com/user-attachments/assets/ce383193-5248-4c8f-b7cd-8ac1bd09565f" />

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
