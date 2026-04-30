# Add agent-analytics skill

Source: [davepoon/buildwithclaude#66](https://github.com/davepoon/buildwithclaude/pull/66)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/agent-analytics/SKILL.md`

## What to add / change

## Summary

- Adds Agent Analytics skill to the all-skills collection
- Analytics platform built for AI agents — track, analyze, run A/B experiments, and optimize across multiple projects via CLI

## Component Details
- **Name**: agent-analytics
- **Type**: Skill
- **Category**: analytics

## Testing
- [x] Tested functionality
- [x] No overlap with existing components (existing analytics skills like mixpanel-automation and amplitude-automation use Rube MCP/Composio — this is a standalone platform with its own CLI)

## Examples

1. "How are my projects doing?" — agent checks traffic, funnels, and experiments across all projects in one query
2. "Signup funnel has 68% drop-off at step 2" — agent creates an A/B test, monitors significance, and recommends shipping the winner
3. "Set up tracking on my new landing page" — agent wires up event tracking on CTAs and key actions via the API

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
