# feat: add expert panel scoring to copy-editing

Source: [coreyhaines31/marketingskills#213](https://github.com/coreyhaines31/marketingskills/pull/213)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/copy-editing/SKILL.md`

## What to add / change

## Summary
- Adds multi-persona expert panel scoring technique for high-stakes copy
- Includes iterative scoring loop: assemble personas, score 1-10, revise, re-score until 8+
- Provides recommended panels for landing pages, email sequences, and sales pages
- Adds scoring rubric and when-to-use guidance
- Bumps version to 1.2.0

Inspired by Eric Siu's recursive expert panel pattern — adapted from their Python-based scoring to a lightweight, tool-agnostic technique.

## Test plan
- [ ] Verify SKILL.md under 500 lines (currently 498)
- [ ] Verify section integrates naturally after Seven Sweeps Framework

Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
