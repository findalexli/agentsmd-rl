# docs: clean up develop skill boilerplate and stale references

Source: [TheBushidoCollective/han#84](https://github.com/TheBushidoCollective/han/pull/84)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/core/skills/develop/SKILL.md`

## What to add / change

## Summary

- Enrich `description` frontmatter with trigger terms for better skill matching
- Remove 4 redundant sections (Name, Synopsis, Description, Implementation) that repeated "Comprehensive 8-phase workflow" verbatim
- Remove stale Usage section referencing non-existent `/feature-dev` command
- Update See Also to reference current skill names

All phase content, best practices, and example workflow preserved unchanged.

Inspired by observations in #77 (without the third-party CI dependency).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
