# [DevTools] Fix null ref crash in ContextMenu when items list is empty

## Problem

In the React DevTools profiler Timeline view, right-clicking on the canvas before hovering over a specific event causes a crash:

```
TypeError: Cannot read properties of null (reading 'ownerDocument')
```

The `ContextMenu` component crashes when rendered with an empty `items` array. The component correctly returns `null` for the empty-items case, but its `useLayoutEffect` hook still fires and tries to operate on a ref whose `.current` value is `null`. The effect accesses DOM properties on `ref.current` unconditionally, causing the TypeError.

## Expected Behavior

The `ContextMenu` component should handle the case where `items` is empty (or the portal container is missing) without crashing. The `useLayoutEffect` hook should not attempt to access DOM elements when the menu is hidden.

## Files to Look At

- `packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js` — the component with the crashing `useLayoutEffect`
- `packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenuContainer.js` — parent component that renders ContextMenu
