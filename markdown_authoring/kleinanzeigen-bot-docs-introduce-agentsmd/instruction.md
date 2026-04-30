# docs: introduce AGENTS.md

Source: [Second-Hand-Friends/kleinanzeigen-bot#1014](https://github.com/Second-Hand-Friends/kleinanzeigen-bot/pull/1014)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## ℹ️ Description
Introduce `AGENTS.md` as the repo's first agent playbook and contributor quick guide.

- Link to the related issue(s): N/A
- Describe the motivation and context for this change.

## 📋 Changes Summary

- Added `AGENTS.md` to provide repo-specific guidance for contributors and AI agents.
- Documented the source-of-truth hierarchy, testing expectations, PR requirements, and validation steps.
- Kept the guidance concise and aligned with the existing repo docs and workflows.

### ⚙️ Type of Change
Select the type(s) of change(s) included in this pull request:
- [x] 🐞 Bug fix (non-breaking change which fixes an issue)
- [x] ✨ New feature (adds new functionality without breaking existing usage)
- [ ] 💥 Breaking change (changes that might break existing user setups, scripts, or configurations)

## ✅ Checklist
Before requesting a review, confirm the following:
- [x] I have reviewed my changes to ensure they meet the project's standards.
- [x] I have tested my changes and ensured that all tests pass  (`pdm run test`).
- [x] I have formatted the code (`pdm run format`).
- [x] I have verified that linting passes (`pdm run lint`).
- [x] I have updated documentation where necessary.

By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of your choice.

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added contributor guide

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
