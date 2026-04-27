# feat(skills): add social-media-posts skill for X and LinkedIn

Source: [ComposioHQ/agent-orchestrator#1498](https://github.com/ComposioHQ/agent-orchestrator/pull/1498)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/social-media/SKILL.md`

## What to add / change

## What

Adds a new skill `skills/social-media/SKILL.md` for drafting platform-optimized social media posts.

## What it covers
- **X (Twitter):** Single posts (280/600 char), threads with hook→story→CTA structure, no-hashtag default
- **LinkedIn:** 150-300 word posts, Unicode bold formatting, arrow bullets, section breaks
- **Post types:** Milestone celebrations, product launches, hot takes, article promotion
- **Style guide:** Builder tone, banned phrases list, specific-over-vague numbers
- **Output:** Copy-paste ready code blocks per platform

## Why
Needed a consistent voice and format for social content around releases, milestones, and feature ships. No more ad-hoc drafting — load the skill and follow the structure.

## Usage
```
Load skill: social-media-posts
Then ask: "Write an X thread for the v0.3.0 release" or "Draft a LinkedIn post for 6K stars"
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
