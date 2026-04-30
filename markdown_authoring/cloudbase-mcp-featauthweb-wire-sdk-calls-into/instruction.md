# feat(auth-web): ✨ wire SDK calls into form handlers

Source: [TencentCloudBase/CloudBase-MCP#412](https://github.com/TencentCloudBase/CloudBase-MCP/pull/412)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `config/source/skills/auth-web/SKILL.md`

## What to add / change

## Summary

- Fixes the guidance gap behind attribution `issue_mn47mb08_la997y`.
- Strengthens `auth-web` so agents connect `auth.signUp` / `verifyOtp` directly inside existing form handlers instead of leaving SDK calls isolated in a helper file.

## Evidence

- Representative run: `application-js-react-cloudbase-signup/2026-03-24T05-54-11-lc4z2m`
- Failure signal: `调用 CloudBase SDK` remained the only failed check because the UI handlers in `App.tsx` were still TODO while the SDK calls lived in a detached helper path.

## Validation

- Rebuilt compat config from the local skill source.
- Rebuilt `mcp` package so a fresh evaluation can reference a local `dist/cli.cjs`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
