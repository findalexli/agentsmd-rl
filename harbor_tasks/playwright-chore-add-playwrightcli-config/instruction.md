# Add `config` command to playwright-cli

## Problem

The `playwright-cli` terminal tool lets users manage browser sessions (open, close, session-list, etc.) but has no way to reconfigure a running session with a different config file. Users who want to change viewport, context options, or other config must manually stop and restart the session with new flags.

## Expected Behavior

A new `config` command should allow restarting the current session with a different configuration file. The command should:

1. Accept an optional path to a JSON config file (defaults to `playwright-cli.json`)
2. Stop the existing session if it's running, then reconnect with the new config
3. Work with named sessions via the `--session` flag
4. Be available as both `playwright-cli config <path>` and via `--config=<path>` with `open`

## Verification

The implementation is complete when:

- The `Category` type in `command.ts` includes a `'config'` member
- A `config` command is declared in `commands.ts` with `name: 'config'` and `category: 'config'`
- The commands array in `commands.ts` includes the config command (with a comment `// config` above it)
- The categories array in `helpGenerator.ts` has an entry with `name: 'config'` and `title: 'Configuration'`
- The program routes a `'config'` command through `handleSessionCommand`
- The session manager has a `configure()` method that: resolves the session name, checks if it can connect, stops the existing session, updates the config, and reconnects
- The daemon config in `browser/config.ts` has `contextOptions` with a `viewport` of `{ width: 1280, height: 720 }` for headless mode
- `SKILL.md` has a `### Configuration` section documenting `playwright-cli config`, `--session=` usage, and `--config=` usage

## Daemon Browser Configuration

The daemon browser configuration must set default viewport dimensions for headless mode. The viewport must be set to 1280x720 pixels. This is configured in `browser/config.ts` using the `contextOptions` key with a `viewport` property.

## SKILL.md Documentation

The project's skill documentation must include a `### Configuration` section with:
- Usage showing `playwright-cli config` with a config file argument
- Usage with named sessions using `--session=` combined with `config`
- The `--config=` flag usage with the `open` command