# Remove Premature Theme Auto-Update Notification

The `WorkbenchThemeService` in `src/vs/workbench/services/themes/browser/workbenchThemeService.ts` contains a `showThemeAutoUpdatedNotification` method that was added prematurely. This notification is shown to existing users whose color theme changed because the product default was updated (e.g., Dark Modern to VS Code Dark), offering "Browse Themes" and "Revert" options.

However, this notification was added before the actual theme rename landed, causing it to fire incorrectly. It needs to be removed (reverted) until the theme rename is in place.

Remove the `showThemeAutoUpdatedNotification` method, its storage key constant (`THEME_AUTO_UPDATED_NOTIFICATION_KEY`), and the call to it in the `initialize` method. Keep `showNewDefaultThemeNotification` which is the correct notification mechanism.
