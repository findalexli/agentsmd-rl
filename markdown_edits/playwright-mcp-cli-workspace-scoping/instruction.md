# Task: Scope Playwright CLI Daemon by Workspace

The Playwright MCP CLI currently scopes daemon processes by the installation directory. This causes issues when multiple projects use the same Playwright installation - their sessions interfere with each other.

## Goal

Scope the daemon by workspace instead of installation directory. A workspace is identified by the presence of a `.playwright/` directory.

## Required Changes

### 1. Code Changes (packages/playwright/src/mcp/terminal/)

**program.ts:**
- Replace `installationDir` and `installationDirHash` with `workspaceDir` and `workspaceDirHash` in `ClientInfo`
- Add a `findWorkspaceDir(startDir)` function that walks up the directory tree looking for a `.playwright/` folder (up to 10 levels)
- Update `createClientInfo()` to use workspace directory instead of installation directory
- Update `daemonProfilesDir()` to scope profiles by workspace hash
- Update `daemonSocketPath()` to use `workspaceDirHash` instead of `installationDirHash`
- Update config file auto-discovery from `playwright-cli.json` to `.playwright/cli.config.json`
- Update `install()` function to create `.playwright/` folder and accept `--skills` flag
- Rename command handler from `kill-all` to `session-kill-all`

**commands.ts:**
- Rename `kill-all` command to `session-kill-all`
- Rename `install-browser` command to `install` with description "Initialize workspace"
- Add `--skills` option to `install` command
- Create separate `install-browser` command for browser installation (swap the two commands)
- Update command descriptions: "Open browser" → "Open the browser", "Close the page" → "Close the browser"
- Update config option description to mention `.playwright/cli.config.json` default

### 2. Documentation Updates

**packages/playwright/src/skill/SKILL.md:**
- Update command examples to use `session-kill-all` instead of `kill-all`
- Update close/delete-data section to match new structure
- Ensure all session commands are documented with consistent naming

**packages/playwright/src/skill/references/session-management.md:**
- Replace all instances of `kill-all` with `session-kill-all`
- Update config file path references from `playwright-cli.json` to `.playwright/my-cli.json`

## Testing Your Changes

After making changes, verify:
1. `workspaceDirHash` is used instead of `installationDirHash` in program.ts
2. `findWorkspaceDir()` function exists and searches for `.playwright/` directory
3. `session-kill-all` command exists in commands.ts
4. `install` command has "Initialize workspace" description
5. SKILL.md and session-management.md reflect the new command names
6. Config file references use `.playwright/cli.config.json`

## Files to Modify

- `packages/playwright/src/mcp/terminal/program.ts`
- `packages/playwright/src/mcp/terminal/commands.ts`
- `packages/playwright/src/skill/SKILL.md`
- `packages/playwright/src/skill/references/session-management.md`

Do NOT modify test files - they are updated separately by the test infrastructure.
