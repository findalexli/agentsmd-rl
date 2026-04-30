# docs: fix release note writer guidance spelling

Source: [microsoft/vscode-docs#9674](https://github.com/microsoft/vscode-docs/pull/9674)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/release-note-writer/SKILL.md`

## What to add / change

Summary
- fix the "initially" spelling in the release-note-writer skill guidance

Related issue
- N/A (trivial docs typo fix)

Guideline alignment
- docs-only wording fix in one file
- no behavior changes

Validation
- Ran `git diff --check`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
