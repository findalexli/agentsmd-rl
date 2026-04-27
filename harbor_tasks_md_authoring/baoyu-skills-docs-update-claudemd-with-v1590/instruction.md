# docs: Update CLAUDE.md with v1.59.0 features and skill registry

Source: [JimLiu/baoyu-skills#77](https://github.com/JimLiu/baoyu-skills/pull/77)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
Comprehensive documentation update for CLAUDE.md reflecting the v1.59.0 release, including new skills, official API support, ClawHub registry integration, and improved guidance for skill development.

## Key Changes

- **Version & API Updates**: Updated project version to 1.59.0 and documented support for official AI APIs (OpenAI, Google, DashScope, Replicate) alongside the reverse-engineered Gemini Web API
- **New Skills**: Added documentation for 6 new skills:
  - `baoyu-post-to-weibo` (Weibo posting automation)
  - `baoyu-infographic` (Professional infographics with 21 layouts × 20 styles)
  - `baoyu-image-gen` (Official API image generation backend)
  - `baoyu-url-to-markdown` (URL to markdown conversion via Chrome CDP)
  - `baoyu-format-markdown` (Markdown formatting/beautification)
  - `baoyu-markdown-to-html` (Markdown to styled HTML with WeChat themes)
  - `baoyu-translate` (Multi-mode translation)
- **Repository Structure**: Added `scripts/` directory documentation for maintenance utilities (`sync-clawhub.sh`, `sync-md-to-wechat.sh`)
- **ClawHub/OpenClaw Integration**: Added comprehensive section on publishing skills to ClawHub registry with metadata requirements and sync instructions
- **Skill Development Guidelines**: 
  - Added SKILL.md frontmatter template with openclaw metadata requirements
  - Updated skill structure documentation to clarify optional `scripts/`, `references/`, and `prompts/` directories
  - Enhanced category selection guidance with n

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
