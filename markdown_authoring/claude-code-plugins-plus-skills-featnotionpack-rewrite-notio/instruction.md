# feat(notion-pack): rewrite notion-enterprise-rbac (skill 23/32)

Source: [jeremylongshore/claude-code-plugins-plus-skills#475](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/475)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/notion-pack/skills/notion-enterprise-rbac/SKILL.md`

## What to add / change

## Summary
- Rewrote `notion-enterprise-rbac` with complete OAuth 2.0 and RBAC implementation
- Full OAuth authorization flow with CSRF protection (TypeScript + Python)
- Per-workspace token store with encryption-at-rest guidance
- Permission-aware API calls distinguishing ObjectNotFound vs RestrictedResource vs Unauthorized
- Content discovery via `search` endpoint
- Application-level role system (admin/editor/viewer) with Express middleware
- Audit logging to structured logs and optionally to a Notion audit database
- Workspace deauthorization cleanup handler

## Test plan
- [ ] Validate with `python3 scripts/validate-skills-schema.py --enterprise plugins/saas-packs/notion-pack/`
- [ ] Verify OAuth endpoints match Notion's current API spec

Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
