#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied (idempotency check)
if grep -q '"id": "Dark 2026"' extensions/theme-defaults/package.json 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/extensions/theme-defaults/package.json b/extensions/theme-defaults/package.json
index da70493255a8c..f4d04e5c55eb9 100644
--- a/extensions/theme-defaults/package.json
+++ b/extensions/theme-defaults/package.json
@@ -14,14 +14,14 @@
   "contributes": {
     "themes": [
       {
-        "id": "VS Code Light",
-        "label": "%vsCodeLightThemeLabel%",
+        "id": "Light 2026",
+        "label": "%light2026ThemeLabel%",
         "uiTheme": "vs",
         "path": "./themes/2026-light.json"
       },
       {
-        "id": "VS Code Dark",
-        "label": "%vsCodeDarkThemeLabel%",
+        "id": "Dark 2026",
+        "label": "%dark2026ThemeLabel%",
         "uiTheme": "vs-dark",
         "path": "./themes/2026-dark.json"
       },
diff --git a/extensions/theme-defaults/package.nls.json b/extensions/theme-defaults/package.nls.json
index 1e9bbdc6a59b2..df31243ef4a8e 100644
--- a/extensions/theme-defaults/package.nls.json
+++ b/extensions/theme-defaults/package.nls.json
@@ -1,8 +1,8 @@
 {
 	"displayName": "Default Themes",
 	"description": "The default Visual Studio light and dark themes",
-	"vsCodeLightThemeLabel": "VS Code Light",
-	"vsCodeDarkThemeLabel": "VS Code Dark",
+	"light2026ThemeLabel": "Light 2026",
+	"dark2026ThemeLabel": "Dark 2026",
 	"darkPlusColorThemeLabel": "Dark+",
 	"darkModernThemeLabel": "Dark Modern",
 	"lightPlusColorThemeLabel": "Light+",
diff --git a/src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts b/src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts
index 43deb1d4450ad..ab58adf1c9b68 100644
--- a/src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts
+++ b/src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts
@@ -5,6 +5,7 @@

 import { Extensions, IConfigurationRegistry } from '../../../../platform/configuration/common/configurationRegistry.js';
 import { Registry } from '../../../../platform/registry/common/platform.js';
+import { ThemeSettingDefaults } from '../../../../workbench/services/themes/common/workbenchThemeService.js';

 Registry.as<IConfigurationRegistry>(Extensions.Configuration).registerDefaultConfigurations([{
 	overrides: {
@@ -68,7 +69,7 @@ Registry.as<IConfigurationRegistry>(Extensions.Configuration).registerDefaultCon
 		'workbench.layoutControl.type': 'toggles',
 		'workbench.editor.useModal': 'all',
 		'workbench.panel.showLabels': false,
-		'workbench.colorTheme': 'VS Code Dark',
+		'workbench.colorTheme': ThemeSettingDefaults.COLOR_THEME_DARK,

 		'window.menuStyle': 'custom',
 		'window.dialogStyle': 'custom',
diff --git a/src/vs/workbench/services/themes/common/workbenchThemeService.ts b/src/vs/workbench/services/themes/common/workbenchThemeService.ts
index 040489ccad03e..88deb0af3215a 100644
--- a/src/vs/workbench/services/themes/common/workbenchThemeService.ts
+++ b/src/vs/workbench/services/themes/common/workbenchThemeService.ts
@@ -39,8 +39,8 @@ export enum ThemeSettings {
 }

 export namespace ThemeSettingDefaults {
-	export const COLOR_THEME_DARK = 'VS Code Dark';
-	export const COLOR_THEME_LIGHT = 'VS Code Light';
+	export const COLOR_THEME_DARK = 'Dark 2026';
+	export const COLOR_THEME_LIGHT = 'Light 2026';
 	export const COLOR_THEME_HC_DARK = 'Default High Contrast';
 	export const COLOR_THEME_HC_LIGHT = 'Default High Contrast Light';

@@ -59,8 +59,12 @@ export function migrateThemeSettingsId(settingsId: string): string {
 		case 'Default Light Modern': return 'Light Modern';
 		case 'Default Dark+': return 'Dark+';
 		case 'Default Light+': return 'Light+';
-		case 'Experimental Dark': return 'VS Code Dark';
-		case 'Experimental Light': return 'VS Code Light';
+		case 'Experimental Dark':
+		case 'VS Code Dark':
+			return ThemeSettingDefaults.COLOR_THEME_DARK;
+		case 'Experimental Light':
+		case 'VS Code Light':
+			return ThemeSettingDefaults.COLOR_THEME_LIGHT;
 	}
 	return settingsId;
 }
diff --git a/src/vs/workbench/services/themes/test/common/workbenchThemeService.test.ts b/src/vs/workbench/services/themes/test/common/workbenchThemeService.test.ts
index bdb41d71db563..2843b3ff46d98 100644
--- a/src/vs/workbench/services/themes/test/common/workbenchThemeService.test.ts
+++ b/src/vs/workbench/services/themes/test/common/workbenchThemeService.test.ts
@@ -4,7 +4,7 @@
  *--------------------------------------------------------------------------------------------*/

 import assert from 'assert';
-import { migrateThemeSettingsId } from '../../common/workbenchThemeService.js';
+import { migrateThemeSettingsId, ThemeSettingDefaults } from '../../common/workbenchThemeService.js';
 import { ensureNoDisposablesAreLeakedInTestSuite } from '../../../../../base/test/common/utils.js';
 import { ThemeConfiguration } from '../../common/themeConfiguration.js';
 import { TestConfigurationService } from '../../../../../platform/configuration/test/common/testConfigurationService.js';
@@ -28,15 +28,15 @@ suite('WorkbenchThemeService', () => {

 		test('migrates Experimental theme IDs to VS Code themes', () => {
 			assert.deepStrictEqual(
-				['Experimental Dark', 'Experimental Light'].map(migrateThemeSettingsId),
-				['VS Code Dark', 'VS Code Light']
+				['Experimental Dark', 'Experimental Light', 'VS Code Dark', 'VS Code Light'].map(migrateThemeSettingsId),
+				[ThemeSettingDefaults.COLOR_THEME_DARK, ThemeSettingDefaults.COLOR_THEME_LIGHT, ThemeSettingDefaults.COLOR_THEME_DARK, ThemeSettingDefaults.COLOR_THEME_LIGHT]
 			);
 		});

 		test('returns unknown IDs unchanged', () => {
 			assert.deepStrictEqual(
-				['Dark Modern', 'VS Code Dark', 'Some Custom Theme', ''].map(migrateThemeSettingsId),
-				['Dark Modern', 'VS Code Dark', 'Some Custom Theme', '']
+				['Dark Modern', 'Dark 2026', 'Some Custom Theme', ''].map(migrateThemeSettingsId),
+				['Dark Modern', 'Dark 2026', 'Some Custom Theme', '']
 			);
 		});
 	});
PATCH

echo "Patch applied successfully"
