# Rename and namespace Claude skills under dd-sdk-ios

Source: [DataDog/dd-sdk-ios#2755](https://github.com/DataDog/dd-sdk-ios/pull/2755)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/git-branch/SKILL.md`
- `.claude/skills/git-commit/SKILL.md`
- `.claude/skills/open-pr/SKILL.md`
- `.claude/skills/running-tests/SKILL.md`
- `.claude/skills/xcode-file-management/SKILL.md`
- `CLAUDE.md`

## What to add / change

### What and why?

Rename all Claude Code skills to use the `dd-sdk-ios:` namespace for clarity and consistency. Also renames `git-pr` to `open-pr` and adds a user-confirmation gate before running `gh pr create`. Advertises all available skills in `CLAUDE.md`.

### How?

- Updated `name` frontmatter in all 5 skill files
- Added a confirmation step in `dd-sdk-ios:open-pr` before executing `gh pr create`
- Added an "Available Skills" table at the top of `CLAUDE.md`

### Review checklist
- [ ] Feature or bugfix MUST have appropriate tests (unit, integration)
- [x] Make sure each commit and the PR mention the Issue number or JIRA reference — N/A (tooling chore, no ticket)
- [ ] Add CHANGELOG entry for user facing changes — N/A (internal tooling)
- [ ] Add Objective-C interface for public APIs — N/A
- [ ] Run `make api-surface` when adding new APIs — N/A

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk: documentation/Claude skill metadata changes only, with no impact on SDK runtime code. Main risk is minor workflow disruption if callers still reference the old skill names.
> 
> **Overview**
> **Namespaces Claude skills for this repo** by renaming the `name` frontmatter in all skill `SKILL.md` files to use the `dd-sdk-ios:` prefix, and renaming `git-pr` to `dd-sdk-ios:open-pr`.
> 
> **Tightens PR creation guidance** by requiring a user confirmation step before running `gh pr create`, and updates `CLAUDE.md` to list the available skills in a new table.
> 
> <sup>Wri

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
