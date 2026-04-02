# Bug Report: `enableComponentPerformanceTrack` flag should be static, not dynamically gated

## Problem

The `enableComponentPerformanceTrack` feature flag is currently configured as a dynamic flag in several platform-specific feature flag forks (native-fb, www). This means it can be toggled at runtime via experiments infrastructure. However, this flag has been stabilized and should now be unconditionally enabled — treating it as a dynamic/variant-controlled flag causes inconsistent behavior across builds and prevents dead-code elimination during compilation.

In the native-fb fork, the flag is additionally gated behind `__PROFILE__`, meaning it is completely disabled in production builds even though the feature is ready for general availability.

## Expected Behavior

`enableComponentPerformanceTrack` should be statically set to `true` across all platform forks, allowing the compiler to inline and optimize around it consistently. It should no longer appear in dynamic flag sets.

## Actual Behavior

The flag is exported from dynamic flag modules and destructured from the dynamic flags object, causing unnecessary runtime overhead and inconsistent enablement across build targets.

## Files to Look At

- `packages/shared/forks/ReactFeatureFlags.native-fb-dynamic.js`
- `packages/shared/forks/ReactFeatureFlags.native-fb.js`
- `packages/shared/forks/ReactFeatureFlags.www-dynamic.js`
- `packages/shared/forks/ReactFeatureFlags.www.js`
