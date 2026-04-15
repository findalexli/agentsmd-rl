# Proxy bypass for loopback addresses ignores user configuration

## Problem

When a user sets `proxy.bypass` to `localhost`, `127.0.0.1`, or `::1` in their Chromium browser launch options, Playwright still force-adds `<-loopback>` to the `--proxy-bypass-list` Chrome argument. This causes loopback traffic to be proxied even though the user explicitly configured it to be bypassed.

The current logic in `packages/playwright-core/src/server/chromium/chromium.ts` only checks whether `<-loopback>` itself is already present in the bypass rules via `proxyBypassRules.includes('<-loopback>')`, but doesn't recognize that `localhost`, `127.0.0.1`, and `::1` are semantically equivalent loopback addresses.

## Required Behavior

In `packages/playwright-core/src/server/chromium/chromium.ts`, modify the proxy bypass logic so that:

1. A new variable named `bypassesLoopback` must be defined to track whether loopback traffic is being bypassed
2. The logic must check if any of the following are present in the bypass rules:
   - `<-loopback>`
   - `localhost`
   - `127.0.0.1`
   - `::1`
3. The condition `!process.env.PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK && !bypassesLoopback` must be used to decide whether to add `<-loopback>` to `proxyBypassRules`
4. When the user includes any loopback address (`localhost`, `127.0.0.1`, or `::1`) in their `proxy.bypass` configuration, Playwright must not force-add `<-loopback>`
5. The existing behavior for non-loopback bypass targets (like `example.com`) should remain unchanged — `<-loopback>` should still be force-added in those cases

## Files to Look At

- `packages/playwright-core/src/server/chromium/chromium.ts` — the Chromium browser launcher, specifically the proxy bypass argument construction logic

## Additional Task

Create a new skill document at `.claude/skills/playwright-dev/github.md` covering how to upload fixes to GitHub. The document must include:

- Branch naming convention: branches should be named with a `fix-` prefix followed by the issue number (e.g., `fix-12345`)
- Conventional commit message format: commit titles should use `fix(scope): description` or `feat(scope): description` syntax
- Commit body format: include a `Fixes:` line referencing the GitHub issue URL

Update `.claude/skills/playwright-dev/SKILL.md` to link to the new `github.md` document in its table of contents.
