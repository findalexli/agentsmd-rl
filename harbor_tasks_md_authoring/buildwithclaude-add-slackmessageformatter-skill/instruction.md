# Add slack-message-formatter skill

Source: [davepoon/buildwithclaude#87](https://github.com/davepoon/buildwithclaude/pull/87)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/slack-message-formatter/SKILL.md`

## What to add / change

## Summary
- Adds **slack-message-formatter**, a skill that converts Markdown to pixel-perfect Slack output via two paths: rich HTML (copy-paste into Slack) and Slack mrkdwn (API/webhook delivery)
- Generates a Slack-themed browser preview and auto-copies rich HTML to the clipboard for one-step paste
- Supports tables, task lists, code blocks, nested lists, 150+ emoji shortcodes, and Slack mentions

## Component Details
- **Name**: slack-message-formatter
- **Type**: Skill
- **Category**: communication

## Testing
- [x] Tested functionality — 166 passing tests covering HTML conversion, mrkdwn conversion, emoji mapping, tables, edge cases
- [x] No overlap with existing components — no existing Slack formatting skill in the marketplace
- [x] Follows SKILL.md frontmatter and structure conventions

## Examples

1. **Write a Slack announcement**
   ```
   Write a Slack message announcing our Q2 product launch
   ```
   Generates Markdown, converts to rich HTML, opens a Slack-themed preview in the browser, and copies to clipboard. User pastes into Slack with Cmd+V.

2. **Format existing content for Slack**
   ```
   Format this for Slack: We shipped 3 new features this week...
   ```
   Takes the content, converts it to properly formatted Slack output with bold, links, lists, and emoji rendered correctly.

3. **Send via webhook**
   ```
   Send a deploy notification to Slack via webhook
   ```
   Converts to mrkdwn and sends directly to a Slack channel via the configured webhook UR

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
