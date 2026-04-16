# Add playwright-cli stub for local development

The Playwright repository has an npm script `playwright-cli` in the root `package.json` that runs the CLI directly from source. This approach has limitations:

1. Users cannot run `npx playwright-cli` directly in the repo
2. Global installation is the only option for some users

## Goal

Enable users to run `playwright-cli` via `npx` without a global install, while still supporting global installation as a fallback.

## Tasks

### 1. Create a stub package

Create a new package at `packages/playwright-cli-stub/` containing:

**package.json**
- Package name: `playwright-cli-stub`
- Version: `0.0.0`
- Flag: `private: true`
- A `bin` entry mapping `playwright-cli` to an executable script

**playwright-cli-stub.js** (executable)
- A Node.js script that loads the CLI program from the playwright package
- Handles errors by logging the error message and exiting with code 1
- Has a shebang for direct execution

### 2. Update root package.json

Remove the `playwright-cli` script from the root `package.json` scripts section (the stub package will provide this functionality instead).

### 3. Update SKILL.md documentation

The file `packages/playwright/src/skill/SKILL.md` documents the CLI. Update the `## Installation` section to:

- Recommend trying `npx playwright-cli --version` first to check if a local version is available
- Show how to use `npx playwright-cli` for commands when the local version works
- Document global installation (`npm install -g @playwright/cli@latest`) as a fallback when npx doesn't work

The documentation should reflect a local-first approach: try npx first, then fall back to global install if needed.

## Files to create/modify

- `packages/playwright-cli-stub/package.json` (create)
- `packages/playwright-cli-stub/playwright-cli-stub.js` (create)
- `package.json` (remove playwright-cli script)
- `packages/playwright/src/skill/SKILL.md` (update Installation section)

## Verification

After making changes:
1. The stub package directory and files should exist
2. The stub package.json should have correct name, version, private flag, and bin entry
3. The stub JS file should be executable
4. The root package.json should no longer have the playwright-cli script
5. The SKILL.md Installation section should recommend npx first before global install