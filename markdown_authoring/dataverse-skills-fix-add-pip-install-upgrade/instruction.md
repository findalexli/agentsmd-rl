# fix: add pip install --upgrade step to init skill

Source: [microsoft/Dataverse-skills#18](https://github.com/microsoft/Dataverse-skills/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/plugins/dataverse/skills/init/SKILL.md`

## What to add / change

## Summary
- Added `pip install --upgrade azure-identity requests PowerPlatform-Dataverse-Client` as an explicit step in both init scenarios
- **Scenario A**: new step 7 (before verify at step 8)
- **Scenario B**: new step 6 (before verify at step 7)
- Renumbered all subsequent steps and updated cross-references (MCP config step refs in the preamble)

## Why
The init skill copies `scripts/auth.py` and runs `python scripts/auth.py` to verify the connection, but never installs the Python packages that `auth.py` depends on. If packages are missing, the verify step fails. If packages are outdated, they silently stay on old versions. This was the root cause of users having to explicitly ask Claude to upgrade packages even after PR #17 added `--upgrade` to setup and python-sdk skills — the init flow never called pip at all.

## Test plan
- [ ] Run full init Scenario A (existing repo, new machine) — confirm pip install runs before verify
- [ ] Run full init Scenario B (new project) — confirm pip install runs before verify
- [ ] Verify step numbering is sequential in both scenarios

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
