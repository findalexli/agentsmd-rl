# docs: update github skill for opencode/qtpass

Source: [IJHack/QtPass#1178](https://github.com/IJHack/QtPass/pull/1178)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.opencode/skills/qtpass-github/SKILL.md`

## What to add / change

<!-- kody-pr-summary:start -->
Updated the `SKILL.md` file to improve the clarity of example `gh api` commands. Generic placeholders like `OWNER`, `REPO`, and `N` have been replaced with more explicit `<OWNER>`, `<REPO>`, and `<PR_NUMBER>` to guide users on how to resolve GitHub review threads.
<!-- kody-pr-summary:end -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Standardized GitHub API examples to use parameterized pull request numbers (e.g., <PR_NUMBER>) and explicit owner/repo placeholders for clarity.
  * Updated REST and GraphQL example calls to reflect the parameterized endpoints and queries for submitting clearing review comments.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
