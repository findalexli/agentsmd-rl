# Fix Host Prop Removal Attribute Cleanup

The Remix component runtime has a bug in how host properties are removed from DOM
elements. When a property like `id` or `value` is present in a previous render
but absent in the next render, the `diffHostProps` function handles the removal.
However, the current logic leaves behind empty string attribute values on the DOM
element instead of fully removing the reflected attributes.

## Symptom

When rendering an element with attributes and then re-rendering without those
attributes, the DOM ends up with empty attribute strings rather than having the
attributes removed entirely:

- An `<input id="hello" value="world" />` re-rendered as `<input />` leaves
  `<input id="">` in the DOM instead of `<input>`
- The `value` property is reset to `''` (correct), but the `value` attribute
  remains on the element when it should be removed
- The same issue affects non-input elements like `<div id="hello"
  className="world">` — when re-rendered without those props, the `id` and
  `class` attributes persist as empty strings rather than being removed

The problem is in `packages/component/src/lib/diff-props.ts`. The current code
sets the DOM property to `''` for any property that supports property-based
access, then continues — skipping attribute removal entirely. For form control
properties like `value` and `checked`, resetting the runtime state is correct,
but the reflected attribute should still be removed afterward. For regular
properties like `id` and `className`, setting them to `''` creates an empty
attribute string instead of removing the attribute.

## What Needs to Change

The fix should ensure that:

1. When a property is removed from a host element's props, the corresponding
   reflected attribute is fully removed from the DOM (not left as an empty
   string)
2. Runtime form control state (`value`, `checked`, `selectedIndex`,
   `defaultValue`, `defaultChecked`, `selected`) is properly reset so that form
   controls return to their default state
3. Two previously-skipped test cases in
   `src/test/vdom.insert-remove.test.tsx` ("removes attributes") and
   `src/test/vdom.replacements.test.tsx` ("updates an element with attributes")
   are updated to pass with correct attribute assertions
4. A new test case is added in `src/test/vdom.insert-remove.test.tsx` to verify
   that removing reflected attributes from non-input elements (like `<div>`)
   also works correctly without leaving empty values

## Testing

The component package uses vitest with browser mode (Playwright/Chromium). Tests
are in `src/test/` and can be run with `npx vitest run`. Use
`root.flush()` after `root.render()` before making assertions about DOM state.

Run specific test files:
```bash
npx vitest run src/test/vdom.insert-remove.test.tsx
npx vitest run src/test/vdom.replacements.test.tsx
```

The full suite should also pass:
```bash
npx vitest run
```

## Code Style Requirements

This repo uses Prettier formatting (printWidth: 100, no semicolons, single
quotes, spaces not tabs). ESLint with max-warnings=0 is enforced. Use `let` for
local variables and `const` only at module scope. No loops or conditionals in
test suite `describe()` blocks.
