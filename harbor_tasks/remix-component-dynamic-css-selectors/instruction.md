# Fix Dynamic CSS Selectors with Undefined Values

The CSS-in-JS style processing library in `@remix-run/component` throws a `TypeError` when a nested CSS selector or at-rule value is `undefined`. This prevents conditional styling patterns where developers want to optionally disable a selector rule.

## Symptom

Given a style object with a conditionally-enabled nested selector:

```tsx
css={{
  '&:hover': isPending ? undefined : { background: 'white' }
}}
```

The `processStyle` function throws:

```
TypeError: Cannot convert undefined or null to object
```

This occurs because the code calls `Object.entries(value)` on the nested selector value without first checking whether the value is a valid object. The same problem affects at-rules (`@media`, `@keyframes`, `@function`, etc.) when their values are `undefined`.

## Expected Behavior

- When a nested CSS selector's value is `undefined` or `null`, it should be silently skipped (omitted from the generated CSS output), not cause a crash.
- When an at-rule's value is `undefined` or `null`, it should be silently skipped.
- Only plain record objects should be treated as valid style values. Arrays and other non-plain-object values should be skipped rather than iterated over.
- Defined nested selectors and at-rules in the same style object should still produce their correct CSS output.

## Specific Cases to Handle

1. **Undefined nested selector**: `{ '& span': { color: 'blue' }, '& span.special': undefined }` — the `'& span.special'` rule should be absent from the generated CSS, while `'& span'` renders normally.

2. **Undefined at-rule**: `{ '@media (max-width: 600px)': undefined }` — the at-rule block should be absent from the CSS.

3. **Mixed defined/undefined**: A style object containing both defined and undefined nested selectors should produce CSS for only the defined ones.

4. **Array values**: Passing an array as a nested selector's value (e.g., `'& span': ['not', 'valid']`) should skip the rule rather than iterating the array as key-value pairs.

The fix must work within the `styleToCss` function (which is called by the exported `processStyle`) and the `atRuleBodyToCss` function, all located in the same file.

## Code Style Requirements

- The project uses Prettier with `printWidth: 100`, no semicolons, single quotes, and spaces (not tabs).
- Prefer `let` for local variables; `const` only at module scope.
- Use regular `function` declarations for new functions rather than arrow functions, unless the function is a callback.
- Only add comments when the code is doing something surprising or non-obvious.
- Test files must not use loops or conditional statements to generate test cases within `describe()` blocks.

## Verification

The test suite will call the `processStyle` function with various style objects containing `undefined` values for nested selectors and at-rules, then verify the generated CSS output is correct and complete.
