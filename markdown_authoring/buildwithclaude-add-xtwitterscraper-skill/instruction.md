# Add x-twitter-scraper skill

Source: [davepoon/buildwithclaude#69](https://github.com/davepoon/buildwithclaude/pull/69)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/x-twitter-scraper/SKILL.md`

## What to add / change

## Summary

Adds the x-twitter-scraper skill for [Xquik](https://xquik.com), an X (Twitter) real-time data platform. Provides a REST API, MCP server (22 tools), and HMAC webhooks covering tweet search, user profiles, bulk extraction (19 tool types), giveaway draws, account monitoring, follow checks, and trending topics.

## Component Details

- **Name**: x-twitter-scraper
- **Type**: Skill
- **Category**: social-media

## Testing

- [x] Tested MCP server connectivity via Claude Code and Cursor
- [x] Verified REST API endpoints with live data
- [x] No overlap with existing twitter-automation skill (that one uses Composio/Rube MCP for posting & OAuth actions; this one is read-only data extraction & monitoring via Xquik's own API)

## Examples

**Search tweets and get metrics:**
> "Search for tweets about 'AI agents' from the last week, then show me engagement metrics for the top result"

Uses `search-tweets` to find tweets, then `lookup-tweet` to get like/retweet/view counts.

**Extract followers and check relationships:**
> "Get the followers of @anthropic and check if @OpenAI follows them"

Uses `estimate-extraction` + `run-extraction` with `follower_explorer`, then `check-follow` for the relationship check.

**Set up real-time monitoring:**
> "Monitor @elonmusk for new tweets and send notifications to my webhook at https://example.com/hook"

Uses `add-monitor` to start tracking, `add-webhook` to register the endpoint, `test-webhook` to verify delivery.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
