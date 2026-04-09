# enableViewTransition not enabled for RN FB builds

## Problem

The `enableViewTransition` feature flag is set to `false` in the React Native Facebook (RN FB) build variant and its associated test-renderer forks. This means view transition features are unavailable in the RN FB channel, even though they should be enabled to match the current state of the codebase.

## Expected Behavior

`enableViewTransition` should be set to `true` in all RN FB–related flag fork files so the feature is active in that build channel.

## Files to Look At

- `packages/shared/forks/ReactFeatureFlags.native-fb.js` — Feature flags for the RN FB build variant
- `packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js` — Test renderer flags for RN FB
- `packages/shared/forks/ReactFeatureFlags.test-renderer.www.js` — Test renderer flags for the www channel
