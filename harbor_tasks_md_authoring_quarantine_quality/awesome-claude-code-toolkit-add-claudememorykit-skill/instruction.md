# Add claude-memory-kit skill

Source: [rohitg00/awesome-claude-code-toolkit#298](https://github.com/rohitg00/awesome-claude-code-toolkit/pull/298)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/claude-memory-kit/SKILL.md`

## What to add / change

## What

Adds `claude-memory-kit` to the skills directory — a persistent memory system for Claude Code.

## Repo

https://github.com/awrshift/claude-memory-kit

## Key features

- Two-layer memory: hot cache (MEMORY.md) + knowledge wiki
- Safety hooks prevent context loss during compression
- `/close-day` end-of-day synthesis in one command
- Multi-project support with per-project backlogs
- Zero external dependencies, MIT license
- 700+ production sessions across 7 projects

## Files added

- `skills/claude-memory-kit/SKILL.md`

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added documentation for the claude-memory-kit skill, detailing its persistent memory system, multi-project backlogs, context isolation, safety features, and included commands for end-of-day synthesis and guided walkthroughs.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
