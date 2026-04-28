# Fix tag formatting in SKILL.md

Source: [Ar9av/obsidian-wiki#4](https://github.com/Ar9av/obsidian-wiki/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.skills/llm-wiki/SKILL.md`

## What to add / change

Added space after the opening parenthesis in tags for better parsing.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
