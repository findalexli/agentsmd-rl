# t1081.4: Update AGENTS.md — document daily skill refresh and repo version wins on update

Source: [marcusquinn/aidevops#1639](https://github.com/marcusquinn/aidevops/pull/1639)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/AGENTS.md`

## What to add / change

## Summary

- Documents the daily skill refresh behaviour added by t1081.1: 24h-gated check via `skill-update-helper.sh --auto-update --quiet`, state file fields (`last_skill_check`, `skill_updates_applied`), env vars (`AIDEVOPS_SKILL_AUTO_UPDATE`, `AIDEVOPS_SKILL_FRESHNESS_HOURS`), and status command.
- Clarifies that `aidevops update` overwrites shared agents in `~/.aidevops/agents/` — only `custom/` and `draft/` directories survive. Imported skills outside these dirs are overwritten; users should re-import or move to `custom/` for persistence.
- Adds a cross-reference note in the Skills & Cross-Tool section linking to the auto-update skill refresh behaviour.

## Changes

- `.agents/AGENTS.md`: Added "Daily skill refresh" and "Repo version wins on update" paragraphs to Auto-Update section; added "Skill persistence" note to Skills & Cross-Tool section.

Ref #1585

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
