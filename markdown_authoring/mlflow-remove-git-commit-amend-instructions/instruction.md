# Remove git commit --amend instructions from CLAUDE.md

Source: [mlflow/mlflow#19487](https://github.com/mlflow/mlflow/pull/19487)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

### Related Issues/PRs

<!-- Uncomment 'Resolve' if this PR can close the linked items. -->
<!-- Resolve --> #xxx

### What changes are proposed in this pull request?

Removed the git commit amend workflow from CLAUDE.md that was causing Claude Code to always amend commits. The removed section instructed:

```bash
# Fix any issues and amend your commit if needed
git add <fixed files>
git commit --amend -s
```

This resulted in undesirable behavior where Claude Code would continuously amend the same commit instead of creating new commits for fixes.

### How is this PR tested?

- [ ] Existing unit/integration tests
- [ ] New unit/integration tests
- [x] Manual tests

Verified the documentation change maintains workflow continuity and removed the problematic instructions.

### Does this PR require documentation update?

- [x] No. You can skip the rest of this section.
- [ ] Yes. I've updated:
  - [ ] Examples
  - [ ] API references
  - [ ] Instructions

### Release Notes

#### Is this a user-facing change?

- [x] No. You can skip the rest of this section.
- [ ] Yes. Give a description of this change to be included in the release notes for MLflow users.

<!-- Details in 1-2 sentences. You can just refer to another PR with a description if this PR is part of a larger change. -->

#### What component(s), interfaces, languages, and integrations does this PR affect?

Components

- [ ] `area/tracking`: Tracking Service, tracking client APIs, autologging
- [ ] `area/models`: MLmodel fo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
