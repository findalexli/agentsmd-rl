# Scope CLI daemon sessions by workspace instead of installation directory

## Problem

The `playwright-cli` daemon currently scopes sessions by the **installation directory** of the package. This means that if two different projects use the same Playwright installation, they share daemon sessions — leading to session conflicts and unexpected cross-project state leakage.

The daemon isolation is controlled via a hash of the installation path (`installationDirHash` in `program.ts`), which gets used for socket paths and profile directories. This needs to change to workspace-based scoping.

## What needs to change

1. **Workspace detection**: Instead of using the package installation path, find the workspace root by walking up from `cwd` looking for a `.playwright` directory marker. Fall back to the package location if no workspace marker is found.

2. **Install command**: The current `install` command in `commands.ts` is named `install-browser` and only installs browsers. Refactor so there's a new `install` command that initializes the workspace (creates the `.playwright` marker directory) with an optional `--skills` flag, and rename the old install to `install-browser`.

3. **Command rename**: The `kill-all` command should be renamed to `session-kill-all` to be consistent with the session command naming scheme (`session-list`, `session-close-all`).

4. **Config file path**: The default config file path should move from `playwright-cli.json` in the current directory to `.playwright/cli.config.json` under the workspace marker directory.

5. **Update the CLI's skill documentation and reference files** to reflect the renamed commands and new workspace initialization workflow. The project's dev skill file (`.claude/skills/playwright-mcp-dev/SKILL.md`) instructs contributors to keep the skill docs in sync with CLI changes.

## Files to look at

- `packages/playwright/src/mcp/terminal/commands.ts` — CLI command declarations
- `packages/playwright/src/mcp/terminal/program.ts` — daemon session management, client info, socket paths
- `packages/playwright/src/skill/SKILL.md` — user-facing CLI documentation
- `packages/playwright/src/skill/references/session-management.md` — session management reference docs
- `.claude/skills/playwright-mcp-dev/SKILL.md` — dev instructions (read this for guidance on what to update)
