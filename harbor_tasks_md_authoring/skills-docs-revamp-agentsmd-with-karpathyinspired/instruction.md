# docs: revamp AGENTS.md with Karpathy-inspired guidelines and TDD principles

Source: [microsoft/skills#18](https://github.com/microsoft/skills/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `Agents.md`

## What to add / change

## Summary

Revamps `AGENTS.md` and `.github/copilot-instructions.md` to provide better steering for AI coding agents working with Azure/Foundry SDKs.

### Key Changes

- **Fresh Information First** — Emphasizes searching official docs (Microsoft Docs MCP) before implementing, since Azure SDKs change constantly
- **4 Core Principles** (inspired by [Karpathy's observations](https://x.com/karpathy/status/2015883857489522876)):
  1. Think Before Coding — Don't assume, surface tradeoffs
  2. Simplicity First — Minimum code, nothing speculative
  3. Surgical Changes — Touch only what you must
  4. Goal-Driven Execution (TDD) — Define success criteria, loop until verified
- **Clean Architecture** — Layered boundaries diagram
- **Complete Skills List** — All 17 skills documented with purposes
- **MCP Servers** — Documentation for microsoft-docs, context7, deepwiki, playwright, etc.
- **Clean Code Checklist** — Pre-commit verification
- **Testing Patterns** — Arrange/Act/Assert with Azure SDK examples
- **Do's and Don'ts** — Clear guidelines with success indicators

### Why

LLMs often:
- Make wrong assumptions and run with them
- Overcomplicate code with unnecessary abstractions
- Change adjacent code as side effects
- Work with outdated SDK knowledge

These guidelines directly address those issues by steering agents toward verification, simplicity, and surgical changes.

### Files Changed

- `AGENTS.md` — Complete revamp with all principles and documentation
- `.github/copilot-inst

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
