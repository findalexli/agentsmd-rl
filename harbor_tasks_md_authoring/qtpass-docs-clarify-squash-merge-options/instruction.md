# docs: clarify squash merge options and recommend force-with-lease

Source: [IJHack/QtPass#1177](https://github.com/IJHack/QtPass/pull/1177)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.opencode/skills/qtpass-github/SKILL.md`

## What to add / change

<!-- kody-pr-summary:start -->
The pull request updates the documentation for GitHub CLI usage and Git best practices.

Specifically, it:
*   Clarifies the GitHub CLI squash merge options, distinguishing between merging immediately and scheduling a merge that waits for CI checks to pass.
*   Recommends using `git push --force-with-lease` for safer force pushes on feature branches when necessary, providing a code example.
*   Explicitly warns against using `git push --force` on `main` or other shared branches.
<!-- kody-pr-summary:end -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Updated Git workflow guidance to recommend safer force-push practices and updated examples
  * Strengthened branch-protection guidance with explicit recommended vs. forbidden push examples
  * Clarified squash-merge instructions by splitting GitHub CLI flows into immediate and scheduled merge paths
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
