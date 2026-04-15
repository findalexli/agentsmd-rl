# Fix blank settings tabs and missing route in Electron desktop app

## Problem

In the Electron desktop app, navigating to `/settings/stats` and `/settings/creds` shows blank pages. Additionally, the `/onboarding` route is not registered in the desktop router configuration, causing a missing redirect.

The root cause is that the desktop-specific files have drifted from their web counterparts:
- `componentMap.desktop.ts` (Electron, synchronous imports) is missing entries that exist in `componentMap.ts` (web, dynamic imports)
- `desktopRouter.config.desktop.tsx` (Electron) is missing routes that exist in `desktopRouter.config.tsx` (web)

## Expected Behavior

All settings tabs that work in the web app should also work in the Electron desktop app. Both the component map and the router configuration must stay in sync between web and desktop variants.

Specifically:
- The `componentMap.desktop.ts` file must include entries for `Stats` and `Creds` settings tabs (matching the web version)
- The `desktopRouter.config.desktop.tsx` file must include the `/onboarding` route (matching the web version)

## Files to Look At

- `src/routes/(main)/settings/features/componentMap.desktop.ts` — Electron settings tab map, should mirror entries from `componentMap.ts`
- `src/routes/(main)/settings/features/componentMap.ts` — Web settings tab map (reference for what's missing)
- `src/spa/router/desktopRouter.config.desktop.tsx` — Electron router config, should mirror routes from the web version
- `src/spa/router/desktopRouter.config.tsx` — Web router config (reference for missing routes)

## Additional Requirement

After fixing the code, update the agent skill documentation to help prevent this kind of drift in the future. Update these three specific skill files:

1. `.agents/skills/react/SKILL.md` — Must document the `.desktop` file sync rule, mentioning `.desktop` file variants and using terms like "sync", "pair", or "drift" to describe keeping desktop and web files consistent.

2. `.agents/skills/spa-routes/SKILL.md` — Must document the desktop router parity requirement, explicitly mentioning `desktopRouter.config.desktop` and using terms like "both", "parity", or "drift" to describe the need to edit both the web and desktop router config files when adding routes.

3. `.agents/skills/code-review/SKILL.md` — Must include a SPA/routing section that mentions `desktopRouter` and uses terms like "SPA" or "routing" to describe checking that desktop and web router pairs stay synchronized.
