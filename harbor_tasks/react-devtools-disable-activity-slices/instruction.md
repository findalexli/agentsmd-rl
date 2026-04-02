# Disable Activity Slices in React DevTools

The Activity slices feature in React DevTools needs to be disabled by default. This feature is not ready for release and should only be enabled in development builds, not in production builds.

The feature needs to be controlled by a new feature flag called `enableActivitySlices`. This flag should:
- Be `false` for internal Facebook builds (core-fb and extension-fb configurations)
- Use `__DEV__` for open source builds (core-oss, extension-oss, and default configurations), so it's enabled in development but disabled in production

The flag needs to be consumed in the SuspenseTab component to control whether the activity list panel is shown. When the flag is disabled, the activity list should be hidden regardless of whether there are activities to display.

Relevant files:
- `packages/react-devtools-shared/src/config/` - Contains the feature flag configurations for different build types
- `packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js` - The component that needs to check the flag

**Note:** The feature flag system in React DevTools uses separate files for different build configurations. Any new flag must be added consistently across all configuration files.
