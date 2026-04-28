# chore: fix duplicated content in architecture.mdc

Source: [oraxen/oraxen#1692](https://github.com/oraxen/oraxen/pull/1692)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/architecture.mdc`

## What to add / change

- Remove duplicate sections in .cursor/rules/architecture.mdc
- Update NMS version references to include v1_21_R6

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Deduplicates the architecture guide, updates NMS version references to v1_21_R6, and refreshes the Development Workflow instructions.
> 
> - **Docs (`.cursor/rules/architecture.mdc`)**:
>   - Remove duplicated sections throughout the file.
>   - Update NMS module range to `v1_21_R6` and example `NMSHandler` path.
>   - Normalize wording (e.g., repository apostrophe usage).
>   - Refresh **Development Workflow** with Docker-based local server instructions.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit da6a9210fe4aa4aa85aacbe791048a38fc002339. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
