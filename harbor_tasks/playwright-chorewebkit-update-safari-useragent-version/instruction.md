# Update WebKit Safari User-Agent Version to Current Stable

## Problem

The WebKit browser in Playwright currently reports Safari version `26.0` in its user-agent string. The latest stable Safari release is `26.4`. This means all WebKit user-agent strings — in the browser constant, device descriptors, badges, and release notes — are stale and will report the wrong browser version to servers.

## What to Do

1. Find the latest stable Safari version from [Safari Release Notes](https://developer.apple.com/documentation/safari-release-notes) (the highest numbered entry that is not a Technology Preview).

2. Update the Safari version string wherever it appears:
   - `packages/playwright-core/src/server/webkit/wkBrowser.ts` — the `BROWSER_VERSION` constant
   - `packages/playwright-core/browsers.json` — the `browserVersion` field for WebKit
   - `packages/playwright-core/src/server/deviceDescriptorsSource.json` — all `Version/X.Y` in WebKit device user-agent strings
   - `README.md` — the WebKit version badge and compatibility table
   - `docs/src/release-notes-*.md` — the browser versions section in each language's release notes

3. Document the update process as a new skill doc in `.claude/skills/playwright-dev/webkit-safari-version.md`. The doc should:
   - Name `BROWSER_VERSION` as the source of truth for the Safari version
   - Reference `wkBrowser.ts` where it is declared
   - Explain how to find the latest stable Safari version
   - Be linked from `.claude/skills/playwright-dev/SKILL.md`

## Files to Look At

- `packages/playwright-core/src/server/webkit/wkBrowser.ts` — declares `BROWSER_VERSION`
- `packages/playwright-core/browsers.json` — browser metadata including version
- `packages/playwright-core/src/server/deviceDescriptorsSource.json` — device user-agent strings
- `.claude/skills/playwright-dev/SKILL.md` — index of development skill docs
