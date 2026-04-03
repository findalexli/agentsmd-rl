# Enable console.error for Recoverable Errors in Noop Renderer

The React noop renderer (`packages/react-noop-renderer/src/createReactNoop.js`) has a `onRecoverableError` callback that is supposed to log recoverable errors. However, the `console.error(error)` call is commented out with a TODO comment: "Turn this on once tests are fixed".

This means recoverable errors in tests using the noop renderer are silently swallowed, making it harder to detect and debug issues. The tests that previously failed with this enabled have since been fixed.

Enable the `console.error(error)` call in `onRecoverableError`, add the appropriate eslint-disable comment (since `react-internal/no-production-logging` and `react-internal/warning-args` rules would flag it), and add a Flow type annotation to the function signature.
