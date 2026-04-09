# DevTools: Suspense timeline milestone update crashes with multiple renderers

## Problem

In the React DevTools Suspense tab, when the user changes the Suspense timeline milestone (scrubbing through the timeline to see progressive loading states), the DevTools backend crashes if multiple React renderers are attached to the page.

The root cause is that the milestone update is broadcast to every renderer indiscriminately. Each renderer may have different features and fiber structures, so sending a fiber from one renderer to another causes a crash. For example, if React canary and React experimental are both attached, a milestone update references fiber properties (like `pendingIndicator`) that only exist in one version but not the other, resulting in `undefined` access errors.

## Expected Behavior

The Suspense timeline milestone update should be scoped to the specific renderer that owns the affected suspension boundaries. Each renderer should only receive updates for fibers it manages, and the timeline step data should carry enough information to route updates correctly.

## Files to Look At

- `packages/react-devtools-shared/src/backend/agent.js` — handles the `overrideSuspenseMilestone` action dispatched from the frontend
- `packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTimeline.js` — UI component that triggers milestone changes when the user scrubs the timeline
- `packages/react-devtools-shared/src/devtools/store.js` — computes the timeline step data used by the UI
- `packages/react-devtools-shared/src/bridge.js` — defines bridge message types between frontend and backend
- `packages/react-devtools-shared/src/frontend/types.js` — frontend type definitions including timeline step shape
