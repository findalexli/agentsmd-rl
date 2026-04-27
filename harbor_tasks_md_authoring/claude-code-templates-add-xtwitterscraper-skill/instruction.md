# Add x-twitter-scraper skill

Source: [davila7/claude-code-templates#390](https://github.com/davila7/claude-code-templates/pull/390)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `cli-tool/components/skills/marketing/x-twitter-scraper/SKILL.md`

## What to add / change

## Summary

Adds an X (Twitter) data skill under `marketing/x-twitter-scraper`. It teaches Claude Code how to work with the [Xquik](https://xquik.com) REST API, MCP server, and webhooks.

What the skill covers:
- Tweet search, user profiles, engagement metrics, follow checks
- 19 bulk extraction tools (followers, replies, reposts, quotes, communities, Spaces, etc.)
- Giveaway draws with filters (must retweet, min followers, required hashtags, etc.)
- Real-time account monitoring via webhooks
- Trending topics
- MCP server config for Claude Code (`.mcp.json` snippet included)

Full skill source: [github.com/Xquik-dev/x-twitter-scraper](https://github.com/Xquik-dev/x-twitter-scraper)
API docs: [docs.xquik.com](https://docs.xquik.com)

## Test plan

- [ ] Verify SKILL.md renders correctly on GitHub
- [ ] Check YAML frontmatter has `name` and `description`
- [ ] Confirm code examples are syntactically valid
- [ ] Test with `npx claude-code-templates@latest --skill x-twitter-scraper --dry-run` if possible

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Adds a new X (Twitter) data skill at cli-tool/components/skills/marketing/x-twitter-scraper. It documents how to use the Xquik REST API, webhooks, and MCP for search, extractions, giveaways, trending, and monitoring.

- Area: components (cli-tool/components/)
- New component added (marketing/x-twitter-scraper); regenerate docs/components.json
- No changes to CLI, API, website, or workers
- Requires 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
