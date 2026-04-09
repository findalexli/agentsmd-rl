# Make `npx playwright-cli` work for local development

## Problem

Currently, running `npx playwright-cli` in the repo does not work. The `playwright-cli` command is only available through an npm script defined in the root `package.json` (`npm run playwright-cli`), which is inconvenient — especially for tools and skills that expect `playwright-cli` to be a real executable found via `npx`.

## Expected Behavior

`npx playwright-cli` should resolve to a local stub package within the monorepo that delegates to the actual CLI entry point. The old npm script in root `package.json` should be replaced by this proper package-based approach.

## Files to Look At

- `package.json` — root package with the current `playwright-cli` npm script
- `packages/playwright/lib/cli/client/` — the actual CLI entry point lives here
- `packages/playwright/src/skill/SKILL.md` — the skill file documenting `playwright-cli` installation and usage

## What to Do

1. Create a stub package in the monorepo's `packages/` directory that registers a `playwright-cli` binary via its `bin` field. The stub should be a thin wrapper that requires and runs the existing CLI program module (check how the current npm script invokes the CLI to find the right module path).

2. Remove the old `playwright-cli` npm script from the root `package.json` since the stub package replaces it.

3. Update the skill documentation (`packages/playwright/src/skill/SKILL.md`) — the Installation section should be revised to recommend trying the local `npx` approach first, with global install as a fallback only when local is unavailable.
