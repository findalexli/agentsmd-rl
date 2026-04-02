# DevTools: Display React.optimisticKey in Component Tree

React 19.3 introduces `React.optimisticKey` - a special symbol used as a key for optimistic updates in React's concurrent features. However, when this key appears in React DevTools, it displays inconsistently:

1. In the tree view, it stringifies as the internal Symbol value (`Symbol(react.optimistic_key)`)
2. During component inspection, it returns `null` instead of showing any indication of the special key

This makes debugging components using optimistic updates confusing, as developers can't tell which components have optimistic keys vs. no keys at all.

## Files to Modify

- `packages/react-devtools-shared/src/backend/fiber/renderer.js`

## Expected Behavior

When `React.optimisticKey` is used as a component key:
- It should display as the readable string `"React.optimisticKey"` in both:
  - The DevTools tree component list
  - The component inspection panel

## Notes

- Look for how component keys are converted to strings and extracted for display
- The constant `REACT_OPTIMISTIC_KEY` already exists in the codebase and identifies this special symbol
- The display should match the public API name (`React.optimisticKey`) not the internal symbol description
