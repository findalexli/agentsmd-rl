# Add faceswap skill for AI face swapping in video via Node Gateway

Source: [heygen-com/skills#20](https://github.com/heygen-com/skills/pull/20)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/faceswap/SKILL.md`

## What to add / change

## Add HeyGen Face Swap Skill

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

This pull request adds a new skill for performing AI-powered face swapping using the HeyGen API. The skill enables swapping faces from a source image into a target video through HeyGen's `/v1/nodes/executions` endpoint with the `FaceswapNode` type.

### Key Features

- **Face Swap Processing**: Swap faces from source images into target videos using GPU-accelerated AI
- **Async Workflow**: Submit face swap jobs and poll for completion with proper status handling
- **Authentication**: Requires `HEYGEN_API_KEY` environment variable for API access
- **Comprehensive Documentation**: Includes curl, TypeScript, and Python examples with complete request/response formats

### API Integration

The skill provides a complete workflow for:
1. Submitting face swap requests with source image and target video URLs
2. Polling execution status until completion
3. Retrieving the final processed video URL
4. Error handling for failed or timed-out operations

### Use Cases

- Replacing faces in existing videos with custom faces
- Creating personalized avatar videos by combining generated content with face swapping
- Processing video content for face replacement applications
- Integrating with other HeyGen nodes for complete video generation pipelines

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
