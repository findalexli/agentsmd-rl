# Fix invalid YAML in skill-creator SKILL.md frontmatter

Source: [langchain-ai/deepagents#675](https://github.com/langchain-ai/deepagents/pull/675)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `libs/deepagents-cli/examples/skills/skill-creator/SKILL.md`

## What to add / change

Fixes #657

The colon in "Use this skill when the user asks to:" was causing the YAML frontmatter to be invalid.

## Changes
- Wrapped the `description` field in double quotes to properly escape colons
- Escaped internal quotes within the description

## Testing
- Verified YAML parses correctly with Python's yaml.safe_load()
- Validated all other SKILL.md files still parse correctly

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
