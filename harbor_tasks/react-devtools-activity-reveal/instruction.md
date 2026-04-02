# Bug Report: React DevTools fails to show children when Activity component is revealed

## Problem

When using React DevTools to inspect a component tree that includes `<Activity>` (formerly `<Offscreen>`) components, children that were previously hidden and then revealed do not appear in the DevTools component tree. This means that if an Activity component transitions from a hidden state to a visible state, its children remain invisible in the DevTools inspector even though they are rendering correctly in the actual DOM.

## Expected Behavior

When an `<Activity>` component transitions from hidden to visible (e.g., `mode="hidden"` changing to `mode="visible"`), its children should appear in the React DevTools component tree, correctly reflecting the current state of the rendered UI.

## Actual Behavior

After revealing a previously hidden `<Activity>` component, the DevTools tree does not display its children. The component tree appears empty under the Activity node despite the children being rendered and visible on screen. This occurs because the children were unmounted from DevTools tracking when hidden, but are never re-mounted into the DevTools tree upon reveal.

## Files to Look At

- `packages/react-devtools-shared/src/backend/fiber/renderer.js`
