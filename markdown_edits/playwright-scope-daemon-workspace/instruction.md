# Scope Daemon Sessions by Workspace

The Playwright CLI currently scopes daemon sessions by the installation directory, which causes issues when the same installation is used across multiple projects. Sessions from different workspaces can interfere with each other because they share the same daemon profile directory based on installation location.

## Task

Refactor the daemon session management to scope sessions by **workspace** instead of installation directory. A workspace is identified by the presence of a `.playwright/` folder (similar to how Git uses `.git/`).

## Required Changes

### 1. Code Changes

**packages/playwright/src/mcp/terminal/program.ts:**
- Replace `installationDirHash` with `workspaceDirHash` throughout
- Add a `findWorkspaceDir()` function that walks up the directory tree looking for a `.playwright/` folder (up to 10 levels)
- Update `daemonProfilesDir()` to take `workspaceDirHash` and include it in the path
- Update `daemonSocketPath()` to use `workspaceDirHash` in socket names
- Change default config file location from `playwright-cli.json` to `.playwright/cli.config.json`
- Update retry logic to use exponential backoff `[100, 200, 400]` instead of fixed delay
- Simplify error message when session not open to: "please run open first" (without showing formatted args)
- Update `install()` function to create `.playwright/` folder and print "Workspace initialized at {cwd}"
- Make install-skills an option `--skills` on the install command

**packages/playwright/src/mcp/terminal/commands.ts:**
- Rename `kill-all` command to `session-kill-all`
- Restructure install commands: `install` (workspace init) and `install-browser` (browser install)
- Update command descriptions:
  - `open`: "Open the browser" (was "Open browser")
  - `close`: "Close the browser" (was "Close the page")
  - `config`: add "defaults to .playwright/cli.config.json" to description

### 2. Documentation Updates

**packages/playwright/src/skill/SKILL.md:**
- Update session commands section:
  - Change `playwright-cli kill-all` to `playwright-cli session-kill-all`
  - Add descriptive comments above commands (e.g., "# Close all browsers" instead of inline "# stop all sessions")
  - Update close/delete-data section with new comment style

**packages/playwright/src/skill/references/session-management.md:**
- Update all `kill-all` references to `session-kill-all`
- Update config file example to use `.playwright/my-cli.json` instead of `playwright-cli.json`

## Key Behaviors

1. **Workspace Discovery**: Starting from cwd, walk up parent directories up to 10 levels looking for `.playwright/` folder
2. **Hash Generation**: Use SHA1 hash of the workspace directory path (first 16 chars)
3. **Daemon Profiles**: Store in `{cache_dir}/ms-playwright/daemon/{hash}/`
4. **Socket Names**: Use `{hash}-{session}.sock` format
5. **Install Command**: Creates `.playwright/` marker folder, optionally installs skills with `--skills` flag

## Files to Modify

- `packages/playwright/src/mcp/terminal/program.ts` (daemon scoping, workspace discovery)
- `packages/playwright/src/mcp/terminal/commands.ts` (command renames and restructure)
- `packages/playwright/src/skill/SKILL.md` (command documentation)
- `packages/playwright/src/skill/references/session-management.md` (session management reference)

The documentation updates are critical - the SKILL.md and session-management.md files must accurately reflect the new command names and workspace-based architecture.
