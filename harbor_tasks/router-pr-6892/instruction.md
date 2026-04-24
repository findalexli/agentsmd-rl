# Auto-update Example Dependency Versions

## Problem

In this monorepo, when workspace package versions change (via changesets), the example applications' `package.json` files still reference old versions of the workspace packages. This causes examples to become out of sync with the actual workspace package versions.

For instance, if `@tanstack/react-router` is bumped to version `1.95.1`, but examples still reference `^1.94.0`, users cloning the examples may encounter version mismatches.

## Task

Create an automated solution that updates all example `package.json` files to use the correct caret versions (`^x.y.z`) matching the current workspace package versions.

The solution must:

1. Be implemented as a Node.js script located at `scripts/update-example-deps.mjs`
2. Read the current versions from all packages in the `packages/` directory by reading their `package.json` files and extracting the `version` field
3. Find all `package.json` files in the `examples/` directory (excluding node_modules)
4. Update any `dependencies` or `devDependencies` that reference workspace packages to use the correct `^{version}` caret format
5. Output the word `Done` (capital D, exact case) upon completion
6. Integrate with the existing `changeset:version` workflow by being called from that npm script

## Files to examine

- `packages/*/package.json` - workspace package versions (look for packages with names like `@tanstack/*`)
- `examples/**/package.json` - example applications that need updating
- `package.json` - root package.json with npm scripts (specifically the `changeset:version` script)
- `scripts/` - existing scripts directory

## Expected behavior

When the solution runs:
- It should scan all workspace packages for their current versions
- It should update any example that depends on workspace packages
- It should output which examples were updated (one per line, e.g., `Updated examples/foo/package.json`)
- It should output `Done` followed by a summary when complete (e.g., `Done. Updated N example(s).`)
- The `changeset:version` script in `package.json` should call this script

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
