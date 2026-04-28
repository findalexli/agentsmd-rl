# Add AGENTS.md for AI coding agent guidance

Source: [RevenueCat/purchases-unity#833](https://github.com/RevenueCat/purchases-unity/pull/833)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Adds `AGENTS.md` file to provide development guidelines for AI coding agents working with this repository

The file includes:
- Project overview and Unity/C# structure
- Common development commands and package creation
- Platform wrapper architecture (iOS/Android/Noop)
- Public API stability guidelines
- PR labeling conventions
- Code guardrails and best practices

## Test plan
- [x] AGENTS.md follows the same format as other RevenueCat SDK repos (purchases-ios, purchases-android, purchases-flutter)
- [x] Contains accurate information based on repository exploration

🤖 Generated with [Claude Code](https://claude.ai/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
