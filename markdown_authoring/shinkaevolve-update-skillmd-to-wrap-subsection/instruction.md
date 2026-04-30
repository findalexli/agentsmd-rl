# Update SKILL.md to wrap subsection filenames

Source: [SakanaAI/ShinkaEvolve#81](https://github.com/SakanaAI/ShinkaEvolve/pull/81)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/shinka-setup/SKILL.md`

## What to add / change

This small PR adds backticks to the filenames in subsection titles. I mainly want to fix the issue where `<ext>` wasn’t being shown properly on GitHub, like the following:

<img width="658" height="218" alt="CleanShot 2026-02-24 at 11 13 44@2x" src="https://github.com/user-attachments/assets/a2863dec-4b1f-486c-86e3-2fd0421a7c86" />

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
