# Enable view transition feature flag for React Native FB builds

## Problem

The `enableViewTransition` feature flag is disabled in the React Native Facebook build configuration. The flag is already enabled in the main `ReactFeatureFlags.js` (used by canary builds), but the RN-specific fork files still have it set to `false`. This means view transition support is unavailable in the React Native FB build and its test renderers.

Tests gated with `// @gate enableViewTransition` are being skipped in RN FB channel testing because the flag is off.

## Expected Behavior

The `enableViewTransition` flag should be set to `true` in the relevant RN FB and test-renderer fork files so that view transitions are available in the React Native Facebook build, matching the main flag file's setting.

## Files to Look At

- `packages/shared/forks/ReactFeatureFlags.native-fb.js` — RN FB channel flags
- `packages/shared/forks/` — all fork files for different build channels
