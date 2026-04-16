# Fix Read-Only Fields During Document Paste

## Problem

When pasting a document in Sanity Studio, fields marked as `readOnly` in the target schema are silently overwritten with values from the source document. This affects both:

1. **Static read-only fields**: `{ readOnly: true }`
2. **Conditional read-only fields**: `{ readOnly: ({ currentUser }) => !isAdmin(currentUser) }`

The expected behavior is that read-only fields should preserve their existing target values during a paste operation, and users should be warned about which fields were skipped.

## Where to Look

The core logic for copy-paste value transfer is in:

**`packages/sanity/src/core/studio/copyPaste/transferValue.ts`**

Key function: `transferValue()` and the internal `collateObjectValue()` helper.

The i18n warning strings for paste operations are in:

**`packages/sanity/src/core/i18n/bundles/copy-paste.ts`**

## Related Issue

- Issue #7408: "read-only fields on the target document were silently overwritten"

## Test File Reference

The test file `packages/sanity/src/core/studio/copyPaste/__test__/transferValue.test.ts` contains existing tests for read-only field handling. Look for patterns like:

- `pasteDocumentLevel` helper function
- Tests involving `readOnly` schema properties
- Warning/error expectations with `i18n` keys

## What to Implement

1. Detect when pasting at document level (when `targetRootPath` is empty)
2. Check each field's `readOnly` property before copying its value
3. For conditional `readOnly` (functions), evaluate them with the correct context (currentUser, document, parent, value)
4. Skip copying read-only fields and preserve existing target values instead
5. Generate warning messages listing the skipped fields
6. Add appropriate i18n strings for the warning messages

## Agent Guidelines

Refer to `AGENTS.md` in the repo root for:
- Use **pnpm** (not npm) for package management
- Run `pnpm build` before testing
- Run `pnpm lint:fix` before committing
- Use `pnpm vitest run --project=sanity <path>` for single test files
- Follow conventional commit format for PR titles: `type(scope): lowercase description`
