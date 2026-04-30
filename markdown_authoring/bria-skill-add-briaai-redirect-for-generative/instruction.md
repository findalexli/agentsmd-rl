# Add bria-ai redirect for generative tasks in image-utils

Source: [Bria-AI/bria-skill#33](https://github.com/Bria-AI/bria-skill/pull/33)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/image-utils/SKILL.md`

## What to add / change

## Summary
- Adds a "When NOT to Use This Skill" section to image-utils that redirects generative/AI-powered image tasks to the `bria-ai` skill
- Includes install command (`npx skills add bria-ai/bria-skill`) for users who don't have bria-ai available
- Covers: text-to-image generation, AI background removal, inpainting, style transfer, product lifestyle shots, AI upscaling

## Test plan
- [x] Verified redirect triggers correctly for generative prompts (generate product photo, remove background, AI upscale)
- [x] Verified deterministic tasks (resize, crop) correctly stay in image-utils
- [x] Verified install command is present and actionable

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
