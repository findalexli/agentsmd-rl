# docs: add .github/copilot-instructions.md

Source: [oisee/vibing-steampunk#80](https://github.com/oisee/vibing-steampunk/pull/80)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary

Add `.github/copilot-instructions.md` to give GitHub Copilot (and other AI assistants using this file) immediate context when working in this repository.

## What's included

- **Build / test / lint commands** — including how to run a single test by name
- **Architecture overview** — request flow from AI agent → MCP handlers → ADT client → SAP, plus the write lifecycle (GetSource → SyntaxCheck → Lock → Update → Unlock → Activate)
- **Adding a new tool** — the 5-step checklist with code patterns for ADT client methods and MCP handlers
- **Key conventions** — functional options, safety system operation codes, tool modes, handler file organization, config priority, integration test setup, report naming, release process

## Source material

Distilled from `CLAUDE.md` and `ARCHITECTURE.md`, focused on what's actionable for code generation rather than exhaustive documentation.

## Checklist

- [x] No code changes — documentation only
- [x] Does not duplicate existing files (no prior `copilot-instructions.md` existed)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
