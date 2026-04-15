# Add `config` command to playwright-cli

## Problem

The `playwright-cli` terminal tool lets users manage browser sessions (open, close, session-list, etc.) but has no way to reconfigure a running session with a different config file. Users who want to change viewport, context options, or other config must manually stop and restart the session with new flags.

## Expected Behavior

A new `config` command should allow restarting the current session with a different configuration file. The command should:

1. Accept an optional path to a JSON config file (defaults to `playwright-cli.json`)
2. Stop the existing session if it's running, then reconnect with the new config
3. Work with named sessions via the `--session` flag
4. Be available as both `playwright-cli config <path>` and via `--config=<path>` with `open`

## Implementation Requirements

### Type System

- The `Category` type union must include `'config'` as a member.

### Command Declaration

- A `config` command must be declared using `declareCommand` with `name: 'config'` and `category: 'config'`.
- The command must be added to the commands array with a `// config` comment above it.

### Help System

- The help generator's categories array must include an entry with `name: 'config'` and `title: 'Configuration'`.

### Program Routing

- When the command name is `'config'`, the program must route it through `handleSessionCommand` passing `'config'` as the subcommand.
- The `handleSessionCommand` function must dispatch the `'config'` subcommand to a `configure()` method on the session manager.

### Configure Method

The `configure()` method on the session manager must:

1. Resolve the session name from args
2. Check if the session can be connected
3. If connected, stop the existing session
4. Update `this._options.config` with the new config path
5. Reconnect to the session

### Daemon Browser Config

The daemon browser configuration should set default viewport dimensions for headless mode by adding `contextOptions` with a `viewport` of `{ width: 1280, height: 720 }`.

### SKILL.md Documentation

Update the project's skill documentation to include a `### Configuration` section with:

- Usage showing `playwright-cli config` with a config file argument
- Usage with named sessions using `--session=` combined with `config`
- The `--config=` flag usage with the `open` command
