# Simplify eslint-plugin-react-hooks preset configurations for v7.0.0

## Problem

The `eslint-plugin-react-hooks` package currently exposes too many configuration presets, creating confusion for users. There are five named configs (`recommended`, `recommended-legacy`, `recommended-latest-legacy`, `flat/recommended`, `recommended-latest`) plus their flat equivalents, many of which exist only for backwards compatibility with older ESLint or plugin versions.

Additionally, the `recommended` preset only enables the two basic hooks rules (`rules-of-hooks` and `exhaustive-deps`) but does not include the React Compiler rules, which should now be on by default.

## Expected Behavior

Slim down to just 2 configuration presets:

- **`recommended`**: includes ALL recommended rules (both basic hooks rules and compiler rules)
- **`recommended-latest`**: same as recommended plus any bleeding-edge experimental compiler rules

The removed presets (`recommended-legacy`, `recommended-latest-legacy`, `flat/recommended`) and their flat config equivalents should be deleted entirely from `packages/eslint-plugin-react-hooks/src/index.ts`.

The plugin's `meta` object should also include a `version` field.

After making the code changes, update the package's README to reflect the simplified configuration. The README currently has version-specific installation sections (for different ESLint/plugin versions) that are no longer needed — these should be consolidated into clean, simple instructions. The custom configuration examples in the README should also be updated to show the full set of available rules including compiler rules.

## Files to Look At

- `packages/eslint-plugin-react-hooks/src/index.ts` — plugin entry point with config definitions
- `packages/eslint-plugin-react-hooks/README.md` — installation and usage documentation
- `packages/eslint-plugin-react-hooks/CHANGELOG.md` — add a 7.0.0 entry for the breaking change
- `packages/eslint-plugin-react-hooks/package.json` — version field
- `ReactVersions.js` — central version registry
- `fixtures/eslint-v6/.eslintrc.json`, `fixtures/eslint-v7/.eslintrc.json`, `fixtures/eslint-v8/.eslintrc.json` — update preset references
