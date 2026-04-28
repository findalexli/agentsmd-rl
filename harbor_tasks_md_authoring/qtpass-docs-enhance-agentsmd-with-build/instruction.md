# docs: enhance AGENTS.md with build variants and signing guidance

Source: [IJHack/QtPass#1152](https://github.com/IJHack/QtPass/pull/1152)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- kody-pr-summary:start -->
This pull request updates the `AGENTS.md` file to improve development guidance and clarity.

Key changes include:
*   **Build Instructions:** Added explicit Qt 5 alternative commands for full builds and coverage alongside the existing Qt 6 commands.
*   **Commit Signing:** Enhanced the commit signing section with prerequisites and verification steps for using `git commit -S`.
*   **Key Conventions:** Clarified the reason for using `QCoreApplication::arguments()` by noting its benefits for Unicode handling and cross-platform consistency.
*   **Path Normalization:** Refined the explanation of `QDir::cleanPath()` to emphasize that it normalizes path separators to forward slashes on all platforms.
<!-- kody-pr-summary:end -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated build instructions to cover Qt 6 and Qt 5 builds and coverage runs
  * Expanded Git workflow guidance for signed commits with prerequisites and verification steps
  * Enhanced key conventions documentation for CLI Unicode and cross-platform compatibility
  * Clarified path-boundary handling explanations for improved clarity

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
