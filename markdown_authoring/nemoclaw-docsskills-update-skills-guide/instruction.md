# docs(skills): update skills guide

Source: [NVIDIA/NemoClaw#1646](https://github.com/NVIDIA/NemoClaw/pull/1646)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/nemoclaw-skills-guide/SKILL.md`

## What to add / change

<!-- markdownlint-disable MD041 -->
## Summary

Usage tested in Cursor: 

<img width="691" height="1119" alt="Screenshot 2026-04-08 at 4 09 34 PM" src="https://github.com/user-attachments/assets/d7bba3e9-ab90-4d1f-9420-22707cb84800" />



## Related Issue
<!-- Link to the issue: Fixes #NNN or Closes #NNN. Remove this section if none. -->

## Changes
<!-- Bullet list of key changes. -->

## Type of Change
<!-- Check the one that applies. -->
- [ ] Code change for a new feature, bug fix, or refactor.
- [ ] Code change with doc updates.
- [x] Doc only. Prose changes without code sample modifications.
- [ ] Doc only. Includes code sample changes.

## Testing
<!-- What testing was done? -->
- [ ] `npx prek run --all-files` passes (or equivalently `make check`).
- [ ] `npm test` passes.
- [ ] `make docs` builds without warnings. (for doc-only changes)

## Checklist

### General

- [x] I have read and followed the [contributing guide](https://github.com/NVIDIA/NemoClaw/blob/main/CONTRIBUTING.md).
- [x] I have read and followed the [style guide](https://github.com/NVIDIA/NemoClaw/blob/main/docs/CONTRIBUTING.md). (for doc-only changes)

### Code Changes
<!-- Skip if this is a doc-only PR. -->
- [ ] Formatters applied — `npx prek run --all-files` auto-fixes formatting (or `make format` for targeted runs).
- [ ] Tests added or updated for new or changed behavior.
- [x] No secrets, API keys, or credentials committed.
- [ ] Doc pages updated for any

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
