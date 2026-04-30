# fix(skill): use ${CLAUDE_SKILL_DIR} for script paths

Source: [netresearch/jira-skill#58](https://github.com/netresearch/jira-skill/pull/58)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/jira-communication/SKILL.md`
- `skills/jira-syntax/SKILL.md`

## What to add / change

## Summary

- Replace all relative `scripts/` paths with `${CLAUDE_SKILL_DIR}/scripts/` in both SKILL.md files
- **jira-communication**: 20+ occurrences updated, removed misleading "Paths are relative to" line
- **jira-syntax**: 3 occurrences updated (validate script references)
- Scripts are now found regardless of the user's working directory

## Context

`${CLAUDE_SKILL_DIR}` is the [officially documented mechanism](https://code.claude.com/docs/en/skills) for skills to reference their own scripts. Relative paths broke when skills were invoked from a project directory other than the skill's repo.

## Test plan

- [ ] Invoke jira-communication skill from a non-jira-skill project directory
- [ ] `uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py --help` resolves correctly
- [ ] `${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh` resolves correctly
- [ ] SKILL.md word count still under 500

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
