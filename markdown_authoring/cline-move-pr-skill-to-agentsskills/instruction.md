# Move PR skill to .agents/skills

Source: [cline/cline#9505](https://github.com/cline/cline/pull/9505)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/create-pull-request/SKILL.md`

## What to add / change

### Related Issue

**Issue:** #XXXX

### Description

Moves the `create-pull-request` skill from `.cline/skills/` to `.agents/skills/` and removes changeset guidance (changesets are being removed from the project).

### Test Procedure

Skill files are configuration/documentation only. Verified the file content is correct and the rename was detected properly by git.

### Type of Change

-   [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
-   [ ] ✨ New feature (non-breaking change which adds functionality)
-   [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
-   [ ] ♻️ Refactor Changes
-   [ ] 💅 Cosmetic Changes
-   [ ] 📚 Documentation update
-   [x] 🏃 Workflow Changes

### Pre-flight Checklist

-   [x] Changes are limited to a single feature, bugfix or chore (split larger changes into separate PRs)
-   [x] Tests are passing (`npm test`) and code is formatted and linted (`npm run format && npm run lint`)
-   [x] I have reviewed [contributor guidelines](https://github.com/cline/cline/blob/main/CONTRIBUTING.md)

### Screenshots

N/A - skill file changes only.

### Additional Notes

No changeset needed - this is an internal workflow change with no user-facing impact.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
