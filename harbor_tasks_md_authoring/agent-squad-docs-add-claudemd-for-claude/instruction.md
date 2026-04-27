# docs: add CLAUDE.md for Claude Code guidance

Source: [2FastLabs/agent-squad#477](https://github.com/2FastLabs/agent-squad/pull/477)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Issue Link (REQUIRED)
Fixes #478

## Summary

Adds a root-level `CLAUDE.md` so future Claude Code sessions (for issue triage and PR review on this repo) start with the right context instead of re-discovering it every time.

### Changes

- New `CLAUDE.md` at repo root covering:
  - **Repo shape** — dual-language monorepo (`python/` + `typescript/`) with feature-parity expectation; note on the `multi-agent-orchestrator` → `agent-squad` and `awslabs` → `2fastlabs` rename history.
  - **Commands** — `make code-quality` / `make test` (Python, from `python/`), `npm run lint` / `npm test` / `npm run coverage` (TypeScript, from `typescript/`), plus single-test invocations and the `prebuild` version-file generator quirk.
  - **Architecture** — the five core abstractions (`AgentSquad` orchestrator, `Classifier`, `Agent`, `ChatStorage`, `Retriever`), the default `BedrockClassifier` fallback, and the two composite agents (`ChainAgent`, `SupervisorAgent`).
  - **CI-enforced contributing rules** — issue-first policy, PR template, Python 3.11–3.13 matrix, Lychee link check.
  - **Cross-implementation notes** — snake_case vs camelCase exports, `*Options` dataclass construction pattern, `try/except ImportError` gating for optional extras.

### User experience

Before: Claude Code sessions opened against this repo had to discover commands, architecture, and the issue-first policy from scratch on every run.
After: that context is loaded automatically from `CLAUDE.md`, so PR reviews and issue

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
