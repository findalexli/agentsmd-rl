# [PR-Agent] Fix ApplyQueryAttributes called with empty dictionary on back

## Problem

According to Microsoft's documentation, calling `query.Clear()` in `ApplyQueryAttributes` should prevent the method from being called again when re-navigating to the existing page (e.g., with `GoToAsync("..")`).

**Current (broken) behavior:** `ApplyQueryAttributes` IS called with an empty dictionary when navigating back, even after calling `query.Clear()`.

**Expected behavior:** `ApplyQueryAttributes` should NOT be called with empty dictionary after `query.Clear()` has been called.

## Files to Look At

- `src/Controls/src/Core/Shell/ShellNavigationManager.cs` — Core navigation logic that invokes `ApplyQueryAttributes`
- `.github/copilot-instructions.md` — Agent configuration with PublicAPI file handling rules

## Implementation Notes

The fix involves adding a guard in two code paths within `ApplyQueryAttributes` method:

1. **Path 1 (ShellContent)**: Skip calling `ApplyQueryAttributes` if `mergedData.Count == 0 && isPopping == true`
2. **Path 2 (isLastItem)**: Skip setting `QueryAttributesProperty` if `mergedData.Count == 0 && isPopping == true`

The condition should be:
```csharp
if (mergedData.Count > 0 || !isPopping)
{
    // Only call/set if data exists OR not popping
}
```

This respects when user calls `query.Clear()` - they don't want attributes applied on back navigation.
