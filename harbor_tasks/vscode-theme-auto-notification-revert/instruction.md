# Bug Report: Theme auto-update notification causes unwanted theme revert for existing users

## Problem

After VS Code updated its default color themes (e.g., from "Dark Modern" to "VS Code Dark"), existing users who never explicitly chose a theme are shown a one-time notification offering to "Browse Themes" or "Revert" to the previous default. However, this notification is problematic — it fires during theme service initialization and offers a revert path that overrides the intended default theme migration. The notification introduces confusion and a disruptive UX flow where users are prompted to go back to a theme that is no longer the product default, undermining the purpose of updating the defaults in the first place.

## Expected Behavior

When VS Code updates its default themes, existing users should seamlessly receive the new default theme. The separate "new default theme" notification already handles awareness. There should be no additional notification prompting users to revert to an outdated previous default.

## Actual Behavior

A redundant notification appears during initialization offering users the option to revert to the old default theme (e.g., "Dark Modern"), conflicting with the intended migration to the new defaults and creating a confusing dual-notification experience.

## Files to Look At

- `src/vs/workbench/services/themes/browser/workbenchThemeService.ts`
