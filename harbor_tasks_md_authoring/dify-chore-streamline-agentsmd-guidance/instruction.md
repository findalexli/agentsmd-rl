# chore: streamline AGENTS.md guidance

Source: [langgenius/dify#26308](https://github.com/langgenius/dify/pull/26308)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- streamline `AGENTS.md` so the backend workflow highlights the required QA gate
- remove redundant command listings that duplicate Makefile targets or encourage local integration test runs
- clarify ongoing language, style, and practice expectations for agents without extra boilerplate

Fixes #26307

## Screenshots

| Before | After |
|--------|-------|
| N/A | N/A |

## Checklist

- [ ] This change requires a documentation update, included: [Dify Document](https://github.com/langgenius/dify-docs)
- [x] I understand that this PR may be closed in case there was no previous discussion or issues. (This doesn't apply to typos!)
- [ ] I've added a test for each change that was introduced, and I tried as much as possible to make a single atomic change.
- [x] I've updated the documentation accordingly.
- [ ] I ran `dev/reformat`(backend) and `cd web && npx lint-staged`(frontend) to appease the lint gods

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
