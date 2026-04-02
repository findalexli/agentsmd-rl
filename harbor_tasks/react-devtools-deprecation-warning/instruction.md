# Bug Report: React DevTools shows wrong build type icon when multiple renderers are present

## Problem

When a page uses multiple React renderers (e.g., React DOM and React Three Fiber, or a mix of production and development builds), the DevTools browser extension icon and popup display whichever renderer attached *last*, rather than showing the most informative build type. This means if a development build attaches first but a production build attaches second, the extension icon switches to the production icon — hiding the fact that a non-production build is present on the page. The deprecation warning and build type indicator are therefore unreliable on pages with multiple renderers.

## Expected Behavior

When multiple React renderers are present on a page, the extension icon should reflect the "worst" (most notable) build type. If any renderer is a development or outdated build, that should take priority over production builds so the developer is properly warned.

## Actual Behavior

Each renderer attachment overwrites the previous build type unconditionally. The last renderer to attach dictates the icon, potentially masking development or deprecated builds behind a production indicator.

## Files to Look At

- `packages/react-devtools-extensions/src/contentScripts/installHook.js`
- `packages/react-devtools-extensions/src/background/setExtensionIconAndPopup.js`
- `packages/react-devtools-shared/src/backend/types.js`
- `packages/react-devtools-shared/src/hook.js`
