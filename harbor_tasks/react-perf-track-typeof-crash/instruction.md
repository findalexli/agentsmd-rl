# React Performance Track: Crash When Diffing Props with Cross-Origin Objects

## Problem

React's performance tracking crashes when diffing component props that contain DOM objects from cross-origin contexts (such as iframes with opaque origins). The crash occurs because accessing certain properties on these objects throws security errors.

## Example Scenario

When a component receives props containing an iframe element:
```jsx
function App({ container }) {
  useEffect(() => {}, [container]);
  // ...
}

// Passing an iframe element
<App container={iframeElement} />
```

React's performance tracking tries to diff the props to show what changed between renders. However, it crashes when trying to read properties on the cross-origin `contentWindow` of the iframe.

## Expected Behavior

React should gracefully handle cross-origin objects during prop diffing without crashing. The performance track should be able to diff these objects and display their properties (like `nodeType`, `textContent`, `contentWindow`) in the DevTools timeline.

## Reproduction

The issue manifests when:
1. A component has props containing DOM elements (like iframes)
2. React tries to diff those props for performance tracking
3. Accessing certain properties on the cross-origin window throws a security error

## Requirements

The fix must:
1. Introduce a helper function with a name matching the pattern `readReactElementTypeof` (the exact name is verified by tests)
2. Use the `in` operator to check for the `$$typeof` property without triggering getter traps on cross-origin objects
3. Use `hasOwnProperty.call` to ensure only own properties are checked (not inherited ones)
4. The helper must be defined before the `addValueToProperties` function uses it
5. Replace all direct `$$typeof` accesses in `addValueToProperties` and `addObjectDiffToProperties` with calls to this helper

The target file is `packages/shared/ReactPerformanceTrackProperties.js`.