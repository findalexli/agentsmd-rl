# feat: add microsoft-docs skill for querying official Microsoft documentation

Source: [microsoft/skills#233](https://github.com/microsoft/skills/pull/233)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/microsoft-docs/SKILL.md`

## What to add / change

Adds a new `microsoft-docs` skill that enables querying Microsoft Learn documentation using the Microsoft Learn MCP Server (or the `mslearn` CLI as a fallback).

## What it does

- Searches Microsoft Learn for concepts, guides, tutorials, configuration options, limits, quotas, and best practices
- Fetches full page content when search excerpts are insufficient
- Covers any Microsoft technology (Azure, .NET, M365, Windows, Power Platform, etc.)

## Files changed

- `.github/skills/microsoft-docs/SKILL.md` -- new skill definition with YAML frontmatter and usage guide

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
