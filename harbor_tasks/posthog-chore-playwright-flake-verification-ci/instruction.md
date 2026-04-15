# Add flake verification for new Playwright tests

## Problem

New or modified Playwright tests sometimes land flaky — they pass once but fail intermittently in CI, causing noisy failures on unrelated PRs. There's currently no automated check that changed spec files are stable before merging.

Additionally, the test-writing best practices live only inside the `.agents/skills/playwright-test/SKILL.md` skill file. Human developers looking at `playwright/README.md` don't benefit from them, and the skill duplicates content that should have a single source of truth.

## Expected Behavior

### 1. Flake verification CI step

A CI step should automatically detect which `playwright/**/*.spec.ts` files were touched by a PR and re-run them to catch flakes before they merge.

**Requirements:**
- Create a verification script at `.github/scripts/verify-playwright-new-tests-and-snapshots.sh` that:
  - Takes a base SHA and optional repeat count as arguments
  - Uses `git diff` to find changed `.spec.ts` files in the `playwright/` directory
  - Validates arguments and prints usage info on bad input (must include the string "usage" in the output)
  - Runs Playwright with `--repeat-each` (at least 10 repetitions) and `--retries=0` or `--retries 0`
  - Must include a `write_results` function or logic to write results
  - Writes results to `playwright/flake-verification-results.json` with fields:
    - `status`: string indicating pass/fail status
    - `message`: string with a descriptive message
    - `files`: array of affected spec file paths
    - `repeat_count`: number of repetitions used
  - The JSON file must use the exact filename `flake-verification-results.json`

- Update `.github/workflows/ci-e2e-playwright.yml` to:
  - Call the verification script `verify-playwright-new-tests-and-snapshots.sh` on pull requests
  - Read the `flake-verification-results.json` file after verification runs
  - Include flake verification failures in the PR comment that reports Playwright results
  - The comment should indicate which files failed verification and link to the report
  - Must reference the verification script and handle the flake verification results

### 2. Documentation consolidation

The Playwright skill (`.agents/skills/playwright-test/SKILL.md`) should be consolidated so that best practices live in `playwright/README.md` instead of being duplicated.

**Requirements:**
- Update `SKILL.md` to:
  - Reference `playwright/README.md` for best practices using the `@filename` syntax (e.g., `@playwright/README.md`)
  - Remove inline rules about CSS selectors, page object models, and test.step() that are moving to README
  - Keep only agent-specific operational instructions (e.g., "Keep looping until all tests pass")
  - Must include the string "README" or "readme" in the content to indicate the reference

- Update `playwright/README.md` to:
  - Add a "Best practices" section covering:
    - Prefer `getByRole` or `getByTestId` over CSS selectors; add `data-attr` to components if needed
    - Write fewer, longer tests that do multiple things, split logical steps with `test.step()`
    - Use page object models for common tasks (see `page-models/`)
    - Assert on UI changes after interactions, not on network requests resolving
    - Never put conditional logic (`if`) in a test
  - Add a "Gotchas" section covering:
    - Flaky tests are usually due to not waiting for the right thing
    - Strict mode violations when selectors match multiple elements
  - Must include the string "best practices" (case insensitive)
  - Must include the string "gotcha" (case insensitive)
  - Must include "getByRole" or "getByTestId" in content
  - Must include "page object model" or "page-models" in content
  - Must include "test.step" or "test.step()" in content
  - Must include "flaky" in the gotchas section
  - Must include "strict mode" or "loose selector" in the gotchas section

## Files to Look At

- `.github/scripts/` — where CI helper scripts live; create `verify-playwright-new-tests-and-snapshots.sh`
- `.github/workflows/ci-e2e-playwright.yml` — the Playwright CI workflow
- `.agents/skills/playwright-test/SKILL.md` — the Claude Code skill for writing Playwright tests
- `playwright/README.md` — the human-readable testing documentation
