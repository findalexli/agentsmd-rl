# Add CLAUDE.md for Claude Code onboarding

Source: [NVIDIA-NeMo/Gym#733](https://github.com/NVIDIA-NeMo/Gym/pull/733)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds `CLAUDE.md` to provide project context for Claude Code sessions
- Covers architecture, CLI commands, configuration patterns, JSONL data schema, benchmark contribution workflow, code style, async patterns, external tool auto-install, and cluster gotchas
- All content is generic (no benchmark-specific references)

## Test plan
- [x] Verify CLAUDE.md renders correctly on GitHub
- [x] Spot-check CLI commands against `pyproject.toml` entry points

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
