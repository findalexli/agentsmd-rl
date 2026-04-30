# Add video-chapter CLI command

## Task

Implement a new `video-chapter` CLI command for playwright-cli that allows users to add chapter markers to video recordings. This feature should call the existing `page.overlay.chapter()` API to show full-screen chapter cards during video recording sessions.

## Required Changes

### 1. Backend Tool (`packages/playwright-core/src/tools/backend/video.ts`)

Add a new `videoChapter` tool that:
- Defines a tool named `browser_video_chapter` with capability `devtools`
- Accepts parameters: `title` (string, required), `description` (string, optional), `duration` (number, optional)
- Calls `tab.page.overlay.chapter(title, { description, duration })` to display the chapter card
- Returns a success message via `response.addTextResult()`

Also rename the existing `startVideo` and `stopVideo` variables to `videoStart` and `videoStop` for naming consistency, and update the export array to include all three tools.

### 2. CLI Command (`packages/playwright-core/src/tools/cli-daemon/commands.ts`)

Add a new `videoChapter` command that:
- Uses `declareCommand()` with name `video-chapter` and category `devtools`
- Has a `title` argument (required) and optional `--description` and `--duration` options
- Maps to the `browser_video_chapter` tool
- Include it in the `commandsArray` in the devtools section (after `videoStop`, before `devtoolsShow`)

### 3. Documentation Updates

After implementing the code changes, update the relevant documentation to reflect the new command:

**SKILL.md** (`packages/playwright-core/src/tools/cli-client/skill/SKILL.md`):
- Add the `video-chapter` command to the DevTools examples section
- Show the full command with all available options: `--description` and `--duration`

**video-recording.md** (`packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md`):
- Add chapter marker examples to the video recording workflow
- Show how to add chapters at different points in the recording (e.g., before navigation, before form actions)

**getting-started-cli.md** (`docs/src/getting-started-cli.md`):
- Add `video-chapter` to the CLI command reference list in the DevTools section
- Include a brief description of what the command does

## Context

The `page.overlay.chapter()` API already exists and can display full-screen chapter cards with blurred backdrops during video recording. This is useful for marking section transitions in demo videos. The CLI should expose this functionality to users.

Look at the existing `video-start` and `video-stop` commands as reference for how to implement the new command and tool.

## Notes

- The video-chapter command requires a video recording to be active (started via `video-start`)
- Duration is in milliseconds
- The chapter card will auto-dismiss after the specified duration
- Do not modify the test files (tests/mcp/cli-devtools.spec.ts)
