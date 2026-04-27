# Add Muninn boot + decision traces to CLAUDE.md

Source: [oaustegard/claude-skills#294](https://github.com/oaustegard/claude-skills/pull/294)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

*Filed by Muninn*

## What

Three related changes to CLAUDE.md:

1. **Muninn Boot section** — Claude Code now boots Muninn at session start, getting full operational context and memory access. Credentials auto-detect from well-known paths.

2. **Decision Trace instructions** — After meaningful work, CC stores a `remember()` trace: what was learned, key decisions, constraints discovered. Tight template, no bloat.

3. **Import path cleanup** — Replaced hardcoded `sys.path.insert` + `from scripts import` with post-boot `from remembering.scripts import` throughout.

## Why

Both wings of the raven operate on the same codebase with asymmetric visibility. Without decision traces, Claude.ai discovers changes without context. Direct trigger: issue #293, where Muninn proposed restoring `remembering/__init__.py` without knowing the constraint had been established over ~10 rounds.

Booting Muninn in CC also eliminates the hardcoded import patterns scattered through CLAUDE.md — one boot block replaces multiple `sys.path.insert` incantations.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
