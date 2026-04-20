# Mantine: Add `selectFirstOptionOnDropdownOpen` Prop

## Context

The Mantine component library (packages/@mantine/core) provides several "Combobox-like" dropdown components: `Select`, `MultiSelect`, `Autocomplete`, and `TagsInput`. These components share common props defined in the `ComboboxLikeProps` interface in `packages/@mantine/core/src/components/Combobox/Combobox.types.ts`.

## Feature Request

Implement a new prop `selectFirstOptionOnDropdownOpen` on the `ComboboxLikeProps` interface and wire it up in all four ComboboxLike components (`Select`, `MultiSelect`, `Autocomplete`, `TagsInput`).

### Expected Behavior

- **Prop name**: `selectFirstOptionOnDropdownOpen`
- **Type**: `boolean` (optional, defaults to `false`)
- **Behavior when `true`**: When the dropdown opens, the first available (non-disabled) option in the list should be automatically selected. This is accomplished by calling `combobox.selectFirstOption()`.
- **Behavior when `false`** (default): Existing dropdown-open behavior is preserved. For `Select`, this means the currently active/highlighted option index is updated and scrolled into view.

### Components to Modify

1. `packages/@mantine/core/src/components/Combobox/Combobox.types.ts`
   - Add the new prop definition to the `ComboboxLikeProps` interface

2. `packages/@mantine/core/src/components/Select/Select.tsx`
   - Accept the new prop
   - When `selectFirstOptionOnDropdownOpen` is `true`, call `combobox.selectFirstOption()` on dropdown open
   - When `false`, preserve the existing `combobox.updateSelectedOptionIndex('active', { scrollIntoView: true })` behavior

3. `packages/@mantine/core/src/components/MultiSelect/MultiSelect.tsx`
   - Accept the new prop
   - When `true`, call `combobox.selectFirstOption()` on dropdown open

4. `packages/@mantine/core/src/components/Autocomplete/Autocomplete.tsx`
   - Accept the new prop
   - When `true`, call `combobox.selectFirstOption()` on dropdown open

5. `packages/@mantine/core/src/components/TagsInput/TagsInput.tsx`
   - Accept the new prop
   - When `true`, call `combobox.selectFirstOption()` on dropdown open

### JSDoc for the Prop

```typescript
/** If set, the first option is selected when dropdown opens, `false` by default */
selectFirstOptionOnDropdownOpen?: boolean;
```

### Testing

- All existing tests in `Select.test.tsx`, `MultiSelect.test.tsx`, `Autocomplete.test.tsx`, and `TagsInput.test.tsx` must continue to pass
- TypeScript compilation must succeed with no errors
