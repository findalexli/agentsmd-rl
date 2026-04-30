# Add Node.js version check before loading the CLI

## Problem

Running `create-cloudflare` on an older Node.js version (e.g. v18) fails with a confusing syntax error because the bundled CLI code uses features that require Node.js 20+. There is no pre-flight version check — the CLI just crashes with an unhelpful parse error.

## Expected Behavior

Before loading the bundled CLI, there should be a lightweight version gate that:
1. Checks if the running Node.js version meets the minimum requirement
2. If too old, prints a clear error message stating the minimum required version, the user's current version, and suggests version managers (like Volta or nvm)
3. Exits with a non-zero status code without loading the CLI

This follows the pattern already used by wrangler's `bin/wrangler.js` in this same monorepo.

## Implementation Guidance

- Add a bin shim (a plain CommonJS script) that runs the version check before requiring the actual CLI bundle
- Update `package.json` to point `bin` at the new shim instead of `dist/cli.js` directly
- The minimum Node.js version should come from `package.json`'s `engines.node` field (single source of truth)
- Update `engines.node` to `>=20.0.0` to codify the actual requirement
- Include `bin` in the `files` array so it gets published

After making the code changes, update the project's `AGENTS.md` to reflect the new architecture — the entry point structure and build documentation should accurately describe how the bin shim relates to the CLI bundle.

## Files to Look At

- `packages/create-cloudflare/package.json` — current bin and engines configuration
- `packages/create-cloudflare/AGENTS.md` — project documentation for AI agents
- `packages/wrangler/bin/wrangler.js` — reference implementation of the same pattern
