# Add CLAUDE.md (pointing to AGENTS.md)

Source: [WordPress/secure-custom-fields#364](https://github.com/WordPress/secure-custom-fields/pull/364)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Required for Claude Code, see https://code.claude.com/docs/en/claude-code-on-the-web#best-practices.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
