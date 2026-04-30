# Refocus godot-decomposer on isolation and iteration principles

Source: [htdt/godogen#2](https://github.com/htdt/godogen/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/game-decomposer/SKILL.md`
- `.claude/skills/gamedev/SKILL.md`
- `.claude/skills/godot-decomposer/SKILL.md`
- `CLAUDE.md`

## What to add / change

## Summary

Rewrote the godot-decomposer skill documentation to emphasize the core principle: **isolation enables iteration**. The decomposition strategy now centers on creating independently testable tasks with minimal, challenge-focused placeholders, rather than treating decomposition as a generic planning exercise.

## Key Changes

- **Clarified core purpose**: Replaced generic "development plan" language with explicit focus on isolation, iteration, and blast radius control. Each task gets its own test harness; failures regenerate only that task.

- **Removed MEMORY.md requirement**: Eliminated the project memory file initialization. Agents now focus on task execution rather than maintaining a shared knowledge base.

- **Restructured strategy section**: Condensed 7 detailed subsections into 5 focused principles:
  - Placeholders must exercise the real challenge (not avoid it)
  - Independence = blast radius control
  - Merge progressively (2-3 things at a time)
  - Group coherent behaviors (don't over-split)
  - Verification must be unambiguous and test-harness-ready

- **Rewrote "Why Decompose"**: Replaced with "Core Principle: Isolation Enables Iteration" that explains *how* isolation works (test harness per task, early hard tasks for clean signal, no confounding variables).

- **Simplified task field descriptions**: Made Requirements, Placeholder, and Verify fields more concrete and actionable. Emphasized that Verify drives automated screenshot capture, not manual testi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
