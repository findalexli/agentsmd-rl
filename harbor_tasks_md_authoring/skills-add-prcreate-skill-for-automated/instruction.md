# Add pr-create skill for automated PR creation with CI monitoring

Source: [posit-dev/skills#20](https://github.com/posit-dev/skills/pull/20)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `posit-dev/pr-create/SKILL.md`

## What to add / change

## Summary
- Adds a new `pr-create` skill that automates the PR workflow: assess state, branch, commit, sync, draft PR, run local checks, push, create PR, monitor CI, and fix failures until green
- Generalized from a project-specific workflow to be language-agnostic — discovers project check commands from CLAUDE.md/AGENTS.md, config files, and CI workflows rather than prescribing specific toolchain commands
- Assumes git, GitHub, and GitHub Actions CI; primarily targets R, Python, and web-technology projects

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
