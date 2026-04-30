# docs: sync CLAUDE.md architecture map with current src/ layout

Source: [JackChen-me/open-multi-agent#171](https://github.com/JackChen-me/open-multi-agent/pull/171)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Layer Map now lists all current `src/` directories (added Dashboard, CLI, Utils, Errors; split Exports into root + `/mcp` subpath).
- LLM section reflects all 9 providers, async lazy `createAdapter()`, and `baseURL` for OpenAI-compatible local servers.
- Documents loop detection, MCP integration, local-model text-tool-extractor, and the shared `fs-walk` helper used by `grep`/`glob`.
- Adds `test:coverage` / `test:e2e` and the new `examples/` subdir layout.

Docs only — no code changes.

## Test plan
- [x] Manual review: every file/directory referenced in the doc exists under `src/`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
