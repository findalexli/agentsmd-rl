# Fix Proxy Bypass for Loopback Addresses

## Problem

When Playwright launches Chromium with a proxy configuration that includes `localhost`, `127.0.0.1`, or `::1` in the bypass list, the browser incorrectly adds `<-loopback>` to the proxy bypass rules. This overrides the user's explicit bypass configuration, causing loopback traffic to be routed through the proxy when it should bypass it.

## Requirements

The fix must satisfy these verification criteria:

1. **Variable naming**: Introduce a constant named exactly `bypassesLoopback` declared with `const bypassesLoopback`

2. **Logic structure**: Use `!bypassesLoopback` in a conditional check

3. **Loopback detection**: The code must check for all four loopback indicators:
   - `<-loopback>`
   - `localhost`
   - `127.0.0.1`
   - `::1`

4. **Code quality**: The `bypassesLoopback` variable should hold the result of checking whether loopback is already bypassed, and the conditional that adds `<-loopback>` should use this variable

5. **File integrity**: The modified TypeScript file must remain valid with `export class Chromium` defined

## Documentation Tasks

Create `.claude/skills/playwright-dev/github.md` documenting how to upload fixes to GitHub:
- Branch naming conventions (e.g., `fix-<issue-number>`)
- Conventional commit format with scope (e.g., `fix(proxy): description`)
- The `Fixes:` line format referencing the full GitHub issue URL

Update `.claude/skills/playwright-dev/SKILL.md` to reference `github.md` in its Table of Contents.

Look at the existing structure of SKILL.md to understand the format and style for the new documentation.
