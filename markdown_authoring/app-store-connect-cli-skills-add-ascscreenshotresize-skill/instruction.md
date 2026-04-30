# Add asc-screenshot-resize skill

Source: [rorkai/app-store-connect-cli-skills#31](https://github.com/rorkai/app-store-connect-cli-skills/pull/31)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/asc-screenshot-resize/SKILL.md`

## What to add / change

## Summary
- Adds a new `asc-screenshot-resize` skill for preparing App Store screenshots
- Covers required dimensions for all device classes: iPhone, iPad, Apple Watch, Mac, Apple TV
- Uses macOS built-in `sips` — zero third-party dependencies
- Includes batch resize workflow, Unicode filename fix, and validation guardrails

## What's included
- Complete dimension reference table for all App Store Connect device sizes
- Step-by-step workflow: check → resize → batch → verify
- Handles the common macOS Unicode filename issue (`U+202F`) that breaks CLI tools
- Guardrails for alpha channel, format, and aspect ratio

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
