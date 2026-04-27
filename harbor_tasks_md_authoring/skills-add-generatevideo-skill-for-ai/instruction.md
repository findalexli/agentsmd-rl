# Add generate-video skill for AI video generation via Node Gateway

Source: [heygen-com/skills#19](https://github.com/heygen-com/skills/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ai-video-gen/SKILL.md`

## What to add / change

## Add HeyGen video generation skill

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

This adds a new skill for generating AI videos from text prompts using the HeyGen API. The skill supports:

- Multiple video generation providers (VEO 3.1, Kling, Sora, Runway, Seedance, LTX)
- Configurable aspect ratios (16:9, 9:16, 1:1)
- Image-to-video generation with reference images
- Text-to-video generation with detailed prompts
- Polling workflow for checking generation status

The skill includes comprehensive documentation with curl examples, TypeScript/Python code samples, and best practices for prompt engineering and provider selection. It requires the `HEYGEN_API_KEY` environment variable and uses the HeyGen `/v1/nodes/executions` endpoint.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
