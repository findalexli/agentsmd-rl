# Add CLAUDE.md with project guidelines

Source: [rocicorp/mono#4868](https://github.com/rocicorp/mono/pull/4868)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Added CLAUDE.md file with project-specific guidelines for Claude
- Documented code quality requirements (lint, format, type-check)
- Documented TypeScript conventions for optional fields in the codebase

## Test plan
- [x] File created successfully
- [x] Guidelines are clear and actionable
- [x] No code changes that require testing

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
