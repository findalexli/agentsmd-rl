# Fix CollectionView selection crash with HeaderTemplate on Android

## Problem

When an Android `CollectionView` has a `HeaderTemplate` (or `FooterTemplate`) and `SelectionMode` is set to `Single` or `Multiple`, tapping any item throws an `ArgumentOutOfRangeException`. The crash originates from `SelectableItemsViewAdapter.OnBindViewHolder` — header and footer `ViewHolder`s are being added to the selection-tracking list, and when `MarkPlatformSelection` later iterates them, it calls `GetItem()` on a header position. The internal `AdjustIndexForHeader` method returns `-1` for header positions, which causes `ElementAt(-1)` to blow up.

## Expected Behavior

Tapping items in a `CollectionView` that has headers/footers and selection enabled should work without crashing. Header and footer view holders should be excluded from the selection-tracking system entirely.

## Files to Look At

- `src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs` — the `OnBindViewHolder` method subscribes the click handler and tracks view holders for selection. Header/footer positions need to be filtered out before any selection logic runs.

## Additional Context

While investigating this area of the codebase, the team also discovered a recurring issue with `PublicAPI.Unshipped.txt` files: the `#nullable enable` directive on line 1 can get displaced when files are sorted during merge conflict resolution (BOM bytes sort incorrectly under `LC_ALL=C`). The project's agent instructions in `.github/copilot-instructions.md` should be updated in the "PublicAPI.Unshipped.txt File Management" section to document this critical requirement and provide a safe merge-conflict resolution script, so that AI agents and contributors don't accidentally break the analyzer by sorting these files.
