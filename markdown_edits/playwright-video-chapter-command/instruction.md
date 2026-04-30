# Add video-chapter CLI command

## Problem

Playwright's `playwright-cli` supports video recording with `video-start` and `video-stop`, but there is no way to add chapter markers during recording. Users recording demo videos or documentation walkthroughs have no way to visually separate sections of a video with title cards.

The underlying `page.overlay.chapter()` API already exists in Playwright's browser automation layer, but it has no corresponding MCP tool or CLI command to expose it.

## Expected Behavior

A new `video-chapter` command should be added that:
1. Accepts a chapter title as a positional argument
2. Supports optional `--description` and `--duration` options
3. Calls the overlay chapter API to show a full-screen chapter card with blurred backdrop during video recording

This requires both an MCP tool definition (backend) and a CLI command declaration (daemon), following the existing patterns for `video-start` and `video-stop`.

After implementing the code changes, update the relevant skill documentation and reference files to document the new command. The project's development guide specifies that CLI commands must be reflected in the skill file and reference docs.

## Files to Look At

- `packages/playwright-core/src/tools/backend/video.ts` — MCP tool definitions for video recording
- `packages/playwright-core/src/tools/cli-daemon/commands.ts` — CLI command declarations
- `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` — Skill documentation listing all commands
- `packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md` — Video recording reference guide
- `docs/src/getting-started-cli.md` — Getting started CLI documentation
- `.claude/skills/playwright-dev/tools.md` — Development guide for adding MCP tools and CLI commands
