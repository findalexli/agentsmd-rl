# docs: add AGENTS.md repository guidelines

Source: [Azure/azure-sdk-for-js#36046](https://github.com/Azure/azure-sdk-for-js/pull/36046)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

(created by copilot)

Add AGENTS.md at repo root as a concise contributor and agent guide tailored to this monorepo.

Why
- Complements CONTRIBUTING.md with short, actionable guidance for agents and humans.

Reference
- AGENTS.md convention used by agentic tooling (e.g., Codex CLI). See https://github.com/openai/codex-cli for context.

Scope
- Documentation only; no code changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
