# Add script to auto-install playwright dependencies before tests

## Problem

Running `npm run test` in any of the Wasp example projects (kitchen-sink, waspello, waspleau, etc.) requires manually installing playwright's browser dependencies first with `npx playwright install --with-deps`. If you forget this step, the tests fail with missing browser errors. This manual step is also duplicated across CI workflow files and the `waspc/run` script.

## Expected Behavior

Running `npm run test` should automatically install playwright's browser dependencies if needed, without requiring a separate manual step. This should work for all example projects that use playwright for e2e tests, as well as `waspc/starters-e2e-tests`.

The manual `npx playwright install --with-deps` calls in CI workflows and the `waspc/run` script should be removed since they become redundant.

After making the code changes, update the relevant documentation to reflect the simplified workflow. The `examples/kitchen-sink/README.md` currently tells users to manually run `npx playwright install --with-deps` as a prerequisite step — this is no longer needed and the instructions should be simplified. Don't forget to also update the golden e2e test snapshot at `waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/` to match.

## Files to Look At

- `examples/*/package.json` — example project npm scripts
- `waspc/starters-e2e-tests/package.json` — starters e2e test scripts
- `waspc/run` — development helper script with e2e test commands
- `.github/workflows/ci-examples-test.yaml` — CI workflow for example tests
- `.github/workflows/ci-starters-test.yaml` — CI workflow for starters tests
- `examples/kitchen-sink/README.md` — e2e test documentation
- `waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/` — golden snapshot files
