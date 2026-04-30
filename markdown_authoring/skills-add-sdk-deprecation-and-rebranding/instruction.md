# Add SDK deprecation and rebranding pattern to skill-creator

Source: [microsoft/skills#272](https://github.com/microsoft/skills/pull/272)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/skill-creator/SKILL.md`

## What to add / change

- Add 'Handling Deprecated or Rebranded SDKs' section with clear guidance
- Include migration notice template for skills
- Show dual installation examples (legacy vs recommended)
- Provide decision criteria for updating vs creating new skills
- Reference real examples: Form Recognizer → Document Intelligence, CallingServer → CallAutomation

Ensures consistent handling of SDK transitions across all future Azure SDK skills.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
