# Enable Fragment Ref Flags Across Build Configurations

The Fragment Refs feature has been implemented but is not fully enabled across all build configurations. We need to enable the remaining Fragment Ref feature flags that are still set to `false`.

## Files to Modify

1. `packages/shared/ReactFeatureFlags.js` — Main default flags
2. `packages/shared/forks/ReactFeatureFlags.native-oss.js` — React Native OSS build
3. `packages/shared/forks/ReactFeatureFlags.test-renderer.js` — Test renderer
4. `packages/shared/forks/ReactFeatureFlags.test-renderer.www.js` — Test renderer www build

## Task

Enable the following feature flags:

1. In `packages/shared/ReactFeatureFlags.js`:
   - `enableFragmentRefsInstanceHandles` should be `true`

2. In `packages/shared/forks/ReactFeatureFlags.native-oss.js`:
   - `enableFragmentRefsInstanceHandles` should be `true`
   - `enableFragmentRefsTextNodes` should be `true`

3. In `packages/shared/forks/ReactFeatureFlags.test-renderer.js`:
   - `enableFragmentRefsInstanceHandles` should be `true`

4. In `packages/shared/forks/ReactFeatureFlags.test-renderer.www.js`:
   - `enableFragmentRefs` should be `true`
   - `enableFragmentRefsScrollIntoView` should be `true`
   - `enableFragmentRefsInstanceHandles` should be `true`
   - `enableFragmentRefsTextNodes` should be `true`

## Notes

- These are JavaScript/Flow files that export boolean constants
- Keep the existing type annotation (`: boolean`) for each flag
- Only change the values from `false` to `true` for the flags specified above
- Other feature flags in these files should remain unchanged
