# Add video-chapter CLI Command

Implement a new `video-chapter` CLI command for playwright-cli that allows users to add chapter markers to video recordings. Chapter markers show full-screen chapter cards with a blurred backdrop during video recording, making it easier to navigate long recordings.

## Functional Requirements

1. **Add CLI command** in `packages/playwright-core/src/tools/cli-daemon/commands.ts`:
   - Command name: `video-chapter`
   - Required argument: `title` (the chapter title)
   - Optional flags: `--description`, `--duration` (in milliseconds)
   - Category: `devtools`
   - The command should call the `browser_video_chapter` tool

2. **Add MCP tool** in `packages/playwright-core/src/tools/backend/video.ts`:
   - Tool name: `browser_video_chapter`
   - Parameters: `title` (string), `description` (string, optional), `duration` (number, optional)
   - Implementation should call `tab.page.overlay.chapter()` with the provided parameters
   - Return a confirmation message like "Chapter '{title}' added."
   - Export the new tool from the module

3. **Rename existing tools** for consistency:
   - Rename `startVideo` to `videoStart`
   - Rename `stopVideo` to `videoStop`
   - Update the default export array to include the new `videoChapter` tool

## Documentation Requirements

The skill documentation must be updated to include the new command. After implementing the code:

1. **Update SKILL.md** (`packages/playwright-core/src/tools/cli-client/skill/SKILL.md`):
   - Add `video-chapter` to the DevTools command examples
   - Show usage with title, description, and duration options

2. **Update video-recording.md** (`packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md`):
   - Add examples showing chapter markers at section transitions
   - Demonstrate realistic usage patterns (e.g., "Getting Started", "Filling Form")

3. **Update getting-started-cli.md** (`docs/src/getting-started-cli.md`):
   - Add the video-chapter command to the quick reference table

## Files to Modify

- `packages/playwright-core/src/tools/cli-daemon/commands.ts` - Add CLI command
- `packages/playwright-core/src/tools/backend/video.ts` - Add MCP tool, rename existing tools
- `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` - Document command
- `packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md` - Add usage examples
- `docs/src/getting-started-cli.md` - Add to command list

## Example Usage

```bash
playwright-cli video-start
playwright-cli video-chapter "Introduction" --description="Opening page" --duration=2000
playwright-cli goto https://example.com
playwright-cli video-chapter "Navigation" --description="Navigating to form"
playwright-cli video-stop
```

The chapter markers should display as full-screen cards with the title, optional description, and a blurred backdrop for the specified duration.
