# Proxy bypass for loopback addresses ignores user configuration

## Problem

When a user sets `proxy.bypass` to `localhost`, `127.0.0.1`, or `::1` in their Chromium browser launch options, Playwright still force-adds `<-loopback>` to the `--proxy-bypass-list` Chrome argument. This causes loopback traffic to be proxied even though the user explicitly configured it to be bypassed.

The current logic in `packages/playwright-core/src/server/chromium/chromium.ts` only checks whether `<-loopback>` itself is already present in the bypass rules, but doesn't recognize that `localhost`, `127.0.0.1`, and `::1` are semantically equivalent loopback addresses.

## Required Behavior

In `packages/playwright-core/src/server/chromium/chromium.ts`, fix the proxy bypass logic so that:

1. When the user includes `localhost` in their `proxy.bypass` configuration, Playwright must NOT force-add `<-loopback>` to `proxyBypassRules`
2. When the user includes `127.0.0.1` in their `proxy.bypass` configuration, Playwright must NOT force-add `<-loopback>` to `proxyBypassRules`
3. When the user includes `::1` in their `proxy.bypass` configuration, Playwright must NOT force-add `<-loopback>` to `proxyBypassRules`
4. The existing behavior for non-loopback bypass targets (like `example.com`) should remain unchanged — `<-loopback>` should still be force-added in those cases when `PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK` is not set

## Files to Look At

- `packages/playwright-core/src/server/chromium/chromium.ts` — the Chromium browser launcher, specifically the proxy bypass argument construction logic

## Quality Requirements

Your changes must pass:

1. **ESLint**: Run `npm run eslint -- --max-warnings=0 packages/playwright-core/src/server/chromium/chromium.ts`
2. **TypeScript transpilation**: The file must transpile without errors
3. **Channel generation**: Run `node utils/generate_channels.js` successfully
4. **Package lint**: Run `npm run lint-packages` successfully
5. **Syntax validation**: The file must have balanced braces and parentheses

## Additional Task

Create a new skill document at `.claude/skills/playwright-dev/github.md` covering how to upload fixes to GitHub. The document must include:

- Branch naming convention: branches should be named with a `fix-` prefix followed by the issue number (e.g., `fix-12345`)
- Conventional commit message format: commit titles should use `fix(scope): description` or `feat(scope): description` syntax
- Commit body format: include a `Fixes:` line referencing the GitHub issue URL

Update `.claude/skills/playwright-dev/SKILL.md` to link to the new `github.md` document in its table of contents.
