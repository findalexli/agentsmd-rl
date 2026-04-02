# Bug Report: React DevTools context menu crashes due to null ref access

## Problem

The context menu in React DevTools crashes with a null reference error when it is rendered. The `ContextMenu` component uses `createRef()` as a default value for its `ref` prop, which means a new ref object is created on every render. Because `createRef()` returns a ref with an initial value of `null`, and the `useLayoutEffect` hook immediately tries to access `ref.current` as an `HTMLElement`, the effect runs before the DOM element is attached to the ref — or runs even when the component returns `null` early (no portal container, empty items list). This leads to a crash when calling methods like `contains()` on a null value.

## Expected Behavior

The context menu should open and close without errors, properly registering and cleaning up window event listeners for click, resize, and keydown events.

## Actual Behavior

The component crashes when the `useLayoutEffect` fires and attempts to use `ref.current` as a DOM element while it is `null`. The effect also lacks proper guards for cases where the component would render nothing.

## Files to Look At

- `packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js`
- `packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenuContainer.js`
