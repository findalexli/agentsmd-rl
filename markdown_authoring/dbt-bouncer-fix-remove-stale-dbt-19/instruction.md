# fix: remove stale dbt 1.9 references from AGENTS.md and build-artifacts skill

Source: [godatadriven/dbt-bouncer#811](https://github.com/godatadriven/dbt-bouncer/pull/811)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/build-artifacts/SKILL.md`
- `AGENTS.md`

## What to add / change

## Summary
- Update AGENTS.md: remove dbt 1.9 from `make build-artifacts` description
- Update `/build-artifacts` skill: remove dbt 1.9 from description and verification steps, add note that 1.9 fixtures are frozen

The makefile only has `build-artifacts-110`, `build-artifacts-111`, and `build-artifacts-local` targets. dbt 1.9 fixtures are frozen (makefile comment, line 19).

## Test plan
- [ ] Verify AGENTS.md matches actual makefile targets
- [ ] Verify skill instructions don't reference non-existent targets

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
