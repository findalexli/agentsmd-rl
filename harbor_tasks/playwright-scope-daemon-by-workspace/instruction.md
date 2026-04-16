# Scope Playwright CLI Daemon by Workspace

## Problem

The Playwright CLI daemon is currently scoped by the installation directory. All projects sharing a Playwright installation share daemon processes, which causes conflicts when:
- Multiple projects on the same machine use Playwright CLI
- Projects need isolated browser sessions
- Daemon conflicts arise between different workspaces

The workspace should be identified by the presence of a `.playwright` folder (which serves as a workspace root marker).

## Task

Refactor the daemon so that scoping, socket paths, profile directories, and configuration all derive from the workspace directory instead of the installation directory.

## Expected Behavior

### Workspace Scoping

The daemon must use workspace-based scoping instead of installation-based scoping:

- The hash used for scoping must be derived from the workspace directory path, not the installation directory path
- The client information type must contain a field for the workspace directory hash and must not contain fields for installation directory or its hash
- A function must exist that locates the workspace by searching parent directories for a `.playwright` folder
- Socket paths must incorporate the workspace directory hash
- When the `PLAYWRIGHT_DAEMON_SESSION_DIR` environment variable is set, the daemon profiles directory must include the workspace hash as a subdirectory
- The default configuration file path must be `.playwright/cli.config.json` (not `playwright-cli.json`)

### Command Restructuring

The CLI commands must reflect the workspace-centric model:

- The forceful daemon kill command must be named `session-kill-all` (not `kill-all`)
- The `install` command must initialize the workspace by creating the `.playwright` folder and must support a `skills` option to conditionally install skills
- Browser installation must be a separate command called `install-browser`
- The `install-skills` top-level command must not exist (its functionality absorbed into `install --skills`)
- The `open` command must have the description `'Open the browser'`, and its config option description must note it "defaults to .playwright/cli.config.json"
- The `close` command must have the description `'Close the browser'`

### Documentation Updates

Per project conventions, skill documentation must stay in sync with CLI commands. Update these documentation files:

1. `packages/playwright/src/skill/SKILL.md`:
   - The Sessions section must reference `session-kill-all` (not `kill-all`)
   - The Configuration section must include the headings `# Close the browser` and `# Delete user data`

2. `packages/playwright/src/skill/references/session-management.md`:
   - Must use `session-kill-all` (not `kill-all`)
   - Must reference the `.playwright` folder for configuration paths

## Files to Modify

The relevant source files are in `packages/playwright/src/mcp/terminal/` and `packages/playwright/src/skill/`.

## Verification

After changes, run `npx tsc --noEmit --skipLibCheck` on the modified TypeScript files to verify no syntax errors.
