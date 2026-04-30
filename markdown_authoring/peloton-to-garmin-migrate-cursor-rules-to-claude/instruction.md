# Migrate .cursor rules to Claude Code config

Source: [philosowaffle/peloton-to-garmin#835](https://github.com/philosowaffle/peloton-to-garmin/pull/835)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/working-issue/SKILL.md`
- `.cursor/rules/api-development-patterns.mdc`
- `.cursor/rules/configuration-patterns.mdc`
- `.cursor/rules/development-workflow.mdc`
- `.cursor/rules/documentation-guide.mdc`
- `.cursor/rules/knowledge-base-maintenance.mdc`
- `.cursor/rules/knowledge-base-reference.mdc`
- `.cursor/rules/project-overview.mdc`
- `.cursor/rules/sync-service-patterns.mdc`
- `.cursor/rules/testing-requirements.mdc`
- `.cursor/rules/ui-development.mdc`
- `CLAUDE.md`

## What to add / change

## Summary

- Removes `.cursor/rules/` (10 `.mdc` files)
- Adds `CLAUDE.md` at the repo root consolidating all cursor rules into Claude Code format — always-apply rules at the top, context-specific sections (API, config, sync, UI, docs, testing) labeled for when they apply
- Adds `.claude/skills/working-issue/` — the standard working-issue skill adapted for P2G: dotnet build/test validation, `[issue-number] Description` commit style, no conventional commit labels

## Test plan

- [ ] Open a new Claude Code session in this repo and verify `CLAUDE.md` is loaded with project context
- [ ] Invoke `/working-issue` and verify the skill loads and uses dotnet commands and correct commit format

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
