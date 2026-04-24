# Bug: Localized Field Data Lost When Bulk-Trashing Draft Documents

## Symptom

When using the trash feature on collections with `versions.drafts` enabled, **localized field data is silently lost** for draft-only documents (documents that have never been published).

This is most visible with localized fields, but affects any field data that exists only in the versions table.

## Reproduction Steps

1. Create a collection with `trash: true` and `versions: { drafts: true }`
2. Add a localized text field (e.g., `localizedField` with `localized: true`)
3. Create a draft document
4. Update the localized field values for multiple locales (e.g., `en` and `es`) while keeping the document as a draft
5. Use the list view to bulk-trash the document
6. Open the trashed document and check the localized field values

**Expected**: Localized field values should be preserved for all locales
**Actual**: Localized field values are empty or show stale published data

## Root Cause

When saving drafts, Payload skips `updateOne` on the main collection table (since the document isn't published yet). The main table only reflects the **last published state**.

Single-document trash operations use `getLatestCollectionVersion()`, which correctly reads from the versions table. However, **bulk trash operations read from the main collection table**, getting stale/empty data.

This explains why draft-only localized field values are lost: the bulk trash operation reads from the main collection table, which doesn't have draft-only localized field values - those values are only in the versions table.

## Affected Code

The bulk trash operation is in `packages/payload/src/collections/operations/update.ts`. The code determines which table to read from (main collection table vs versions table) based on a condition. For draft-only documents with localized fields, the current logic may read from the wrong table, causing data loss during bulk trash.

## Test Collection Setup

The test collection at `test/trash/collections/Posts/index.ts` must include a field named `localizedField` of type `text` with `localized: true` to reproduce the bug.

The test config at `test/trash/config.ts` must have localization enabled with a `localization:` block containing a `locales:` array (e.g., `['en', 'es']` with `defaultLocale: 'en'`).

## References

- Related issue: #15980

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
