# docs: update AGENTS.md with niche knowledge

Source: [IJHack/QtPass#1149](https://github.com/IJHack/QtPass/pull/1149)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- kody-pr-summary:start -->
Removed several sections from `AGENTS.md` that detailed internal development patterns and best practices. The removed content included guidelines on:
*   Managing profile-specific Git settings.
*   Using the `QSettings` singleton pattern via `QtPassSettings::getInstance()`.
*   The pattern for adding new password entries in `MainWindow`.
*   Handling profile table selection changes in `ConfigDialog`.
*   Avoiding setter side effects within loops when loading settings.
<!-- kody-pr-summary:end -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Removed developer implementation guidance from internal documentation, including instructions on profile Git settings storage, configuration dialog handling, testing procedures, and dialog/template wiring patterns.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
