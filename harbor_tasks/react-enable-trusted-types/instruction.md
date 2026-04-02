# Enable Trusted Types Integration

React has built-in support for the browser's Trusted Types API, a security feature that helps prevent DOM-based XSS attacks. However, this integration is currently disabled by default across all React build configurations.

When Trusted Types enforcement is enabled via Content-Security-Policy, browsers reject values passed to DOM injection sinks (like `innerHTML`) unless they are Trusted Types objects. React's implementation avoids string coercion for these values when the integration is enabled, preserving the trusted object types.

## Issue

The `enableTrustedTypesIntegration` feature flag is currently set to `false` in the main React feature flags file and needs to be enabled across all build configurations:

- `packages/shared/ReactFeatureFlags.js` - Main source flags
- `packages/shared/forks/ReactFeatureFlags.native-fb.js` - React Native FB build
- `packages/shared/forks/ReactFeatureFlags.native-oss.js` - React Native OSS build
- `packages/shared/forks/ReactFeatureFlags.test-renderer.js` - Test renderer
- `packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js` - Test renderer for RN FB
- `packages/shared/forks/ReactFeatureFlags.test-renderer.www.js` - Test renderer for www
- `packages/shared/forks/ReactFeatureFlags.www.js` - Meta internal www build

Additionally, since this flag is being enabled everywhere (not dynamically), it should be removed from the dynamic flags file:
- `packages/shared/forks/ReactFeatureFlags.www-dynamic.js`

## Goal

Enable the `enableTrustedTypesIntegration` flag by setting it to `true` in all relevant React feature flag files. Ensure consistency across all build configurations so Trusted Types objects are properly passed through to the DOM without string coercion.

## References

- Trusted Types API: https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API
