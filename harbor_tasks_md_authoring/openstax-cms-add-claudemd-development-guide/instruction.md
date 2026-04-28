# Add CLAUDE.md development guide

Source: [openstax/openstax-cms#1639](https://github.com/openstax/openstax-cms/pull/1639)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Adds a comprehensive `CLAUDE.md` guide for Claude agents working on the openstax-cms repository.

## What's Included

- **Setup instructions**: Complete walkthrough from clone to running server
- **Project structure**: Overview of directories and key files
- **Migration workflow**: Step-by-step guide for creating Django migrations
- **Development tasks**: Common commands for testing, Docker, database management
- **Key models**: Documentation of important models (especially Assignable)
- **Troubleshooting**: Solutions for common setup issues

## Why This Matters

Claude agents have ephemeral workspaces that reset between sessions. This documentation ensures:
- Consistent setup procedures across sessions
- Proper migration creation (avoiding manual migration files)
- Understanding of project architecture
- Quick reference for common tasks

## Related

Jira: https://openstax.atlassian.net/browse/CORE-1277

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
