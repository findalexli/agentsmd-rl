# Fix Read-Only Fields During Document Paste

## Problem

When pasting a document in Sanity Studio, fields marked as `readOnly` in the target schema are silently overwritten with values from the source document. This affects both:

1. **Static read-only fields**: `{ readOnly: true }`
2. **Conditional read-only fields**: `{ readOnly: ({ currentUser }) => !isAdmin(currentUser) }`

The expected behavior is that read-only fields should preserve their existing target values during a paste operation, and users should be warned about which fields were skipped.

## Files to Modify

1. **`packages/sanity/src/core/studio/copyPaste/transferValue.ts`** — Core paste logic
2. **`packages/sanity/src/core/i18n/bundles/copy-paste.ts`** — Internationalization strings

## What to Implement

When `transferValue()` pastes at the **document level** (i.e., when the target root path is empty), it must:

1. **Detect document-level paste** — Identify when `targetRootPath` has length 0
2. **Skip static read-only fields** — Fields with `readOnly: true` should not be overwritten
3. **Evaluate conditional read-only fields** — Fields with `readOnly` as a function must be evaluated with the current user, document, parent, and value context
4. **Preserve target values** — For any skipped field, keep the existing target document's value
5. **Generate a warning** — After processing, if any read-only fields were skipped, push a warning to the errors array containing:
   - A `level` of `'warning'`
   - An `i18n` key chosen based on the count of skipped fields:
     - If 3 or fewer: use the key `'copy-paste.on-paste.validation.read-only-fields-skipped.description'` with argument `{{fieldNames}}`
     - If more than 3: use the key `'copy-paste.on-paste.validation.read-only-fields-skipped-truncated.description'` with arguments `{{fieldNames}}` and `{{count}}`
6. **Add i18n strings** — Define both warning message templates in the copy-paste locale bundle

## i18n String Requirements

Add these two message templates to the copy-paste locale bundle:

- **`'copy-paste.on-paste.validation.read-only-fields-skipped.description'`** — Must accept a `{{fieldNames}}` argument
- **`'copy-paste.on-paste.validation.read-only-fields-skipped-truncated.description'`** — Must accept `{{fieldNames}}` and `{{count}}` arguments

## Verification

After implementing:
- `pnpm vitest run --project=sanity packages/sanity/src/core/studio/copyPaste/__test__/transferValue.test.ts` should pass
- `pnpm turbo run check:types --filter=sanity` should pass
- `pnpm check:oxlint` should pass