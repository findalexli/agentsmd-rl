# Add flake verification for new Playwright tests

## Problem

New or modified Playwright tests sometimes land flaky — they pass once but fail intermittently in CI, causing noisy failures on unrelated PRs. There's currently no automated check that changed spec files are stable before merging.

Additionally, the test-writing best practices live only inside the `.agents/skills/playwright-test/SKILL.md` skill file. Human developers looking at `playwright/README.md` don't benefit from them, and the skill duplicates content that should have a single source of truth.

## Expected Behavior

1. A CI step should automatically detect which `playwright/**/*.spec.ts` files were touched by a PR and re-run them with `--repeat-each` (at least 10 repetitions, zero retries) to catch flakes before they merge. If any repetition fails, the CI step should fail and the results should be surfaced in the existing PR comment that reports Playwright results.

2. The Playwright skill (`.agents/skills/playwright-test/SKILL.md`) should be consolidated so that best practices live in `playwright/README.md` instead of being duplicated. The skill should reference the README for best practices. The README should be reorganized with clear sections for best practices and gotchas.

## Files to Look At

- `.github/scripts/` — where CI helper scripts live
- `.github/workflows/ci-e2e-playwright.yml` — the Playwright CI workflow
- `.agents/skills/playwright-test/SKILL.md` — the Claude Code skill for writing Playwright tests
- `playwright/README.md` — the human-readable testing documentation
