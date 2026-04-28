# docs: add development environment section to CLAUDE.md

Source: [vm0-ai/vm0#363](https://github.com/vm0-ai/vm0/pull/363)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Add Development Environment section to CLAUDE.md documenting the isolated Docker container setup
- Document key assumptions: main branch stability, dev-tunnel usage, database migration, and environment variable sync

## Test plan

- [ ] Review documentation content for accuracy

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
