# Add a setting to disable console log dimming in Strict Mode

## Problem

React DevTools dims the second (duplicate) console log that occurs during Strict Mode's double invocation. This dimming uses ANSI escape codes to make the repeated log appear gray, signaling to the developer that it came from Strict Mode's extra render pass.

However, there is no way to disable this dimming behavior. Some developers find the dimming confusing or prefer to see all logs at full visibility. While there is already a setting to *hide* the duplicate Strict Mode logs entirely (`hideConsoleLogsInStrictMode`), there is no option to keep them visible but remove the dimming effect.

## Expected Behavior

A new boolean setting `disableSecondConsoleLogDimmingInStrictMode` should be added to the DevTools hook settings. When enabled, the second console log during Strict Mode rendering should be output at normal visibility (no ANSI dimming codes). The default should be `false` (dimming stays on by default).

This setting should:
1. Be defined in the `DevToolsHookSettings` type
2. Default to `false` in the hook's initial settings
3. Be checked in the console patching logic that applies dimming
4. Have a UI checkbox in the Debugging settings panel
5. Be validated in the hook settings injector for the browser extension
6. Be passed through the inline DevTools backend

When `hideConsoleLogsInStrictMode` is enabled, this new setting should be visually disabled since there are no logs to dim.

## Files to Look At

- `packages/react-devtools-shared/src/hook.js` — console patching logic that applies ANSI dimming
- `packages/react-devtools-shared/src/backend/types.js` — `DevToolsHookSettings` type definition
- `packages/react-devtools-shared/src/devtools/views/Settings/DebuggingSettings.js` — settings UI
- `packages/react-devtools-extensions/src/contentScripts/hookSettingsInjector.js` — settings validation for browser extension
- `packages/react-devtools-inline/src/backend.js` — inline DevTools backend activation

After making the code changes, update `packages/react-devtools-core/README.md` to document the new setting in the Settings table. The table currently lists the existing settings with their types and defaults — the new setting should be added in the same format.
