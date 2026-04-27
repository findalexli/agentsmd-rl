# docs(skill): add bisect-published-versions playwright-dev guide

Source: [microsoft/playwright#40169](https://github.com/microsoft/playwright/pull/40169)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/playwright-dev/SKILL.md`
- `.claude/skills/playwright-dev/bisect-published-versions.md`

## What to add / change

## Summary
- New `.claude/skills/playwright-dev/bisect-published-versions.md` documenting the side-by-side npm install workflow for reproducing regressions across published Playwright versions.
- Covers setup pitfalls (avoid `npm init playwright@latest` interactive scaffold, single chromium project), where to look in compiled `node_modules/.../lib/`, in-place patching to verify fixes, and reporting back to issues.
- Indexed in `.claude/skills/playwright-dev/SKILL.md`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
