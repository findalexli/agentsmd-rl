# Rename VS Code Dark/Light Themes to Dark 2026/Light 2026

The VS Code default color themes are currently named "VS Code Dark" and "VS Code Light" with IDs matching these names. They need to be renamed to "Dark 2026" and "Light 2026" to follow the year-based naming convention.

This requires changes across multiple files:
1. `extensions/theme-defaults/package.json` — Update theme IDs and label references
2. `extensions/theme-defaults/package.nls.json` — Update localization labels
3. `src/vs/workbench/services/themes/common/workbenchThemeService.ts` — Update `ThemeSettingDefaults` constants and add migration for old names
4. `src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts` — Use `ThemeSettingDefaults` constant instead of hardcoded string
5. `src/vs/workbench/services/themes/test/common/workbenchThemeService.test.ts` — Update test expectations

The migration function `migrateThemeSettingsId` must be updated to map both "VS Code Dark"/"VS Code Light" and "Experimental Dark"/"Experimental Light" to the new names.
