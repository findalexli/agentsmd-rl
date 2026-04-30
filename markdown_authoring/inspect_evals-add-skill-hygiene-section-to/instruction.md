# Add skill hygiene section to AGENTS.md

Source: [UKGovernmentBEIS/inspect_evals#1233](https://github.com/UKGovernmentBEIS/inspect_evals/pull/1233)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This was just an idea I had that might effect continuous improvement of our skill library.
Happy to modify based on feedback!

## Description

Adds a **Skill Hygiene** subsection under General Agent Tips in AGENTS.md, providing guidance for agents on when and how to propose creating or updating reusable skills. Also fixes a pre-existing missing closing quote in the Recommended Permissions JSON block.

## Checklist

- [ ] Are you adding a new eval?

- [ ] Does this change affect existing eval(s)?

- [ ] Is this change consequential to users?

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
