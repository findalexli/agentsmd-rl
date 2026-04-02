# React DevTools: Fix Crash When Renaming Props on Host Components

## Problem

When using React DevTools to edit (rename) props on Host Components like `<input>`, `<div>`, or other DOM elements, the DevTools extension crashes with an error. This happens because the code incorrectly attempts to call `forceUpdate()` on Host Components, which don't implement this method (it's a Class Component API).

## Location

The bug is in the DevTools Fiber renderer backend:
- **File**: `packages/react-devtools-shared/src/backend/fiber/renderer.js`
- **Function**: `renamePath` within the `attach` function (around the `case 'props':` section)

## Current Behavior

When renaming a prop path on a component, the code checks if `instance === null`:
- If null: uses `overridePropsRenamePath(fiber, oldPath, newPath)`
- If not null: directly mutates `fiber.pendingProps` and calls `instance.forceUpdate()`

The problem is that Host Components (DOM elements like `<input>`) **do have an instance** (the DOM node), but **don't have a `forceUpdate` method**. Thus, the current code crashes when trying to rename props on them.

## Expected Behavior

Renaming props on Host Components should work like it does for Function Components:
- Use `overridePropsRenamePath()` to handle the prop renaming
- Don't call `forceUpdate()` on components that don't implement it

Class Components should continue to use `forceUpdate()` as they do now.

## Test Case Reference

The editing tests in `packages/react-devtools-shared/src/__tests__/editing-test.js` contain tests for component prop editing. Look for the test that involves renaming props on a Host Component.

## Hints

1. Look at how props are set (not renamed) in the same function for guidance - there's a switch on `fiber.tag` there that handles Class Components specially
2. The `ClassComponent` constant is defined in the same file and can be used in a switch statement
3. Refer to the `overridePropsRenamePath` usage pattern that's already there for the case when `instance === null`
4. Run the editing tests to verify: `yarn test --testPathPattern='editing-test'`

## Related Concepts

- **Fiber**: React's internal architecture for components
- **Host Components**: DOM elements rendered by React (`<div>`, `<input>`, etc.)
- **Class Components**: React class-based components with lifecycle methods
- **overridePropsRenamePath**: Function to handle prop renaming via the DevTools backend
