# fix(navan-pack): audit repair — missing Overview + Output headers

Source: [jeremylongshore/claude-code-plugins-plus-skills#486](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/486)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/navan-pack/skills/navan-debug-bundle/SKILL.md`
- `plugins/saas-packs/navan-pack/skills/navan-incident-runbook/SKILL.md`
- `plugins/saas-packs/navan-pack/skills/navan-migration-deep-dive/SKILL.md`
- `plugins/saas-packs/navan-pack/skills/navan-multi-env-setup/SKILL.md`
- `plugins/saas-packs/navan-pack/skills/navan-prod-checklist/SKILL.md`
- `plugins/saas-packs/navan-pack/skills/navan-reference-architecture/SKILL.md`
- `plugins/saas-packs/navan-pack/skills/navan-upgrade-migration/SKILL.md`

## What to add / change

## Summary

- 6 skills from batch-5 agent used wrong section headers (## Expected Output instead of ## Output, missing ## Overview)
- Fixed {env} placeholder false positive in navan-multi-env-setup
- Score: 93.0 → 94.3/100, 0 ERRORs remaining

## Root cause

Subagent prompt listed required sections by name but didn't enforce exact markdown header text. Agent chose `## Expected Output` and dropped `## Overview`.

## Test plan

- [x] `python3 scripts/validate-skills-schema.py --enterprise plugins/saas-packs/navan-pack/` — 94.3/100, 0 ERRORs

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
