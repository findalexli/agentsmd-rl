# Add video-chapter CLI command and MCP tool

Playwright CLI provides video recording capabilities via `video-start` and `video-stop` commands. We need to add a new `video-chapter` command that allows users to add chapter markers during video recording.

## Functional Requirements

Add a new CLI command `video-chapter` with the following behavior:

1. **Command definition** in `packages/playwright-core/src/tools/cli-daemon/commands.ts`:
   - Command name: `video-chapter`
   - Category: `devtools`
   - Required argument: `title` (string - the chapter title)
   - Optional options: `--description` (string), `--duration` (number in milliseconds)
   - Maps to a backend tool (you'll need to define this too)

2. **Backend tool** in `packages/playwright-core/src/tools/backend/video.ts`:
   - Create a new tool called `videoChapter` following the pattern of `videoStart`/`videoStop`
   - Tool schema name: `browser_video_chapter`
   - Accepts: `title` (required string), `description` (optional string), `duration` (optional number)
   - In the handler, call `tab.page.overlay.chapter(title, options)` to show the chapter card
   - Return a confirmation message like "Chapter '{title}' added."

3. **Export the new tool** in the default exports array

## Documentation Requirements

After implementing the code changes, update the relevant documentation to help users discover and use this feature:

1. **SKILL.md** (`packages/playwright-core/src/tools/cli-client/skill/SKILL.md`):
   - Add `video-chapter` to the DevTools command examples section
   - Show a practical example with `--description` and `--duration` options

2. **video-recording.md** (`packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md`):
   - Add chapter marker examples showing a complete workflow
   - Show how to add chapter markers between actions during recording
   - Include descriptive examples that show real-world usage

3. **getting-started-cli.md** (`docs/src/getting-started-cli.md`):
   - Add the `video-chapter` command to the command reference table

## Notes

- The `overlay.chapter()` API already exists and is documented in `video-recording.md` - it shows a full-screen chapter card with blurred backdrop
- Look at how `videoStart` and `videoStop` are implemented for the pattern to follow
- The PR should include both the functional code changes AND the documentation updates
- Test your changes by running TypeScript compilation: `npx tsc --noEmit`
