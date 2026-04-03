# expo-router: Replace direct RNScreens type casts with KVC-based compat layer

## Problem

The `LinkPreviewNativeNavigation.swift` file in `packages/expo-router/ios/LinkPreview/` directly casts views to concrete class names from `react-native-screens` (`RNSBottomTabsScreenComponentView`, `RNSBottomTabsHostComponentView`). When react-native-screens 4.24.0 renamed these classes, the casts silently fail, breaking link preview navigation for tab-based layouts.

The code needs to work with **both** react-native-screens 4.23.0 and 4.24.0 without requiring a specific version.

## Expected Behavior

Instead of casting to concrete class names (which break when the library renames its types), the code should detect tab views dynamically — for example using KVC (`responds(to:)` / `value(forKey:)`) or a similar pattern that doesn't depend on exact type names.

The fix should:
1. Create a compatibility utility that abstracts tab view detection and property access
2. Replace all direct `as? RNSBottomTabsScreenComponentView` and `as? RNSBottomTabsHostComponentView` casts in `LinkPreviewNativeNavigation.swift` with calls to this utility
3. Add native Swift tests for the new compatibility layer using the project's Swift Testing conventions
4. Update the podspec to include a test spec for the new tests
5. After making the code changes, update the project's agent instructions (`packages/expo-router/CLAUDE.md`) to document the new Swift testing setup — where native tests live, how to run them, and what conventions to follow (the project now has native Swift tests in addition to the existing Jest tests)

## Files to Look At

- `packages/expo-router/ios/LinkPreview/LinkPreviewNativeNavigation.swift` — the file with direct type casts that need replacing
- `packages/expo-router/ios/ExpoRouter.podspec` — needs a test spec added
- `packages/expo-router/CLAUDE.md` — project documentation that should be updated to cover native Swift testing
