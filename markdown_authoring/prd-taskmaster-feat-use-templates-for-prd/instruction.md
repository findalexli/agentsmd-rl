# feat: use templates for PRD and CLAUDE.md generation

Source: [anombyte93/prd-taskmaster#2](https://github.com/anombyte93/prd-taskmaster/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

- Modified Step 6 to read PRD template from `templates/` directory instead of hardcoded structure
- Added Step 10.5 to generate `CLAUDE.md` from `templates/CLAUDE.md.template`
- Added pre-check to skip generation if `CLAUDE.md`/`codex.md` already exists
- Updated Workflow Overview to reflect 13 steps

## Why This Change?

The `templates/` directory contains well-structured templates (`taskmaster-prd-comprehensive.md`, `taskmaster-prd-minimal.md`, `CLAUDE.md.template`) but they were not being used by the skill. This PR makes the skill actually read and use these templates, providing:

- Consistent PRD structure across projects
- TDD workflow guide (CLAUDE.md) for better development practices
- Respect for existing user configurations (won't overwrite existing files)

## Test plan

- [x] Test PRD generation with comprehensive template
- [ ] Test PRD generation with minimal template
- [ ] Test CLAUDE.md generation when file doesn't exist
- [ ] Test CLAUDE.md skip when file already exists
- [ ] Test codex.md generation flow

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
