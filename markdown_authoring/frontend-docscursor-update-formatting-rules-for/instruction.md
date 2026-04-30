# docs(cursor): update formatting rules for component files

Source: [codecrafters-io/frontend#3601](https://github.com/codecrafters-io/frontend/pull/3601)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/formatting-component-files.mdc`

## What to add / change

Add guidance to use `await` when calling `task.perform()` in lifecycle
hooks like `handleDidInsert` to ensure tests wait for async operations
to complete. This improves test reliability and clarity.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Updates the component formatting rules documentation.
> 
> - Adds guidance to `await` `task.perform()` in lifecycle hooks (e.g., `handleDidInsert`) so tests properly wait for async operations
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit f53254565794760e84e08cc667240a6bfd38c34d. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
