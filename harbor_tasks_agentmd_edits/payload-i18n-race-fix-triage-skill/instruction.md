# Fix Flaky i18n Language Switcher Test

## Problem

The i18n e2e test suite has a flaky `setUserLanguage()` helper function in `test/i18n/e2e.spec.ts`. Tests that switch languages intermittently fail in CI but pass locally.

The issue is in the `setUserLanguage` helper: after selecting a language from the dropdown, the function navigates to the next page before the language change has fully taken effect. The language dropdown triggers a server action (via `switchLanguage()`) which sets a cookie and calls `router.refresh()` — but nothing waits for these async operations to complete before proceeding.

In fast local environments this works fine, but in slower CI environments the timing gap causes the next page to load with the old language still active.

## Expected Behavior

The `setUserLanguage` helper should reliably wait for the language switch to fully complete before returning. This means waiting for:
1. The server action to finish (the POST request that sets the language cookie)
2. The page to re-render with the new language

## Additional Task

After fixing the race condition, create a new Claude Code skill at `.claude/skills/triage-ci-flake/SKILL.md` that documents a systematic workflow for triaging and fixing flaky CI tests. This skill should help future developers follow a structured approach when dealing with CI failures — covering reproduction steps, the distinction between dev and production/bundled testing, common flaky test patterns (race conditions, timing issues), and Playwright-specific best practices.

The skill should include proper YAML frontmatter with `name` and `description` fields.

## Files to Look At

- `test/i18n/e2e.spec.ts` — the `setUserLanguage()` helper has the race condition
- `.claude/skills/` — where Claude Code skills are stored in this repo
