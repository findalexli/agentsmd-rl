# Add changeDetection feature flag

## Problem

Storybook's configuration system is missing a `changeDetection` feature flag. This flag needs to be added so that change detection behavior can be toggled via the `features` configuration in `.storybook/main.ts`. Currently, there is no way for users to configure this option because it doesn't exist in the type system, isn't set in the default presets, and isn't documented.

## Expected Behavior

The `changeDetection` feature flag should be:

1. Declared in the TypeScript type interface for Storybook features, so users get autocompletion and type checking when configuring it
2. Set to `false` by default in the features preset (the feature is off by default)
3. Documented in the features configuration reference alongside the other feature flags

## Files to Look At

- `code/core/src/types/modules/core-common.ts` — TypeScript interface defining all Storybook configuration options, including feature flags
- `code/core/src/core-server/presets/common-preset.ts` — Default preset values for all feature flags
- `docs/api/main-config/main-config-features.mdx` — Documentation for the features configuration options
