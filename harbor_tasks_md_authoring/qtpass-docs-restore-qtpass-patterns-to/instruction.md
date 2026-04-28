# docs: restore QtPass patterns to AGENTS.md

Source: [IJHack/QtPass#1153](https://github.com/IJHack/QtPass/pull/1153)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- kody-pr-summary:start -->
This pull request updates `AGENTS.md` by adding several documentation sections detailing common patterns and best practices within the QtPass codebase.

The added sections include:
*   **Profile Git Settings**: Explains how Git-related options (useGit, autoPush, autoPull) are managed and stored per-profile using `QtPassSettings`, and how to handle profile settings in `ConfigDialog`.
*   **QSettings Singleton Pattern**: Documents the use of `QtPassSettings::getInstance()` as the standard way to interact with application settings, advising consistency in tests.
*   **MainWindow Add Entry Pattern**: Provides a code example illustrating the process of adding a new password entry via `MainWindow::addPasswordEntry()`, including template handling.
*   **ConfigDialog Profile Table Selection**: Describes the logic for loading profile-specific Git settings when a profile is selected in the `ConfigDialog`'s profile table.
*   **Avoid Setter Side Effects in Loops**: Offers guidance on preventing unintended side effects by demonstrating how to update UI elements efficiently without triggering update logic for each item in a loop.
<!-- kody-pr-summary:end -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Expanded developer documentation on configuration and profile handling to improve reliability of profile-specific settings (including Git-related options), settings persistence ac

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
