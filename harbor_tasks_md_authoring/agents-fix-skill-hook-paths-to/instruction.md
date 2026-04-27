# Fix skill hook paths to resolve to correct directories

Source: [astronomer/agents#56](https://github.com/astronomer/agents/pull/56)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `skills/analyzing-data/SKILL.md`
- `skills/init/SKILL.md`

## What to add / change

## Summary

Fixed skill hook paths that were causing "No such file or directory" errors. The previous paths incorrectly included the full skill directory name twice (e.g., `${CLAUDE_PLUGIN_ROOT}/skills/analyzing-data/skills/analyzing-data/scripts/cli.py`).

## Root Cause

Hooks in SKILL.md frontmatter run with the skill's directory as the working directory, so simple relative paths work correctly without needing `${CLAUDE_PLUGIN_ROOT}`.

## Changes

- **analyzing-data**: Use `./scripts/cli.py` (relative to skill directory)
- **init**: Use `../analyzing-data/scripts/cli.py` (relative path to sibling skill)
- **AGENTS.md / CLAUDE.md**: Document that SKILL.md hooks can use relative paths, while `marketplace.json` should use `${CLAUDE_PLUGIN_ROOT}`

## Test plan

- [ ] Install skills via `npx skills add astronomer/agents` (project scope)
- [ ] Install skills via `npx skills add astronomer/agents` (global scope)
- [ ] Verify `analyzing-data` and `init` skill hooks execute without path errors
- [ ] Test both symlink and copy installation methods

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
