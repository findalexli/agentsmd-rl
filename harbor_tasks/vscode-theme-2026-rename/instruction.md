# Theme Rename: VS Code Dark/Light → Dark 2026/Light 2026

The default color themes need to be renamed from their current names to simpler "Dark 2026" and "Light 2026" variants. This change affects multiple components of the theme system.

## Problem

When the theme IDs and labels are updated, users with existing settings referencing the old theme names will not have their themes properly migrated. The `migrateThemeSettingsId` function in the workbench theme service currently maps some legacy theme IDs like "Experimental Dark" and "Experimental Light" to their modern equivalents, but it needs to also handle the upcoming rename of the default themes.

## Files to Modify

1. **`src/vs/workbench/services/themes/common/workbenchThemeService.ts`**
   - Update `ThemeSettingDefaults.COLOR_THEME_DARK` and `COLOR_THEME_LIGHT` constants to use the new names
   - Extend `migrateThemeSettingsId` to map both "Experimental Dark"/"Experimental Light" AND "VS Code Dark"/"VS Code Light" to the appropriate new theme IDs

2. **`src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts`**
   - Import the `ThemeSettingDefaults` constants
   - Replace the hardcoded `'workbench.colorTheme': 'VS Code Dark'` with the constant reference

3. **`extensions/theme-defaults/package.json`** and **`extensions/theme-defaults/package.nls.json`**
   - Update theme IDs and localization keys to use "Dark 2026" and "Light 2026"

## Requirements

- The migration function must handle both old experimental theme IDs AND the old "VS Code Dark"/"VS Code Light" IDs
- Use the `ThemeSettingDefaults` constants consistently instead of string literals in configuration defaults
- Ensure existing theme migrations (Default Dark Modern → Dark Modern, etc.) continue to work
- All theme references must use the new naming convention
