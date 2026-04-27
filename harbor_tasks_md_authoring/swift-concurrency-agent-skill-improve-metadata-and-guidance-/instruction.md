# Improve metadata and guidance on tool use

Source: [AvdLee/Swift-Concurrency-Agent-Skill#13](https://github.com/AvdLee/Swift-Concurrency-Agent-Skill/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `swift-concurrency/SKILL.md`

## What to add / change

This format of skill should be more readable for LLMs + guidance on specific and efficient tool usage not to guess at search patterns wasting input/output tokens

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
