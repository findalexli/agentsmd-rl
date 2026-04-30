# Add skills

Source: [microsoft/GitHub-Copilot-for-Azure#1910](https://github.com/microsoft/GitHub-Copilot-for-Azure/pull/1910)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/investigate-integration-test/SKILL.md`
- `.github/skills/submit-skill-fix-pr/SKILL.md`

## What to add / change

Add skills for investigating integration test failures and submitting PRs with fixes.

## Description

I find myself performing the same operations each time I investigate and fix an integration test failure. Here I've moved most of the relevant information into new skills.

## Checklist

- [ ] Tests pass locally (`cd tests && npm test`)
- [ ] **If modifying skill descriptions:** verified routing correctness with integration tests (`npm run test:skills:integration -- <skill>`)
- [ ] **If modifying skill `USE FOR` / `DO NOT USE FOR` / `PREFER OVER` clauses:** confirmed no routing regressions for competing skills
- [ ] Version bumped in skill frontmatter (if skill files changed)

## Related Issues

_N/A_

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
