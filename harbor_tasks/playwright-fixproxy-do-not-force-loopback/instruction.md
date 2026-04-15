# Proxy bypass for loopback addresses ignores user configuration

## Problem

When a user sets `proxy.bypass` to `localhost`, `127.0.0.1`, or `::1` in their Chromium browser launch options, Playwright still force-adds `<-loopback>` to the `--proxy-bypass-list` Chrome argument. This causes loopback traffic to be proxied even though the user explicitly configured it to be bypassed.

The current logic in the Chromium launcher only checks whether `<-loopback>` itself is already present in the bypass rules, but doesn't recognize that `localhost`, `127.0.0.1`, or `::1` are semantically equivalent loopback addresses.

## Expected Behavior

When the user includes any loopback address (`localhost`, `127.0.0.1`, or `::1`) in their `proxy.bypass` configuration, Playwright should respect that and not force-add `<-loopback>` to the Chrome bypass list.

The existing behavior for non-loopback bypass targets (like `example.com`) should remain unchanged — `<-loopback>` should still be force-added in those cases.

## Files to Look At

- `packages/playwright-core/src/server/chromium/chromium.ts` — the Chromium browser launcher, specifically the proxy bypass argument construction logic

## Additional Task

The project's developer skill documentation (under `.claude/skills/playwright-dev/`) should be extended with a new skill document at `.claude/skills/playwright-dev/github.md` covering how to upload fixes to GitHub. The document must include:

- Branch naming convention: branches should be named with a `fix-` prefix followed by the issue number (e.g., `fix-12345`)
- Conventional commit message format: commit titles should use `fix(scope): description` or `feat(scope): description` syntax
- Commit body format: include a `Fixes:` line referencing the GitHub issue URL

The main skill index at `.claude/skills/playwright-dev/SKILL.md` must be updated to link to the new `github.md` document in its table of contents.
