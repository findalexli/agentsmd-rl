# Add `resolve-backport` skill

Source: [vitessio/vitess#19639](https://github.com/vitessio/vitess/pull/19639)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/resolve-backport/SKILL.md`

## What to add / change

## Description

This adds a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill for resolving merge conflicts in Vitess backport PRs

The skill handles the full backport resolution workflow:
1. Validates the PR has a `Backport` label and checks assignees
2. Fetches the upstream PR diff as source of truth for the intended changes
3. Rebases onto the latest base branch before resolving _(avoids creating resolutions that immediately conflict)_
4. Ensures the correct Go version for the release branch
5. Resolves conflicts guided by the upstream diff, prompting for ambiguous cases
6. Verifies file scope — reverts changes to files not in the upstream PR
7. Runs unit tests, build, formatters, and linters
8. Pushes, removes conflict labels, and monitors CI — investigating failures and rerunning flaky tests as needed

For conflict-free backports it just monitors CI and enables auto-merge

Example:
<img width="800" height="448" alt="Screenshot 2026-03-13 at 16 18 17" src="https://github.com/user-attachments/assets/dd5ac5ff-0db4-4786-b38e-5b48f95bdc5b" />

## Related Issue(s)

## Checklist

-   [x] "Backport to:" labels have been added if this change should be back-ported to release branches
-   [x] If this change is to be back-ported to previous releases, a justification is included in the PR description
-   [x] Tests were added or are not required
-   [x] Did the new or modified tests pass consistently locally and on CI?
-   [x] Documentation

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
