# docs(CLAUDE.md): Add AI assistant guidelines to repository

Source: [freelawproject/courtlistener#6683](https://github.com/freelawproject/courtlistener/pull/6683)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Fixes

Fixes: #6682

## Summary

This PR adds a CLAUDE.md file to the repository with comprehensive guidelines for AI assistants working on CourtListener. The file includes:

- Project structure overview
- Coding rules (URL handling with `reverse()`, type hints, unused code)
- Test base classes and running tests in Docker
- FactoryBoy requirement and fixture ban
- Database migration guide reference
- Conventional commit format
- PR submission guidelines
- Available tools (Docker, CLI)

## Deployment

**This PR should:**

- [X] `skip-deploy` (skips everything below)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
