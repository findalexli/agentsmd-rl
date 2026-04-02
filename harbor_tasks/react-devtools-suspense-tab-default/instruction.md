# React DevTools: Enable Suspense Tab by Default

The React DevTools browser extension currently shows the Suspense tab conditionally based on a version check. The tab is only displayed when connected to a React renderer version 19.3.0-canary or higher that is built in development mode. This conditional behavior requires a waterfall on initial load and causes the DevTools tabs to shift once the check completes.

To improve the user experience and help with discovery, the Suspense tab should be shown unconditionally on initial release. The version-based feature gating logic needs to be removed.

## Task

Modify the React DevTools code to enable the Suspense tab by default in all cases. Look at the extension's main entry point, the backend agent, the bridge definitions, the store, and the DevTools view component.

Key areas to examine:
- `packages/react-devtools-extensions/src/main/index.js` — where panels are created
- `packages/react-devtools-shared/src/backend/agent.js` — where version checks are performed
- `packages/react-devtools-shared/src/devtools/views/DevTools.js` — where tabs are rendered

The fix should remove the dynamic feature detection and make the Suspense tab always visible.
