# Scope daemon processes by workspace instead of installation directory

## Problem

The Playwright CLI daemon currently scopes its sessions by the installation directory. This means all projects sharing the same Playwright installation use the same daemon processes, session data, and socket paths. When working on multiple projects simultaneously, sessions from one workspace can interfere with another — closing a session in project A could affect project B's daemon.

The daemon identification uses `installationDir` and `installationDirHash` in the `ClientInfo` type, and all profile directories and socket paths are derived from this hash. The `install-skills` command only installs Claude/Copilot skills and doesn't set up a workspace marker.

## Expected Behavior

Daemon processes should be scoped per workspace, not per installation. The system should:

1. **Add workspace detection**: Implement a function that walks up from the current working directory to find a `.playwright` marker directory, similar to how git finds `.git`.

2. **Replace installation-based scoping**: Change all daemon path derivation (profiles directory, socket paths, session directory) to use a workspace directory hash instead of the installation directory hash.

3. **Create a unified `install` command**: Replace the separate `install-skills` command with an `install` command that initializes a workspace by creating a `.playwright` directory marker. Skill installation should become an optional flag (`--skills`). The existing `install-browser` command should remain as a separate command.

4. **Rename `kill-all` to `session-kill-all`**: The command that forcefully kills all daemon processes should be renamed for consistency with the session command namespace.

5. **Update config file path**: The default config file location should change from `playwright-cli.json` to `.playwright/cli.config.json`, colocating it with the workspace marker.

After making the code changes, update the relevant documentation files to reflect the renamed commands and new workspace concepts. The project's skill documentation and reference files should accurately describe the current CLI command names and behavior.

## Files to Look At

- `packages/playwright/src/mcp/terminal/program.ts` — Main CLI program logic, daemon session management, client info creation
- `packages/playwright/src/mcp/terminal/commands.ts` — CLI command declarations and registration
- `packages/playwright/src/skill/SKILL.md` — Skill documentation listing all CLI commands
- `packages/playwright/src/skill/references/session-management.md` — Reference doc for session management commands
