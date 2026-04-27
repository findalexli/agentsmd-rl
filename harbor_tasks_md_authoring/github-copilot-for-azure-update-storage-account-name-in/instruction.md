# Update storage account name in analyze-skill-issues skill

Source: [microsoft/GitHub-Copilot-for-Azure#1863](https://github.com/microsoft/GitHub-Copilot-for-Azure/pull/1863)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/analyze-skill-issues/SKILL.md`

## What to add / change

## Description

The data has been migrated to the new storage account. Update the skill to reference the new storage account.

## Checklist

- [ ] Tests pass locally (`cd tests && npm test`)
- [ ] **If modifying skill descriptions:** verified routing correctness with integration tests (`npm run test:skills:integration -- <skill>`)
- [ ] **If modifying skill `USE FOR` / `DO NOT USE FOR` / `PREFER OVER` clauses:** confirmed no routing regressions for competing skills
- [ ] Version bumped in skill frontmatter (if skill files changed)

## Related Issues

<!-- Link to related issues, e.g. Fixes #1234 -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
