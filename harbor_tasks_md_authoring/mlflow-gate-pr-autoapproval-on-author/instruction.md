# Gate PR auto-approval on author role

Source: [mlflow/mlflow#22765](https://github.com/mlflow/mlflow/pull/22765)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr-review/SKILL.md`

## What to add / change

### Related Issues/PRs

N/A

### What changes are proposed in this pull request?

Update the PR review skill to only auto-approve PRs authored by maintainers or admins, determined by checking the author's `role_name` via the GitHub collaborators API.

### How is this PR tested?

- [x] Manual tests

### Does this PR require documentation update?

- [x] No.

### Does this PR require updating the [MLflow Skills](https://github.com/mlflow/skills) repository?

- [x] No.

### Release Notes

#### Is this a user-facing change?

- [x] No.

#### What component(s), interfaces, languages, and integrations does this PR affect?

Components

- [x] `area/build`: Build and test infrastructure for MLflow

<a name="release-note-category"></a>

#### How should the PR be classified in the release notes? Choose one:

- [x] `rn/none` - No description will be included. The PR will be mentioned only by the PR number in the "Small Bugfixes and Documentation Updates" section

#### Is this PR a critical bugfix or security fix that should go into the next patch release?

- [ ] This PR is critical and needs to be in the next patch release
- [x] This PR can wait for the next minor release

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
