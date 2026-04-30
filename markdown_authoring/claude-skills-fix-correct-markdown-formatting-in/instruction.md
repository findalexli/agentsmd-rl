# Fix: correct markdown formatting in prompt-patterns.md

Source: [Jeffallan/claude-skills#160](https://github.com/Jeffallan/claude-skills/pull/160)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/prompt-engineer/references/prompt-patterns.md`

## What to add / change

## Problem

The CoT ~~and ReAct~~ section~~s~~ had nested code block issues causing markdown rendering problems.

## Changes

**Bug fixes:**

- Fixed nested code blocks in "Example: Debugging with CoT"
~~- Fixed nested code blocks in "Example: ReAct for Research"~~  
~~- Fixed ToT code architecture example formatting~~

~~**Optional style change:**~~

~~- Converted ASCII art table to markdown table (will change if you prefer the original style)~~

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
