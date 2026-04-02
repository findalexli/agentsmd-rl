## Bug Report: DevTools Memory Leak on Hoistable Element Unmount

The React DevTools fiber renderer has a memory leak when unmounting host hoistables (elements like `<style>` tags that may be deduplicated by React's Float system).

### Expected Behavior

When multiple components reference the same deduplicated hoistable element (e.g., both render the same `<style>` tag with matching `href` and `precedence`), and one component unmounts, the DevTools should properly update its internal instance mapping. The remaining component should continue to correctly reference the shared DOM element without causing a memory leak.

### Actual Behavior

When a host hoistable is unmounted, the DevTools fiber renderer attempts to update `publicInstanceToDevToolsInstanceMap` to point remaining Fiber instances to the same public host instance. However, the arguments to the `Map.set()` call appear to be incorrect. This causes:

1. Memory leaks - stale entries accumulate in the map
2. Potential issues with element inspection for hoistables

### Files to Examine

Focus on the `releaseHostResource` function in:
- `packages/react-devtools-shared/src/backend/fiber/renderer.js`

Look for where `publicInstanceToDevToolsInstanceMap.set()` is called when cleaning up host resources - specifically when iterating over `resourceInstances`.

### Context

- Host hoistables can be shared/deduplicated across multiple components
- When one component unmounts, the renderer needs to update internal mappings
- The `publicInstanceToDevToolsInstanceMap` maps public host instances to DevTools internal instances

### Testing

The test file `packages/react-devtools-shared/src/__tests__/store-test.js` contains relevant test cases for Store behavior. Running tests with a pattern like "cleans up host hoistables" should reveal the issue.
