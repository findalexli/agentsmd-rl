# Add CLAUDE.md for Claude Code integration

Source: [angularsen/UnitsNet#1621](https://github.com/angularsen/UnitsNet/pull/1621)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Added CLAUDE.md file to provide guidance for Claude Code when working with the UnitsNet codebase
- Includes essential commands, architecture overview, and development guidelines
- Helps Claude Code understand the unique code generation workflow

## Test plan
- [x] Created CLAUDE.md file with comprehensive documentation
- [x] Verified file includes all key commands and workflows
- [x] Documented code generation process and project structure

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
