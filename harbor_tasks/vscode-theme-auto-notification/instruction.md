# Bug Report: Existing users not notified when default color theme changes automatically

## Problem

When VS Code updates its default color theme (e.g., from "Dark Modern" to "VS Code Dark"), existing users who never explicitly chose a theme are silently migrated to the new default. These users see their editor appearance change without any explanation of what happened or why. They have no easy way to understand the change, revert to their previous theme, or browse alternatives.

## Expected Behavior

When an existing user's color theme changes because the product default was updated, VS Code should display a one-time notification informing them about the new look. The notification should offer options to browse other themes or revert to the previous default theme.

## Actual Behavior

The theme changes silently with no notification. Users who were using the inherited default theme find their editor looking different after an update, with no context about the change and no convenient way to revert. The `showNewDefaultThemeNotification` method is called during initialization, but there is no corresponding notification for users whose theme was auto-updated due to a default change.

## Files to Look At

- `src/vs/workbench/services/themes/browser/workbenchThemeService.ts`
