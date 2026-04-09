# Scope CLI Daemon by Workspace

## Problem

The `playwright-cli` daemon currently scopes sessions by installation directory. This means different workspaces that share the same Playwright installation end up sharing daemon processes and session state. If you open a browser in one project, it can collide with sessions in another project using the same installation.

Additionally, the CLI configuration file is looked up as `playwright-cli.json` in the current directory, but there's no formal "workspace" concept. The `install-skills` command always installs skills without offering a way to initialize a workspace first.

## Expected Behavior

1. **Workspace-based scoping**: Daemon sessions should be scoped by workspace, not by installation directory. A workspace is identified by a `.playwright` directory marker (similar to `.git`). The system should walk up from `cwd` to find the nearest `.playwright` marker.

2. **`install` command**: The old `install-skills` command should be replaced with an `install` command that initializes a workspace (creates `.playwright` directory) and optionally installs skills via a `--skills` flag.

3. **`kill-all` renamed**: The `kill-all` command should be renamed to `session-kill-all` to be consistent with the `session-` prefix convention used by other session management commands.

4. **Config path**: The default configuration file path should move from `playwright-cli.json` to `.playwright/cli.config.json`.

5. **Documentation updates**: After making the code changes, update the relevant skill files and reference documentation to reflect the renamed commands and new workspace scoping.

## Files to Look At

- `packages/playwright/src/mcp/terminal/commands.ts` — CLI command declarations and registry
- `packages/playwright/src/mcp/terminal/program.ts` — Session management, daemon scoping, and install logic
- `packages/playwright/src/skill/SKILL.md` — Skill file documenting all CLI commands
- `packages/playwright/src/skill/references/session-management.md` — Session management reference docs
