# Fix react-hook-form dirty state documentation

The design system documentation and cursor rules for Studio forms contain an incorrect pattern for handling `react-hook-form` dirty state.

The current documentation and code examples recommend accessing `form.formState.isDirty` directly. However, `react-hook-form` uses a Proxy-based approach for `formState` — accessing properties directly without destructuring does not properly subscribe to state updates, which means components won't re-render when the dirty state changes.

## What needs to change

1. **`apps/design-system/content/docs/ui-patterns/forms.mdx`** — The "Handle dirty state" best practice (item #5) should be updated to mention that `isDirty` must be destructured from `form.formState` for proper reactivity.

2. **`apps/design-system/content/docs/ui-patterns/modality.mdx`** — The Studio implementation code example for dirty form dismissal uses `form.formState.isDirty` directly in the `checkIsDirty` callback. This should be updated to destructure `isDirty` from `form.formState` first, then pass the destructured value. Add a comment explaining why this matters.

3. After fixing the documentation, update the relevant cursor rule to reflect this best practice so that future AI-assisted code generation follows the correct pattern.

See the react-hook-form docs on formState for details on why this matters.
