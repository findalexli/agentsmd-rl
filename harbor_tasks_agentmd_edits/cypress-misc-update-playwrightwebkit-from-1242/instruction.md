# Fix WebKit cookie domain matching inconsistency

## Problem

When using `cy.getCookie()` in WebKit, cookies are matched using a loose domain matching strategy (`domainMatch` from `tough-cookie`). This causes inconsistent behavior across Linux and macOS: on one platform the apex domain cookie is returned, on the other the fully qualified domain cookie is returned. Users have reported getting the wrong cookie value back when multiple cookies exist for different subdomains of the same root domain.

For example, if there are cookies for both `www.foobar.com` and `foobar.com`, `getCookie` may return the apex domain cookie when the user expects the more specific subdomain cookie.

## Expected Behavior

`getCookie` in the WebKit automation layer should prefer a cookie whose domain exactly matches the requested domain. If no exact match is found, it should fall back to matching the apex domain. This two-pass approach ensures deterministic behavior across platforms.

The `cookieMatches` utility function in `packages/server/lib/automation/util.ts` needs to support an optional strict domain matching mode, and the WebKit `getCookie` method in `packages/server/lib/browsers/webkit-automation.ts` should use it.

Additionally, since this change accompanies a WebKit version upgrade that also moves the CI/Docker base images from Debian Bullseye to Debian Trixie, the project's agent instruction files should be updated to reflect the new Debian codename so that future automated upgrades reference the correct image names.

## Files to Look At

- `packages/server/lib/automation/util.ts` — cookie matching utility (`cookieMatches`)
- `packages/server/lib/browsers/webkit-automation.ts` — WebKit browser automation, `getCookie` method
- `packages/electron/.cursor/rules/electron-upgrade.mdc` — Cursor rules for Electron upgrades, references Docker image names
