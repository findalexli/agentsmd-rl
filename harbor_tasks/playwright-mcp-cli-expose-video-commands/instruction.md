# Expose Video Commands in Playwright MCP CLI

The Playwright MCP CLI needs to expose video recording commands that can be used via the terminal interface.

## Background

The MCP server has tools for browser automation (screenshot, tracing, etc.) but video recording tools are missing from the CLI. Users should be able to start/stop video recording from the terminal.

The Playwright MCP codebase is at `/workspace/playwright/packages/playwright/src/mcp/`.

## Requirements

### 1. Video Tools Module

Create a new `video.ts` module at `packages/playwright/src/mcp/browser/tools/video.ts` that exports two tools:
- `browser_start_video` - Starts video recording on the current page
- `browser_stop_video` - Stops video recording with optional filename parameter

Both tools must use the `'devtools'` capability (not `'tracing'`). The tools should use `defineTabTool` from `./tool` (see `tracing.ts` for the implementation pattern).

### 2. Tool Registry

Update `packages/playwright/src/mcp/browser/tools.ts` to register the video tools:
- Import the video module using the exact statement: `import video from './tools/video';`
- Include video tools in the `browserTools` array using the spread operator: `...video,`
- The import must be alphabetically ordered between `verify` and `wait` imports
- The spread in `browserTools` must be between `...verify,` and `...wait,`

### 3. Rename Capability

The `'tracing'` capability is being generalized to `'devtools'` to include video, tracing, network, and run-code features. Update these files:

- `packages/playwright/src/mcp/config.d.ts` - The `ToolCapability` type must use `'devtools'` instead of `'tracing'` (remove the `'tracing'` entry, add `'devtools'` after `'vision'`)

- `packages/playwright/src/mcp/browser/tools/tracing.ts` - Both `tracingStart` and `tracingStop` tools must have `capability: 'devtools'` (not `'tracing'`)

- `packages/playwright/src/mcp/browser/browserContextFactory.ts` - The capability check must look for `'devtools'` using: `capabilities?.includes('devtools')`

- `packages/playwright/src/mcp/program.ts` - The `--caps` option help text must document `'devtools'` in the possible values: `possible values: vision, pdf, devtools.` The CLI must handle backward compatibility: when `options.caps?.includes('tracing')` is true, execute `options.caps.push('devtools')`

### 4. Terminal Commands

In `packages/playwright/src/mcp/terminal/commands.ts`:

Add a `video-start` command that maps to `browser_start_video` tool:
- Variable name must be `videoStart`
- Must be declared with `declareCommand`
- Must have `name: 'video-start'`
- Must have `category: 'devtools'`
- Must have `toolName: 'browser_start_video'`
- Must have empty args: `args: z.object({})`
- Must have `toolParams: () => ({})`

Add a `video-stop` command with optional `--filename` argument that maps to `browser_stop_video` tool:
- Variable name must be `videoStop`
- Must be declared with `declareCommand`
- Must have `name: 'video-stop'`
- Must have `category: 'devtools'`
- Must have `toolName: 'browser_stop_video'`
- Must have options: `options: z.object({ filename: z.string().optional().describe('Filename to save the video.') })`
- Must have `toolParams: ({ filename }) => ({ filename })`

Register both in `commandsArray` in the devtools section:
- `videoStart,` must appear after `tracingStop,`
- `videoStop,` must appear after `videoStart,`

Move `runCode` command from devtools section to core section:
- The `runCode` variable declaration must appear before the `// Tabs` comment
- In `commandsArray`, `runCode,` must appear after `resize,` and before the `// navigation` section comment

### 5. Output Directory Handling

In `packages/playwright/src/mcp/terminal/program.ts`:
- The MCP server spawn arguments must include: `` `--output-dir=${outputDir}` ``
- The `session.run()` call must pass outputDir as: `session.run({ ...args, outputDir })`

In `packages/playwright/src/mcp/terminal/command.ts`:
- Filename arguments must be resolved against the output directory using: `path.resolve(args.outputDir, args.filename)`
- This requires importing the `path` module at the top of the file

Remove the debug logging statement `console.log(matchingDirs)` from the Session class in `program.ts`.

### 6. Documentation

Update `packages/playwright/src/mcp/terminal/SKILL.md` to document the new video commands in the DevTools section, after the tracing commands:
- `playwright-cli video-start`
- `playwright-cli video-stop video.webm`

These must appear after `playwright-cli tracing-stop` in the code block.

## Reference Files

- `packages/playwright/src/mcp/browser/tools/tracing.ts` - Tool implementation pattern
- `packages/playwright/src/mcp/terminal/commands.ts` - Terminal command pattern
- `packages/playwright/src/mcp/terminal/SKILL.md` - Documentation format
