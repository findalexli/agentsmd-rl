# Update claude.md documentation

Source: [dmarcguardhq/dmarcguard#32](https://github.com/dmarcguardhq/dmarcguard/pull/32)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `claude.md`

## What to add / change

Add a comprehensive project guide for Claude Code containing:
- Tech stack overview (Go, Vue.js, SQLite, Bun, Just)
- Project structure documentation
- Development commands and build instructions
- Testing and code style guidelines
- Key files and API endpoints reference
- Configuration and CI/CD information

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
