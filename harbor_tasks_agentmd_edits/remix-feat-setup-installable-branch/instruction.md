# Add pnpm-installable branch setup script with documentation

## Problem

The Remix monorepo has no way to let users test the latest `main` branch without publishing nightly releases to npm. Publishing nightly versions clutters the npm registry and version history. The repo needs a mechanism to create pnpm-installable branches that users can install directly from GitHub.

Additionally, the `logAndExec` utility in `scripts/utils/process.ts` currently only runs commands with inherited stdio and returns `void`. It needs to support capturing command output as a string for use in scripts that need to inspect command results.

## Expected Behavior

1. **Script**: A new script at `scripts/setup-installable-branch.ts` that:
   - Accepts a branch name (defaults to `nightly`)
   - Checks git status is clean
   - Creates a new branch, runs a build
   - Updates `.gitignore` to include `dist/`
   - Rewrites `@remix-run/*` dependencies in package.json files to point to the GitHub branch
   - Moves peerDeps to normal deps and applies publishConfig overrides
   - Commits the result

2. **Utility change**: `scripts/utils/process.ts` — the `logAndExec` function should support an optional `captureOutput` parameter. When `true`, it captures and returns the command's stdout as a trimmed string instead of inheriting stdio.

3. **Package script**: `package.json` should register a `setup-installable-branch` script entry.

4. **CI workflow**: A new `.github/workflows/nightly.yml` that runs the script on a schedule and supports manual dispatch.

5. **Documentation**: After implementing the code changes, update the project documentation:
   - `README.md` should include an Installation section showing how to install packages (both stable via npm and nightly via pnpm)
   - `CONTRIBUTING.md` should include a Nightly Builds section explaining the nightly workflow and how to use the setup script

## Files to Look At

- `scripts/utils/process.ts` — the `logAndExec` function that needs the capture-output feature
- `package.json` — where the new script should be registered
- `README.md` — needs an Installation section
- `CONTRIBUTING.md` — needs a Nightly Builds section
- `AGENTS.md` — development guide with code style and conventions
