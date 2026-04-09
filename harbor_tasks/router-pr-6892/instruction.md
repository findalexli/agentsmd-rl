# Task: Auto-Update Example Dependencies

## Problem

This is a pnpm workspace monorepo containing:
- **packages/**: Workspace packages with their own versions
- **examples/**: Example applications that depend on workspace packages

When workspace packages are version-bumped (via changesets), the example applications' `package.json` files still reference the old versions. This causes a drift between what's in the workspace and what the examples declare as dependencies.

The release workflow currently runs `changeset version` followed by `pnpm install` and formatting. However, there's no automated step to synchronize the example dependencies with the newly bumped workspace package versions.

## Requirements

You need to create a Node.js script that:

1. **Reads workspace packages**: Scan the `packages/` directory and build a map of package names to their current versions from each package's `package.json`

2. **Updates example dependencies**: For each example in `examples/` that has a `package.json`, check its `dependencies` and `devDependencies`. When a dependency name matches a workspace package, update its version range to match the current workspace version (using `^` prefix)

3. **Integrates with release workflow**: The script should be called as part of the `changeset:version` npm script, after `changeset version` but before `pnpm install`

4. **Outputs progress**: Log which examples were updated and provide a summary count

## Key Files

- `/workspace/router/package.json` - Contains the `changeset:version` script that needs modification
- `/workspace/router/scripts/` - Directory where the new script should be placed
- `/workspace/router/packages/` - Workspace packages with current versions
- `/workspace/router/examples/` - Example applications with dependencies to update

## Expected Behavior

- When the script runs, it should find all workspace packages and their versions
- It should scan all examples and update any outdated workspace dependencies
- The script should handle both `dependencies` and `devDependencies`
- Non-workspace dependencies (like `react`, `lodash`, etc.) should be left untouched
- The script should format the output JSON with 2-space indentation and a trailing newline

## Constraints

- Use only Node.js built-in modules (`fs`, `path`, etc.) - the glob functionality is available via `node:fs` in Node 22
- The script should be idempotent - running it multiple times should not cause issues
- Handle edge cases gracefully (missing directories, no workspace packages, no examples needing updates)
