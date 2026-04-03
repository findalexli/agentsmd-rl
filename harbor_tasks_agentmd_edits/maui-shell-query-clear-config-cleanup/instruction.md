# Fix ApplyQueryAttributes called with empty dictionary on back navigation

## Problem

In .NET MAUI's Shell navigation, when a page implements `IQueryAttributable` and calls `query.Clear()` inside `ApplyQueryAttributes`, the method is still called again with an empty dictionary when the user navigates back (e.g., via `GoToAsync("..")`).

According to the documentation, calling `query.Clear()` should prevent `ApplyQueryAttributes` from being re-invoked on back navigation. Instead, the method fires a second time with an empty `IDictionary<string, object>`.

This happens because `ApplyQueryAttributes` in `ShellNavigationManager.cs` has two code paths that unconditionally apply/set query attributes during pop (back) navigation — even when the merged query data is empty.

## Expected Behavior

When `query.Clear()` is called in `ApplyQueryAttributes`, the method should NOT be invoked again with an empty dictionary when navigating back. The method should only be called if there is actual data to apply.

Both code paths in `ApplyQueryAttributes` (the `ShellContent` branch and the `isLastItem` branch) need to be guarded so they skip applying attributes when the merged data is empty during a pop navigation.

## Files to Look At

- `src/Controls/src/Core/Shell/ShellNavigationManager.cs` — Contains the `ApplyQueryAttributes` static method with two code paths that need guards

## Additional Context

The repo's agent configuration files (`.github/copilot-instructions.md` and `.github/skills/pr-finalize/SKILL.md`) currently contain an outdated requirement that all PRs must start with a specific `[!NOTE]` block about testing PR artifacts. This requirement is no longer needed and should be removed from the instructions and related skill files. After fixing the code, update the relevant agent configuration and skill documentation to remove this outdated PR description requirement.
