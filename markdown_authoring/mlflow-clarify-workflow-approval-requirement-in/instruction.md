# Clarify workflow approval requirement in copilot `SKILL.md`

Source: [mlflow/mlflow#22339](https://github.com/mlflow/mlflow/pull/22339)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/copilot/SKILL.md`

## What to add / change

The "Approving workflows" section lacked context on *why* approval is needed and *when* to run the script, leaving agents without clear guidance.

### Changes

- **`.claude/skills/copilot/SKILL.md`**: Updated section description to explain that Copilot commits require workflow approval for security reasons (unlike maintainer commits), and that `approve.sh` must be run once the PR is finalized.

### How is this PR tested?

- [ ] Manual tests

### Does this PR require documentation update?

- [ ] No.

### Does this PR require updating the [MLflow Skills](https://github.com/mlflow/skills) repository?

- [ ] No.

### Release Notes

#### Is this a user-facing change?

- [x] No.

#### What component(s), interfaces, languages, and integrations does this PR affect?

Components

- [ ] `area/build`: Build and test infrastructure for MLflow

<a name="release-note-category"></a>

#### How should the PR be classified in the release notes? Choose one:

- [x] `rn/none` - No description will be included. The PR will be mentioned only by the PR number in the "Small Bugfixes and Documentation Updates" section

#### Is this PR a critical bugfix or security fix that should go into the next patch release?

- [ ] This PR is critical and needs to be in the next patch release
- [x] This PR can wait for the next minor release

<!-- START COPILOT CODING AGENT SUFFIX -->



<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> # Clarify workflow approval requirement

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
