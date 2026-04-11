# Fix CollectionView Selection Crash with HeaderTemplate on Android

## Problem

When a `CollectionView` has a `HeaderTemplate` (or `FooterTemplate`) and `SelectionMode` is set to `Single` or `Multiple`, clicking an item throws an `ArgumentOutOfRangeException`.

The crash occurs because `SelectableItemsViewAdapter.OnBindViewHolder` was incorrectly adding header and footer `ViewHolder`s to the selection-tracking list. When `MarkPlatformSelection` later iterated those holders, it called `GetItem()` on header positions — which internally calls `AdjustIndexForHeader(0)` returning `-1` — causing `ElementAt(-1)` to crash.

## Expected Behavior

- Items in a CollectionView with `HeaderTemplate`/`FooterTemplate` should be selectable without crashing
- Header and footer positions should be excluded from selection tracking entirely

## Files to Modify

- `src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs` — Add early-return guard to skip header/footer ViewHolders before they enter the selection tracking system

## Config File to Update

- `.github/copilot-instructions.md` — Add critical rule about `#nullable enable` needing to be on line 1 of PublicAPI.Unshipped.txt files

## References

- Issue: #34247
- The fix requires adding a null-safety guard that checks if the position is a header or footer before processing selection
