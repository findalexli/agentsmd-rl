# Bug Report: `enableTrustedTypesIntegration` flag is hardcoded instead of using dynamic variant

## Problem

The `enableTrustedTypesIntegration` feature flag in the www-dynamic fork of React's feature flags is hardcoded to `false` rather than being configured as a dynamic `__VARIANT__` flag. This means the Trusted Types integration cannot be toggled dynamically during testing or experimentation, unlike other feature flags in the same file. The flag is stuck in the "TODO" section of hardcoded flags that were never updated to support variant-based testing.

## Expected Behavior

The `enableTrustedTypesIntegration` flag should behave like other dynamic feature flags (e.g., `enableFragmentRefs`, `enableAsyncDebugInfo`) and be controllable via the `__VARIANT__` mechanism, allowing it to be tested in both enabled and disabled states during www builds.

## Actual Behavior

The flag is hardcoded to `false` in the www-dynamic feature flags fork, preventing any dynamic testing of Trusted Types integration. It sits in a section of flags marked as TODO items that need to be converted to `__VARIANT__`.

## Files to Look At

- `packages/shared/forks/ReactFeatureFlags.www-dynamic.js`
