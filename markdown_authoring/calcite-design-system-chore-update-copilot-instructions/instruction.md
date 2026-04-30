# chore: update copilot instructions

Source: [Esri/calcite-design-system#14233](https://github.com/Esri/calcite-design-system/pull/14233)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

**Related Issue:** #14022 

## Summary

Follow-up to address [notes](https://github.com/Esri/calcite-design-system/pull/14149#pullrequestreview-4071442824) on PR #14149.

Updates the repository’s GitHub Copilot custom instructions to better reflect preferred workflows and review practices for this monorepo.

**Changes:**

- Adds guidance around limiting edits to internal/private workspace packages and proposing modern web patterns with references before applying them.
- Adjusts TypeScript guidance and updates testing guidance to reference Vitest browser tests/locators.
- Adds a review-writing tip to label comment intent (e.g., `nit`, `suggestion`) and reiterates using CSS classes in stories.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
