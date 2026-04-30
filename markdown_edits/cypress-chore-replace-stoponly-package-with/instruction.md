# Replace stop-only with ESLint rule

## Problem

The Cypress monorepo uses a third-party package called `stop-only` (with `yarn stop-only` and `yarn stop-only-all` scripts) to detect accidental `.only()` calls left in test files. This approach has issues: it runs as a separate CI step, doesn't integrate with the existing lint pipeline, and doesn't work correctly on Windows. Meanwhile, the project already uses `eslint-plugin-mocha` which has a `mocha/no-exclusive-tests` rule that can catch `.only()` usage at lint time.

## Expected Behavior

The `.only()` detection should be handled entirely through ESLint — specifically, by enabling `mocha/no-exclusive-tests: 'error'` in the shared ESLint base config. The `stop-only` package and its associated scripts should be removed. The CI pipeline should no longer have a separate "Stop .only" step since `yarn lint` will catch these issues.

One file — `cli/types/tests/cypress-tests.ts` — intentionally uses `.only()` in dtslint-style type samples. It will need an ESLint disable directive so it doesn't trigger the new rule.

After making the code changes, update the project's agent instruction files (`AGENTS.md`) to reflect the new enforcement mechanism. The documentation currently references `yarn stop-only` commands and describes stop-only-based enforcement — this should be updated to describe the ESLint-based approach.

## Files to Look At

- `packages/eslint-config/src/baseConfig.ts` — shared ESLint configuration where mocha rules are defined
- `package.json` — root scripts and devDependencies (contains stop-only references)
- `cli/types/tests/cypress-tests.ts` — file with intentional `.only()` usage that needs an eslint-disable
- `npm/eslint-plugin-dev/.eslintignore` — may need updating to avoid linting `node_modules`
- `.circleci/src/pipeline/@pipeline.yml` — CI build setup with the "Stop .only" step
- `AGENTS.md` — project agent instructions documenting lint commands and code conventions
