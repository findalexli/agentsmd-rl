# Update WebKit Safari User-Agent Version to 26.4

## Problem

The WebKit browser in Playwright currently reports Safari version `26.0` in its user-agent string, but the latest stable Safari release is `26.4`. This means all WebKit user-agent strings — in the browser constant, device descriptors, badges, and release notes — are stale.

Going forward, the version should track Safari stable releases (e.g. 26.4) rather than Safari Technology Preview.

## What Needs to Change

1. The `BROWSER_VERSION` constant in `packages/playwright-core/src/server/webkit/wkBrowser.ts` is the source of truth for the WebKit Safari version string. Update it to `26.4`.

2. The version also appears in:
   - `packages/playwright-core/browsers.json` — the `browserVersion` field for WebKit
   - `packages/playwright-core/src/server/deviceDescriptorsSource.json` — all `Version/X.Y` in WebKit device user-agent strings
   - `README.md` — the WebKit version badge and compatibility table
   - `docs/src/release-notes-*.md` — the browser versions section in each language's release notes

3. After making the code changes, document the Safari version update process as a new development skill in `.claude/skills/playwright-dev/`. The repo already has skill docs for other common tasks (see the existing SKILL.md index). Create a skill doc explaining where the version is declared, how to find the latest stable Safari version, and what to run afterwards. Update the SKILL.md index to link to the new doc.

## Files to Look At

- `packages/playwright-core/src/server/webkit/wkBrowser.ts` — declares `BROWSER_VERSION`
- `packages/playwright-core/browsers.json` — browser metadata including version
- `packages/playwright-core/src/server/deviceDescriptorsSource.json` — device user-agent strings
- `.claude/skills/playwright-dev/SKILL.md` — index of development skill docs
