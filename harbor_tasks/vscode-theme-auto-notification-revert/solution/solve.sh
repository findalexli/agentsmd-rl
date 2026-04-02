#!/bin/bash
set -euo pipefail

# This script removes the showThemeAutoUpdatedNotification method and its call
# This is the revert of PR #306340

THEME_SERVICE_FILE="src/vs/workbench/services/themes/browser/workbenchThemeService.ts"

cd /workspace/vscode

# Check if already applied (idempotency check)
# After the fix, showThemeAutoUpdatedNotification should NOT exist
if ! grep -q "showThemeAutoUpdatedNotification" "$THEME_SERVICE_FILE"; then
    echo "Fix already applied (showThemeAutoUpdatedNotification not found)"
    exit 0
fi

# Create the patch to remove the notification method and its call
git apply - <<'PATCH'
diff --git a/src/vs/workbench/services/themes/browser/workbenchThemeService.ts b/src/vs/workbench/services/themes/browser/workbenchThemeService.ts
index 1fe6515a6011c..20d45050cfac3 100644
--- a/src/vs/workbench/services/themes/browser/workbenchThemeService.ts
+++ b/src/vs/workbench/services/themes/browser/workbenchThemeService.ts
@@ -249,7 +249,6 @@ export class WorkbenchThemeService extends Disposable implements IWorkbenchTheme
 		await this.migrateAutoDetectColorScheme();
 		const result = await Promise.all([initializeColorTheme(), initializeFileIconTheme(), initializeProductIconTheme()]);
 		this.showNewDefaultThemeNotification();
-		this.showThemeAutoUpdatedNotification();
 		return result;
 	}

@@ -277,56 +276,6 @@ export class WorkbenchThemeService extends Disposable implements IWorkbenchTheme
 		}));
 	}

-	private static readonly THEME_AUTO_UPDATED_NOTIFICATION_KEY = 'workbench.themeAutoUpdatedNotification';
-
-	/**
-	 * Shows a one-time notification to existing users whose color theme changed
-	 * because the product default was updated (e.g. Dark Modern → VS Code Dark).
-	 * Offers the option to browse themes or revert to the previous default.
-	 */
-	private showThemeAutoUpdatedNotification(): void {
-		if (this.storageService.getBoolean(WorkbenchThemeService.THEME_AUTO_UPDATED_NOTIFICATION_KEY, StorageScope.APPLICATION)) {
-			return; // already shown
-		}
-		if (this.storageService.isNew(StorageScope.APPLICATION)) {
-			return; // new user, no migration happened
-		}
-
-		// Target existing users whose theme changed because the default changed.
-		// These users have no explicit user-scoped theme value — they inherited the default.
-		const newDefaultThemes = new Set([ThemeSettingDefaults.COLOR_THEME_DARK, ThemeSettingDefaults.COLOR_THEME_LIGHT]);
-		if (!newDefaultThemes.has(this.currentColorTheme.settingsId)) {
-			return; // not using a new default theme
-		}
-		if (!this.settings.isDefaultColorTheme()) {
-			return; // user explicitly chose this theme
-		}
-
-		const previousSettingsId = this.currentColorTheme.type === ColorScheme.LIGHT ? 'Light Modern' : 'Dark Modern';
-
-		const handle = this.notificationService.prompt(
-			Severity.Info,
-			nls.localize({ key: 'newDefaultThemeAutoUpdated', comment: ['{0} is the name of the current color theme, e.g. "VS Code Dark"'] }, "VS Code: has a new look! You can keep {0}, switch to another theme, or go back to your previous one.", this.currentColorTheme.label),
-			[{
-				label: nls.localize('browseThemes', "Browse Themes"),
-				run: () => this.commandService.executeCommand('workbench.action.selectTheme')
-			}, {
-				label: nls.localize('revertTheme', "Revert"),
-				run: () => {
-					const previousTheme = this.colorThemeRegistry.findThemeBySettingsId(previousSettingsId);
-					if (previousTheme) {
-						this.setColorTheme(previousTheme.id, 'auto');
-					}
-				}
-			}]
-		);
-		this._register(Event.once(handle.onDidClose)(() => {
-			this.storageService.store(WorkbenchThemeService.THEME_AUTO_UPDATED_NOTIFICATION_KEY, true, StorageScope.APPLICATION, StorageTarget.USER);
-			// Also suppress the "try new themes" notification — this user is already aware of the new themes.
-			this.storageService.store(WorkbenchThemeService.NEW_THEME_NOTIFICATION_KEY, true, StorageScope.APPLICATION, StorageTarget.USER);
-		}));
-	}
-
 	/**
 	 * Migrates legacy theme setting values to their current equivalents,
 	 * writing back the migrated value so settings sync distributes the correct ID.
PATCH

echo "Applied fix: removed showThemeAutoUpdatedNotification method and its call"
