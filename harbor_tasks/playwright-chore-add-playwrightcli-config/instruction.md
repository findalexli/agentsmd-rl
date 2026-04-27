# Add `config` command to playwright-cli

## Problem

The `playwright-cli` terminal tool lets users manage browser sessions (open, close, session-list, etc.) but has no way to reconfigure a running session with a different config file. Users who want to change viewport, context options, or other config must manually stop and restart the session with new flags.

## Expected Behavior

A new `config` command should allow restarting the current session with a different configuration file:

1. Accept an optional path to a JSON config file (defaults to `playwright-cli.json`)
2. If a session is already running, stop it and reconnect with the new configuration
3. Support named sessions via the `--session` flag

## Requirements

### Command Registration
- The CLI's command type system should include `config` as a recognized command category
- A `config` command should be registered under this category and included in the CLI's command list
- The CLI help output should include a `Configuration` section heading that lists the `config` command

### Command Routing and Behavior
- Running `playwright-cli config <path>` should route through the CLI's session management layer
- The session manager should stop any existing session and reconnect with the updated configuration

### Headless Viewport Defaults
- The daemon browser configuration should set a default viewport of 1280 by 720 pixels when running in headless mode

### SKILL.md Documentation
- `SKILL.md` should include a `### Configuration` section documenting:
  - `playwright-cli config` usage with a config file argument
  - Named session usage with `--session=`
  - The `--config=` flag usage with the `open` command
