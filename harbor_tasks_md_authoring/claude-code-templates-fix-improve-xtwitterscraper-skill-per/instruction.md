# fix: Improve x-twitter-scraper skill per component review

Source: [davila7/claude-code-templates#391](https://github.com/davila7/claude-code-templates/pull/391)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `cli-tool/components/skills/business-marketing/x-twitter-scraper/SKILL.md`

## What to add / change

## Summary
Improvements to the x-twitter-scraper skill from PR #390, based on component-reviewer feedback.

- Move from `marketing/` to `business-marketing/` (correct established category)
- Rewrite description from SEO spam to agent invocation context
- Add agent role, user questions, and decision guidance
- Replace hardcoded API keys with `process.env.XQUIK_API_KEY`
- Use `${XQUIK_API_KEY}` in MCP config instead of placeholder
- Remove duplicate auth blocks in code examples
- Add Related Skills section
- Remove competitor tool mentions

Supersedes #390

## Test plan
- [x] Component-reviewer agent validated (passes with no critical issues)
- [x] Simplify review completed (reuse, quality, efficiency)
- [ ] Verify SKILL.md renders correctly on GitHub
- [ ] Test with `npx claude-code-templates@latest --skill x-twitter-scraper --dry-run`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Improves the x-twitter-scraper skill per component review and moves it to the correct business-marketing category. Adds secure auth and clearer guidance for integrating with Xquik.

- Area: components (cli-tool/components/); new component added at business-marketing/x-twitter-scraper/SKILL.md
- Rewrote content for agent invocation with decision guidance, workflows, and cleaned examples; removed competitor mentions
- Replaced hardcoded keys with process.env.XQUIK_API_KEY and used ${XQUIK_API_KEY} in MCP

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
