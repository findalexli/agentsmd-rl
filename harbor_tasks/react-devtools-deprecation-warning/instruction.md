# Bug Report: React DevTools shows wrong build type icon when multiple renderers are present

## Problem

When a page uses multiple React renderers (e.g., React DOM and React Three Fiber, or a mix of production and development builds), the DevTools browser extension icon and popup display whichever renderer attached *last*, rather than showing the most informative build type. This means if a development build attaches first but a production build attaches second, the extension icon switches to the production icon — hiding the fact that a non-production build is present on the page. The deprecation warning and build type indicator are therefore unreliable on pages with multiple renderers.

## Expected Behavior

When multiple React renderers are present on a page, the extension icon should reflect the "worst" (most notable) build type. If any renderer is a development or outdated build, that should take priority over production builds so the developer is properly warned.

The `ReactBuildType` type represents build types with the following literal values:
- `'production'`
- `'development'`
- `'outdated'`
- `'deadcode'`
- `'unminified'`

The logic for determining which build type takes priority is as follows:

- **First renderer wins**: When there is no current build type (first renderer to attach), the new build type is accepted unconditionally.
- **Non-production beats production**: When the current build type is `'production'` and a non-production build type (`'development'`, `'outdated'`, `'deadcode'`, or `'unminified'`) arrives, the non-production value wins.
- **Production does not downgrade**: When the current build type is a non-production value, subsequent `'production'` attachments must NOT overwrite it — the non-production value is preserved.
- **Non-production can upgrade to worse non-production**: When both current and next are non-production, the worse (more notable) build type wins — newer non-production values replace older ones.

## Actual Behavior

Each renderer attachment overwrites the previous build type unconditionally. The last renderer to attach dictates the icon, potentially masking development or deprecated builds behind a production indicator.

## Implementation Requirements

A new file must be created at `packages/react-devtools-extensions/src/contentScripts/reactBuildType.js` that exports two functions:

1. **`reduceReactBuild(current, next)`** — Takes the current build type (or `null`) and the next build type, and returns the resolved build type following the priority rules above:
   - `reduceReactBuild(null, x)` returns `x` for any build type `x`
   - `reduceReactBuild('production', x)` returns `x` for any non-production `x`
   - `reduceReactBuild(x, 'production')` returns `x` when `x` is non-production
   - `reduceReactBuild(x, y)` returns the worse build type when both are non-production

2. **`createReactRendererListener(window)`** — Takes a window-like object (with a `postMessage` method) and returns a renderer listener function. The listener must:
   - Maintain internal state tracking the worst build type seen so far across all renderer attachments.
   - On each renderer attachment event, call `window.postMessage` with a payload containing `type: 'react-renderer-attached'` and the current worst `reactBuildType`.
   - Each returned listener maintains independent state (not shared with other listeners created by the same factory call).

The `installHook.js` file (at `packages/react-devtools-extensions/src/contentScripts/installHook.js`) must import and use `createReactRendererListener` instead of the current inline renderer callback. The old inline `postMessage` with `'react-renderer-attached'` type in the renderer handler must be replaced by the factory.

The `ReactBuildType` type union must be exported from `packages/react-devtools-shared/src/backend/types.js` as a Flow type with all five literal values: `'production'`, `'development'`, `'outdated'`, `'deadcode'`, and `'unminified'`.

## Files to Look At

- `packages/react-devtools-extensions/src/contentScripts/installHook.js`
- `packages/react-devtools-extensions/src/background/setExtensionIconAndPopup.js`
- `packages/react-devtools-shared/src/backend/types.js`
- `packages/react-devtools-shared/src/hook.js`