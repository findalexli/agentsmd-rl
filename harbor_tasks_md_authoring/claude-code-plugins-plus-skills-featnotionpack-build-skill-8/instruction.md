# feat(notion-pack): build skill 8/30 — notion-debug-bundle

Source: [jeremylongshore/claude-code-plugins-plus-skills#438](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/438)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/notion-pack/skills/notion-debug-bundle/SKILL.md`

## What to add / change

## Summary
- Rewrites `notion-debug-bundle` SKILL.md with real Notion API diagnostic content
- Step 1: Quick connectivity check (SDK version, token validation with `ntn_` prefix check, `/v1/users/me` auth test, platform status from status.notion.so, rate limit info)
- Step 2: Full debug bundle script collecting environment, API auth, database access, platform status, redacted logs, dependency tree into a tarball
- Step 3: Programmatic TypeScript diagnostics using `@notionhq/client` with auth, database retrieve, and search tests

## Test plan
- [ ] Enterprise validator passes (pack avg 83.2/100)
- [ ] SKILL.md follows format: Frontmatter → Overview → Prerequisites → Instructions (3 steps) → Output → Error Handling → Examples → Resources → Next Steps
- [ ] All curl commands use correct Notion API version header (`Notion-Version: 2022-06-28`)
- [ ] Token redaction covers `ntn_*` and `secret_*` patterns
- [ ] Error handling table covers 6 common Notion API error codes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
