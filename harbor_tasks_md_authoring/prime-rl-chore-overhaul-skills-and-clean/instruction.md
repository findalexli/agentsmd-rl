# chore: overhaul skills and clean up AGENTS.md

Source: [PrimeIntellect-ai/prime-rl#2149](https://github.com/PrimeIntellect-ai/prime-rl/pull/2149)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `skills/config/SKILL.md`
- `skills/entrypoints/SKILL.md`
- `skills/inference-server/SKILL.md`
- `skills/installation/SKILL.md`
- `skills/monitor-run/SKILL.md`
- `skills/release/SKILL.md`
- `skills/toml-config/SKILL.md`

## What to add / change

## Summary
- Replace `toml-config` skill with broader `config` skill covering TOML, CLI, composition, and all field type patterns
- Add `entrypoints` skill documenting `rl`, `sft`, and `inference` commands
- Add `release` skill (moved from AGENTS.md)
- Remove `inference-server` skill (consolidated into `entrypoints`)
- Streamline `installation` skill
- Clean up AGENTS.md: concise guidelines, remove redundant sections

## Test plan
- [x] Verified all config patterns (booleans, None, lists, dicts, unions, model fields) by parsing real configs
- [x] Tested `--dry-run`, `--help`, `--slurm` flags against actual entrypoints
- [x] Confirmed skill symlink (`skills/` → `.claude/skills/`) works correctly

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Documentation-only changes (agent guidelines and skills) with no runtime code or dependency modifications.
> 
> **Overview**
> Updates contributor/agent guidance by streamlining `AGENTS.md` (condensed coding/running rules, switches branch prefix guidance to `feat/`, and removes embedded release-note/CLI sections).
> 
> Reorganizes the `skills/` docs: replaces `toml-config` with a broader `config` skill, adds new `entrypoints`, `monitor-run`, and `release` skills, removes the standalone `inference-server` skill, and simplifies the `installation` instructions to focus on `uv sync` flows and advanced extras.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashbo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
