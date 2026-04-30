# Add morning-ai skill

Source: [davepoon/buildwithclaude#127](https://github.com/davepoon/buildwithclaude/pull/127)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/morning-ai/SKILL.md`

## What to add / change

## Summary
Brief description of the contribution

Adds MorningAI as a skill — an AI news tracker that monitors 80+ entities across 6 free sources (Reddit, HN, GitHub, HuggingFace, arXiv, X/Twitter), generates scored daily reports with infographics and message digests.

## Component Details
- **Name**: morning-ai
- **Type**: Skill
- **Category**: data-ai

## Testing
- [x] No overlap with existing components
- [x] Tested functionality — the skill runs via `/morning-ai` and produces scored Markdown reports

## Examples
1. `/morning-ai` — Generate today's AI news report
2. `/morning-ai --lang zh` — Generate report in Chinese
3. `/morning-ai --depth deep` — Deep analysis mode with more detail

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
