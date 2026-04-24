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

## Requirements

The fix must:
1. Introduce a helper function to safely access the `$$typeof` property on arbitrary objects, including cross-origin proxies that throw on direct property access
2. Use an approach that does NOT invoke getters (to avoid security errors on cross-origin objects)
3. Use an approach that checks only own properties (not inherited ones from the prototype chain)
4. Define the helper before the functions that need to use it
5. Replace all direct `$$typeof` property accesses in `addValueToProperties` and `addObjectDiffToProperties` with calls to the helper

The target file is `packages/shared/ReactPerformanceTrackProperties.js`.