# Use AGENTS.md for cross-compatibility

Source: [kubermatic/kubelb#405](https://github.com/kubermatic/kubelb/pull/405)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `test/e2e/AGENTS.md`
- `test/e2e/CLAUDE.md`

## What to add / change

**What this PR does / why we need it**:

**Which issue(s) this PR fixes**:
<!--optional, in `fixes #<issue number>` format, will close the issue(s) when PR gets merged-->
Fixes #

**What type of PR is this?**
<!--
Add one of the following kinds:
/kind bug
/kind cleanup
/kind documentation
/kind feature
/kind design

Optionally add one or more of the following kinds if applicable:
/kind api-change
/kind deprecation
/kind failing-test
/kind flake
/kind regression
/kind chore
-->

**Special notes for your reviewer**:

**Does this PR introduce a user-facing change? Then add your Release Note here**:
<!--
Write your release note:
1. Enter your extended release note in the below block. If the PR requires additional action from users switching to the new release, include the string "action required".
2. If no release note is required, just write "NONE".
-->
```release-note
NONE
```

**Documentation**:
<!--
Please do one of the following options:
- Add a link to the existing documentation
- Add a link to the kubermatic/docs pull request
- If no documentation change is applicable then add:
  - TBD (documentation will be added later)
  - NONE (no documentation needed for this PR)
-->
```documentation
NONE
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
