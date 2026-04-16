# Add Config Command to Playwright CLI

The playwright-cli MCP terminal needs a new `config` command that allows users to reconfigure an existing session with a new configuration file without restarting the entire CLI.

## Functional Changes Needed

1. **Add the config command** to `packages/playwright/src/mcp/terminal/commands.ts`:
   - Create a new command declaration named `config`
   - Category should be `config`
   - Description: "Restart session with new config, defaults to `playwright-cli.json`"
   - Accept an optional `config` argument for the path to the configuration file

2. **Update the Category type** in `packages/playwright/src/mcp/terminal/command.ts` to include `'config'`

3. **Update help generator** in `packages/playwright/src/mcp/terminal/helpGenerator.ts`:
   - Add the `config` category to the categories list
   - Update the `--config` option description to be clearer about creating sessions with custom config

4. **Implement the configure logic** in `packages/playwright/src/mcp/terminal/program.ts`:
   - Refactor `SessionManager.list()` to return `Map<string, boolean>` instead of `{name: string, live: boolean}[]`
   - Add a `configure()` method that stops the current session (if running), applies the new config, and reconnects
   - Handle the `config` command in `handleSessionCommand()`
   - Show the config file path as relative to current working directory when logging

5. **Update browser config** in `packages/playwright/src/mcp/browser/config.ts`:
   - Add `contextOptions.viewport` to the default daemon config
   - Use `null` when headed, or `{ width: 1280, height: 720 }` when headless

## Documentation Update Required

After implementing the code changes, update the SKILL.md file at `packages/playwright/src/mcp/terminal/SKILL.md`:

- Add a new "### Configuration" section between the "DevTools" and "Sessions" sections
- Include example bash commands showing:
  - Basic config usage: `playwright-cli config my-config.json`
  - Config for named sessions: `playwright-cli --session=mysession config my-config.json`
  - Starting with config: `playwright-cli open --config=my-config.json`

Follow the existing formatting style in SKILL.md - use backticks around commands and follow the structure of other sections like "DevTools" and "Sessions".

## Files to Modify

- `packages/playwright/src/mcp/terminal/commands.ts`
- `packages/playwright/src/mcp/terminal/command.ts`
- `packages/playwright/src/mcp/terminal/helpGenerator.ts`
- `packages/playwright/src/mcp/terminal/program.ts`
- `packages/playwright/src/mcp/browser/config.ts`
- `packages/playwright/src/mcp/terminal/SKILL.md`

## Testing

After making changes:
1. Run `npm run build` to compile TypeScript
2. Run `npm run tsc` to verify no type errors
3. Test the CLI help with `node packages/playwright/lib/mcp/terminal/cli.js --help`
