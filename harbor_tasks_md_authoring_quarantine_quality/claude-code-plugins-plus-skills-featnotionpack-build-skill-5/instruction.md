# feat(notion-pack): build skill 5/30 — notion-common-errors

Source: [jeremylongshore/claude-code-plugins-plus-skills#429](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/429)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/notion-pack/skills/notion-common-errors/SKILL.md`

## What to add / change

## Summary
- Rewrote `notion-common-errors` SKILL.md with real Notion API error codes, HTTP statuses, and production-grade fixes
- Covers all 8 error types: `unauthorized` (401), `restricted_resource` (403), `object_not_found` (404), `validation_error` (400), `rate_limited` (429), `conflict_error` (409), `internal_server_error` (500), `service_unavailable` (502/503)
- Added full SDK error handler example using `isNotionClientError()` type guard and `APIErrorCode` enum
- Includes common gotchas: page ID format (dashes vs no dashes), rich text array structure, filter type mismatches, block type structure
- Error table expanded to 9 rows with gateway_timeout (504)
- Added diagnostic script with status check, token verification, and database access test

## Test plan
- [ ] `python3 scripts/validate-skills-schema.py --enterprise plugins/saas-packs/notion-pack/` passes (83.1 avg)
- [ ] SKILL.md follows format: Frontmatter → Overview → Prerequisites → Instructions (Step headings) → Output → Error Handling (9 rows) → Examples → Resources → Next Steps
- [ ] All error codes match official Notion API documentation
- [ ] Code examples use `@notionhq/client` SDK with proper TypeScript types

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
