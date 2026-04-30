# fix: code quality findings from AI analysis

Source: [IJHack/QtPass#1181](https://github.com/IJHack/QtPass/pull/1181)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.opencode/skills/qtpass-github/SKILL.md`

## What to add / change

<!-- kody-pr-summary:start -->
Documentation improvements for `.opencode/skills/qtpass-github/SKILL.md`:

*   Clarified the comment regarding adding an upstream remote, specifying it as a "one-time setup."
*   Enhanced instructions for resolving GitHub pull request review threads by adding a comment explaining how to obtain the `THREAD_ID` from previous step output and updating the placeholder value.
<!-- kody-pr-summary:end -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Clarified instructions for syncing with the main branch, including one-time remote setup guidance
  * Improved thread resolution examples with concrete reference values for better clarity

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
