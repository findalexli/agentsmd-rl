# feat(notion-pack): build skill 3/30 — notion-local-dev-loop

Source: [jeremylongshore/claude-code-plugins-plus-skills#428](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/428)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/notion-pack/skills/notion-local-dev-loop/SKILL.md`

## What to add / change

## Summary
- Rewrote `notion-local-dev-loop` SKILL.md from a generic dev setup guide into a comprehensive Notion-specific local development workflow
- Covers creating a dedicated dev integration with separate `ntn_dev_*` token, isolating dev from production
- Adds singleton client with exponential backoff retry for Notion's 3 req/s rate limit
- Includes full unit test mocking (`vi.mock('@notionhq/client')`) and gated integration tests
- Dual language examples: TypeScript (vitest) and Python (notion-client + pytest)

## Test plan
- [x] Enterprise validator passes (83.3 avg across all 30 notion-pack skills)
- [ ] CI validation passes
- [ ] Skill renders correctly in marketplace build

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
