# Add Theme Auto-Updated Notification for Existing Users

When VS Code updates its default color themes (e.g., from "Dark Modern" to "VS Code Dark"), existing users who were using the previous default will automatically be switched to the new default. These users should be notified about the change with options to keep the new theme, browse alternatives, or revert.

The `WorkbenchThemeService` in `src/vs/workbench/services/themes/browser/workbenchThemeService.ts` currently has `showNewDefaultThemeNotification` for first-time users but lacks a notification for existing users whose theme changed via a default update.

Add a `showThemeAutoUpdatedNotification` method that:
1. Checks if the notification was already shown (using a storage key)
2. Skips new users (they didn't experience a migration)
3. Only targets users on the new default theme who didn't explicitly choose it
4. Shows a notification with "Browse Themes" and "Revert" options
5. Marks the notification as shown and suppresses the new-theme notification
