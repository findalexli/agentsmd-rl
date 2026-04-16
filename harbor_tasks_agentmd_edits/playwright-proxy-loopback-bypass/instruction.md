# Fix Proxy Bypass Logic for Localhost and Update Skill Documentation

## Problem

When using a proxy with a bypass list that includes `localhost`, `127.0.0.1`, or `::1`, Playwright's Chromium launcher was incorrectly forcing loopback traffic through the proxy by adding `<-loopback>` to the `--proxy-bypass-list`. This prevented users from properly bypassing the proxy for local addresses.

The issue is in the proxy configuration logic in `packages/playwright-core/src/server/chromium/chromium.ts`. Currently, the code only checks if `<-loopback>` is explicitly in the bypass list, but doesn't recognize when the user has specified localhost addresses that should implicitly bypass the proxy.

## What You Need to Do

### 1. Fix the Proxy Logic

Modify `packages/playwright-core/src/server/chromium/chromium.ts` to detect when the bypass list contains localhost, 127.0.0.1, or ::1, and skip adding `<-loopback>` in those cases. The fix should:

- Check if any bypass rule equals `localhost`, `127.0.0.1`, or `::1`
- If any of these are present, don't force the loopback proxy
- Use a clear constant name for the check (e.g., `bypassesLoopback`)

### 2. Update Skill Documentation

The `.claude/skills/playwright-dev/SKILL.md` file documents how to develop Playwright. When fixing issues, developers need to know how to properly upload their fixes to GitHub.

Add documentation to the skill file that references a new `github.md` page covering:
- Branch naming conventions (branch per issue)
- Commit format (conventional commits with scope)
- Proper staging (don't use `git add -A`)
- Pushing the branch

Create the `.claude/skills/playwright-dev/github.md` file with this documentation.

## Key Files

- `packages/playwright-core/src/server/chromium/chromium.ts` - Proxy configuration logic
- `.claude/skills/playwright-dev/SKILL.md` - Skill navigation file to update
- `.claude/skills/playwright-dev/github.md` - New skill file to create

After making changes, rebuild with `npm run build` and verify with `npm run check-deps`.
