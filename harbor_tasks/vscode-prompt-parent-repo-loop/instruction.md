# Fix Infinite Loop in findParentRepoFolders

The `findParentRepoFolders` method in `src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts` can enter an infinite loop when walking up the directory tree to find parent git repositories.

The current implementation uses a `do...while` loop that computes `parent = dirname(current)` at the top of the loop but checks `seen.has(current)` and `current.path !== '/'` at the bottom. This structure has a bug: when `dirname()` returns the same path (fixed-point at filesystem root, e.g., `dirname('/') === '/'`), the loop variable `parent` is set but `current` is only updated after the condition check, causing the loop to spin forever on the root directory.

The fix should restructure the loop as `while(true)` with explicit break conditions that check:
- `dirname(current) === current` (filesystem root fixed-point)
- `current.path === '/'` (Unix root)
- User home directory boundary
- Already-seen folders
