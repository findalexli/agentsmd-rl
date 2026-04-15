# Fix CollectionView Selection Crash with HeaderTemplate on Android

## Problem

When a `CollectionView` has a `HeaderTemplate` (or `FooterTemplate`) and `SelectionMode` is set to `Single` or `Multiple`, clicking an item throws an `ArgumentOutOfRangeException`.

The crash occurs because header and footer ViewHolders are incorrectly included in the selection-tracking system. When selection attempts to call `GetItem()` on a header or footer position, it internally uses index adjustment that returns an invalid index, causing `ElementAt` or equivalent to fail.

## Expected Behavior

- Items in a CollectionView with `HeaderTemplate`/`FooterTemplate` should be selectable without crashing
- Header and footer ViewHolders must not participate in selection tracking
- Calling `GetItem()` on header/footer positions must not throw `ArgumentOutOfRangeException`

## Files to Modify

- `src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs` — add a guard that skips header and footer ViewHolders before they enter the selection-tracking system; include a comment explaining why the guard is needed (mentioning that header/footer holders should not participate in selection, and that accessing them causes ArgumentOutOfRangeException)
- `.github/copilot-instructions.md` — add a "Code Review Instructions" section referencing `dotnet format`, and add a rule stating that `#nullable enable` must be on line 1 of `PublicAPI.Unshipped.txt` files (with mention of RS0017); include a safe bash pattern for handling these files that uses `git diff --name-only --diff-filter=U`, `head -1`, `LC_ALL=C sort`, and loops over `$(git diff ...)`

## References

- Issue: #34247
