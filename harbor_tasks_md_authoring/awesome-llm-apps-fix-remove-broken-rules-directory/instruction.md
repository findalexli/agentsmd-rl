# fix: remove broken rules/ directory references in python-expert skill

Source: [Shubhamsaboo/awesome-llm-apps#720](https://github.com/Shubhamsaboo/awesome-llm-apps/pull/720)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `awesome_agent_skills/python-expert/AGENTS.md`
- `awesome_agent_skills/python-expert/SKILL.md`

## What to add / change

## Summary

Fixes #660.

The `python-expert` skill referenced a `rules/` directory that does not exist. `SKILL.md` linked to 8 non-existent rule files and `AGENTS.md` ended each rule section with a "Full details" link pointing into the same missing directory. The "References" section also listed the missing directory.

## Fix

`AGENTS.md` already contains the complete rule content inline with examples, so the referenced deep-dive files are redundant. This PR:

- **AGENTS.md**: removes the 8 broken `[➡️ Full details: ...](rules/...)` links and the missing-directory bullet in "References"
- **SKILL.md**: changes the 8 "Available Rules" bullets to link directly into `AGENTS.md` via section anchors, and rewrites the "How to Use This Skill" paragraph and Quick Start to stop pointing at the non-existent `rules/` directory

Net diff: `AGENTS.md -17 lines`, `SKILL.md +10/-11 lines`.

## Test plan

- [x] Grep for `rules/` inside `awesome_agent_skills/python-expert/` returns no matches
- [x] All `[Rule Name](AGENTS.md#anchor)` links in SKILL.md point at existing section headings in AGENTS.md
- [x] AGENTS.md still renders with all 8 rules fully explained (content was inline, not in the removed links)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
