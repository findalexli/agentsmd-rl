# Plugin: add project manager skill gotchas

Source: [pwrdrvr/openclaw-codex-app-server#23](https://github.com/pwrdrvr/openclaw-codex-app-server/pull/23)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/project-manager/SKILL.md`

## What to add / change

## Summary
- update the repo-local `project-manager` skill to reflect the derived tracker workflow
- add gotchas for the canonical repo slug, opaque project field ids, and GitHub Projects view limitations
- document that the local tracker sync is issue-only while PRs still belong on project 7

## Validation
- reviewed the skill against the actual `gh` commands and failures from this repo workflow
- did not run `pnpm test`
- did not run `pnpm typecheck`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
