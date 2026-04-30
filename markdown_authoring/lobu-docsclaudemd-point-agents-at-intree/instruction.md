# docs(claude.md): point agents at in-tree packages/owletto-backend

Source: [lobu-ai/lobu#410](https://github.com/lobu-ai/lobu/pull/410)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds an "Owletto" section to `CLAUDE.md` so agents know the live MCP server, ClientSDK, sandbox, and tool registry live in `packages/owletto-backend/` (not in the `../owletto` source repo).
- Keeps the existing `Local-only references` pointer for the OpenClaw memory plugin.

## Test plan
- [x] Docs only — no code paths touched.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
