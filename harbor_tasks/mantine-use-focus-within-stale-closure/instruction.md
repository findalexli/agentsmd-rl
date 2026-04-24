# Fix Stale Closure in useFocusWithin Hook

The `useFocusWithin` hook in `@mantine/hooks` has a **stale closure bug** that prevents `onFocus` and `onBlur` callbacks from accessing the latest state values.

## The Problem

When using `useFocusWithin` with callbacks that reference component state:

```tsx
const [count, setCount] = useState(0);
const { ref } = useFocusWithin({
  onFocus: () => setCount(count + 1),  // Captures stale `count`
  onBlur: () => setCount(count - 1),   // Captures stale `count`
});
```

Each time the component re-renders, new callback functions are created with access to the current `count`. However, the hook's internal `useCallback` memoization captures the original callbacks, so the stale closure always sees `count = 0`.

## Symptoms

- State updates in `onFocus`/`onBlur` callbacks don't reflect the current state
- Multiple focus/blur cycles don't properly increment/decrement counters
- Callbacks fire but use outdated values from closure

## Where to Look

The hook is located at:
`packages/@mantine/hooks/src/use-focus-within/use-focus-within.ts`

The `utils` directory in the same package contains helper hooks that can be used to solve this type of stale closure problem.

## Expected Behavior

After the fix:

1. `onFocus` and `onBlur` callbacks should always invoke the latest version of the callback passed by the user
2. The `handleFocusIn` and `handleFocusOut` event handlers inside the hook should have empty dependency arrays to prevent unnecessary re-creation
3. The solution should use a ref-based pattern that allows accessing the current callback without breaking memoization
4. TypeScript should compile without errors
5. All Jest tests for this hook should pass

## Testing

The repo has a test file that validates the fix. Run Jest tests for this specific hook:

```bash
yarn jest use-focus-within --testPathPattern=use-focus-within
```

The test file demonstrates the expected behavior with multiple focus/blur cycles that should properly increment counters.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
- `stylelint (CSS linter)`
