# Add `config` command to playwright-cli

## Problem

The `playwright-cli` terminal interface currently has no way to reconfigure a running session with a different config file. Users who want to change browser settings (viewport, context options, etc.) mid-session must manually stop the session, then restart with `--config`. There is also no dedicated `config` category in the command system.

Additionally, when running in headless daemon mode, no default viewport is set, which can lead to inconsistent page dimensions.

## Expected Behavior

1. A new `playwright-cli config <path>` command should allow reconfiguring a session with a new config file. It should stop any existing session, apply the new config, and reconnect.
2. The `config` command should work with named sessions (`--session=mysession config my-config.json`).
3. The command system needs a `config` category in the Category type, the commands array, and the help generator.
4. The default daemon config should set a sensible viewport (1280x720) for headless mode and null viewport for headed mode.
5. The help text for `--config` and `--headed` global options should be updated to clarify they affect session creation.
6. After implementing the code changes, update the relevant skill documentation to cover the new configuration commands so that agents using `playwright-cli` know how to use them.

## Files to Look At

- `packages/playwright/src/mcp/terminal/program.ts` — session management and command routing
- `packages/playwright/src/mcp/terminal/commands.ts` — command declarations
- `packages/playwright/src/mcp/terminal/command.ts` — Category type definition
- `packages/playwright/src/mcp/terminal/helpGenerator.ts` — help text generation
- `packages/playwright/src/mcp/browser/config.ts` — default daemon browser config
- `packages/playwright/src/mcp/terminal/SKILL.md` — skill documentation for agents
