# Fix Alert Dialogs Not Displaying After Modal Dismissal on iOS

## Problem

On iOS and macOS, calling `DisplayAlert` immediately after dismissing a modal page (including WebAuthenticator modals) silently fails. The alert never appears. Users have been working around this by adding a 750ms+ delay after modal dismissal, but that's fragile and unreliable.

The root cause is in the `GetTopUIViewController` method in `AlertManager.iOS.cs`. This method traverses the view controller presentation chain to find the topmost view controller for presenting alerts. However, during modal dismissal, `PresentedViewController` remains non-null until the dismissal animation completes. The method returns a view controller that is in the process of being dismissed, and iOS silently ignores presentation requests from dismissing view controllers.

## Expected Behavior

Alert dialogs should display immediately after a modal page is dismissed, without requiring any artificial delay. The view controller traversal logic should detect when a presented controller is being dismissed and stop at the presenting controller instead.

## Files to Look At

- `src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs` — contains `GetTopUIViewController`, the method that finds the topmost view controller for presenting alerts

## Additional Cleanup

The repository's agent configuration files (`.github/copilot-instructions.md` and `.github/skills/pr-finalize/`) currently instruct agents to include a NOTE block at the top of every PR description asking users to test PR build artifacts. This requirement has been deprecated — the NOTE block is no longer needed. Remove all references to this NOTE block requirement from the copilot instructions and the pr-finalize skill files (including its example references).
