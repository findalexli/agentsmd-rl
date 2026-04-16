# Add playwright-cli stub for local development

## Overview

The repository has a playwright-cli command that currently requires either a global installation or running through a specific npm script in the root package.json. The goal is to make `npx playwright-cli` work seamlessly in the local development environment.

## Tasks

### 1. Create a new workspace package `playwright-cli-stub`

Create a new package at `packages/playwright-cli-stub/` that:
- Contains a `package.json` with appropriate metadata (name: `playwright-cli-stub`, private: true)
- Exposes a binary called `playwright-cli` pointing to the main script
- Contains the main script `playwright-cli-stub.js` that imports and runs `playwright/lib/cli/client/program`
- The script should have proper Node.js shebang and error handling

### 2. Update root package.json

Remove the `playwright-cli` script from root `package.json` (the one that points to `node packages/playwright/lib/cli/client/cli.js`). This is no longer needed since the workspace package will handle this.

### 3. Update SKILL.md documentation

Update `packages/playwright/src/skill/SKILL.md` to reflect the new installation workflow:
- The documentation currently recommends global installation first
- Change it to recommend trying the local version via `npx playwright-cli --version` first
- Only recommend global installation if the local version is not available
- Update the code examples to show `npx playwright-cli` usage

## Key Files

- Root `package.json` - remove the `playwright-cli` script entry
- `packages/playwright-cli-stub/package.json` - create new file
- `packages/playwright-cli-stub/playwright-cli-stub.js` - create new executable script
- `packages/playwright/src/skill/SKILL.md` - update Installation section

## Notes

- The stub should import from `playwright/lib/cli/client/program` (the compiled output)
- The script needs to be executable (chmod +x)
- The package should be marked as private since it's only for local development
- npm will automatically update package-lock.json when you run `npm install`
- The SKILL.md change is important - it should guide users to try the local workspace version before installing globally
