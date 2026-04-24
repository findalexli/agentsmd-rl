# Task: Add Script to Auto-Update Example Dependency Versions

## Problem

The TanStack Router monorepo uses changesets for version management. When workspace packages are version-bumped via changesets, the example applications in the `examples/` directory still reference old versions of these packages. This creates inconsistency between the actual package versions and what the examples declare as dependencies.

Your task is to create an automation script that keeps example dependencies synchronized with workspace package versions.

## Requirements

1. **Create `scripts/update-example-deps.mjs`**
   - The script should:
     - Scan all packages in `packages/*/package.json` to build a map of package name → current version
     - Find all `package.json` files in the `examples/` directory (recursively), using `globSync` with its `exclude` option to skip `node_modules` directories (the source code must contain the strings `exclude` and `node_modules`)
     - For each example's dependencies and devDependencies:
       - If a dependency name matches a workspace package AND its version range doesn't match `^${workspace_version}`, update it
       - Leave non-workspace dependencies untouched
       - Preserve the JSON formatting (2-space indentation + trailing newline)
     - Print a message for each updated example that includes the word "Updated"
     - Print a summary count of updated examples at the end

2. **Update `package.json`**
   - Modify the `changeset:version` script to run `node scripts/update-example-deps.mjs` after `changeset version` and before `pnpm install`

3. **Key implementation details** (from AGENTS.md):
   - The repo uses `pnpm` as the package manager
   - Internal dependencies use the workspace protocol (`workspace:*`)
   - Nx is used for task orchestration
   - Test changes with `pnpm test:eslint`, `pnpm test:types`, `pnpm test:unit`

## Files to modify/create

- **Create**: `scripts/update-example-deps.mjs` - The dependency update script
- **Modify**: `package.json` - Update the `changeset:version` script

## Expected behavior

When the script runs:
1. It reads all workspace package versions from `packages/*/package.json`
2. It scans `examples/**/package.json` using `globSync` with its `exclude` option to skip `node_modules`
3. It updates any workspace package dependencies to use `^${current_workspace_version}`
4. It writes back the updated package.json files with proper formatting
5. The `changeset:version` npm script invokes this new script as part of the release workflow

## Testing approach

You can test your script by:
1. Checking the script exists at `scripts/update-example-deps.mjs`
2. Verifying `node --check scripts/update-example-deps.mjs` passes
3. Creating a test example with outdated workspace dependencies and running the script
4. Running the repo's existing test suite (`pnpm test:eslint`, `pnpm test:types`, `pnpm test:unit`)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
