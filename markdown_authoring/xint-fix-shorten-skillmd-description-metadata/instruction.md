# fix: shorten SKILL.md description metadata

Source: [0xNyk/xint#23](https://github.com/0xNyk/xint/pull/23)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary
- shorten xint skill frontmatter description to stay under Codex validator limit (1024 chars)
- keep trigger coverage while removing verbose phrasing

## Validation
- bun run typecheck (pass)
- bun test (fails on existing MCP contract tests with Bun.serve EADDRINUSE; unrelated to this markdown-only change)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
