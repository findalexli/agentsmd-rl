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

## Where to Look

The crash happens in `packages/shared/ReactPerformanceTrackProperties.js` during the prop diffing process. This file contains logic for adding values and object diffs to performance properties.

## Files Likely Involved

- `packages/shared/ReactPerformanceTrackProperties.js` - Contains `addValueToProperties` and `addObjectDiffToProperties` functions

## Reproduction

The issue manifests when:
1. A component has props containing DOM elements (like iframes)
2. React tries to diff those props for performance tracking
3. Accessing certain properties on the cross-origin window throws a security error

## Hint

The fix needs to safely check for the existence of a special React property before accessing it on arbitrary objects. This property is used to identify React elements. Consider how to safely read properties that might throw on security-restricted objects.
