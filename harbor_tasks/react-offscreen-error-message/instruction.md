# Bug Report: Error messages reference "Offscreen" instead of the actual component name

## Problem

When a React component wrapped in an offscreen boundary (such as content hidden with the `<Activity>` / `<Offscreen>` API) throws an error, the resulting error message displays "Offscreen" as the component name rather than the name of the actual component involved. This makes debugging significantly harder because developers see unhelpful error messages like `"Offscreen" failed to render` instead of the real component that caused the issue.

## Expected Behavior

Error messages and warnings involving components inside offscreen trees should report the actual parent component name, not the internal "Offscreen" fiber wrapper. The offscreen wrapper is an implementation detail and should be transparent when surfacing component names to developers.

## Actual Behavior

`getComponentNameFromFiber` returns the hardcoded string `"Offscreen"` for offscreen fiber nodes, causing any error or warning that references this fiber to display "Offscreen" as the component name. This leaks an internal implementation detail into developer-facing messages.

## Files to Look At

- `packages/react-reconciler/src/getComponentNameFromFiber.js`
