# Create AGENTS.md

Source: [vbpf/prevail#910](https://github.com/vbpf/prevail/pull/910)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- retune the opening guidance to focus on soundness of analysis with explicit reasoning and conservative defaults
- update the build and test workflow to only reference the `./tests` runner, avoiding non-functional `ctest` guidance

## Testing
- bash scripts/format-code --staged

------
https://chatgpt.com/codex/tasks/task_e_68c8701a68408329a2ba61abb6ff925e

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

- Documentation
  - Added AGENTS.md: a guide for AI agents working with the repository.
  - Covers soundness-first principles, project overview, repository structure, and where to add logic/tests.
  - Includes build and test workflow with example commands.
  - Provides platform prerequisites for Linux/macOS/Windows/Docker.
  - Details coding standards, formatting, license checks, and Git hooks.
  - Notes on documenting new CLI options and invariants.
  - No code or API changes.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
