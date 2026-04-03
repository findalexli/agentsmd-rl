# Make `npx playwright-cli` work for local development

## Problem

In the Playwright monorepo, `npx playwright-cli` doesn't resolve to anything — there's no local package that provides a `playwright-cli` bin entry. Developers currently rely on `npm run playwright-cli` (a script in the root `package.json` that directly invokes `node packages/playwright/lib/cli/client/cli.js`), but this doesn't work with `npx` which is what tools and agents use.

The project's SKILL.md (at `packages/playwright/src/skill/SKILL.md`) currently tells users to install `playwright-cli` globally as the first approach, with `npx` mentioned only as an alternative. This should be reversed — local `npx` resolution should be the recommended approach.

## Expected Behavior

1. Running `npx playwright-cli` within the monorepo should resolve to a local stub package that delegates to the built CLI program
2. The old `playwright-cli` npm script in the root `package.json` should be removed since it's superseded by the stub package
3. The SKILL.md installation instructions should be updated to recommend trying the local `npx playwright-cli` approach first, with global install as a fallback

## Files to Look At

- `packages/playwright/lib/cli/client/program.js` — the CLI program entry point that the stub should delegate to
- `package.json` — root workspace config with the old `playwright-cli` script
- `packages/playwright/src/skill/SKILL.md` — skill documentation with installation instructions (update the Installation section)
