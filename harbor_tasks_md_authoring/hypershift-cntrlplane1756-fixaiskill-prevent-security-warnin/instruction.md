# CNTRLPLANE-1756: fix(ai-skill): prevent security warning in git-commit-format skill

Source: [openshift/hypershift#7125](https://github.com/openshift/hypershift/pull/7125)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/git-commit-format/SKILL.md`

## What to add / change

## Summary
- Fix backtick formatting in git-commit-format skill documentation that triggers false-positive security warnings

## Details
The checklist used backticks around the "!" character, which Claude Code's security checks misinterpret as command execution. This triggered permission prompts for "!" which cannot be granted, blocking normal use of the skill documentation.

Changed to double quotes to prevent the false-positive security warning while maintaining proper formatting.

## Test plan
- [x] Documentation change only
- [x] Verified formatting renders correctly
- [x] No security warnings triggered

Jira: [CNTRLPLANE-1756](https://issues.redhat.com//browse/CNTRLPLANE-1756)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
