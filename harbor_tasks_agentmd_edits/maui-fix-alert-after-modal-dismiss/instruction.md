# Fix alert dialogs not displaying after dismissing modal page on iOS

## Problem

On iOS and macOS, `DisplayAlert` calls silently fail when invoked immediately after dismissing a modal page (including WebAuthenticator modals). Users had to add artificial delays of 750ms+ as a workaround to get alerts to appear.

## Expected Behavior

Alerts should display immediately after a modal page is dismissed, without any delay.

## Files to Look At

- `src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs` — the `GetTopUIViewController` method traverses the view controller presentation chain to find the topmost view controller. During modal dismissal, `PresentedViewController` remains non-null until the dismissal animation completes, causing the method to return a view controller that iOS considers invalid for presenting new content.

## Additional Requirements

This task also involves cleaning up the repository's agent instruction files:

- The `.github/copilot-instructions.md` file contains an outdated "Opening PRs" section that mandates a specific NOTE block in PR descriptions. This section should be removed.
- The `.github/skills/pr-finalize/SKILL.md` file references the same NOTE block requirement in its description requirements and structured template. These references should be removed.
- The `.github/skills/pr-finalize/references/complete-example.md` file includes the NOTE block in its example. It should be removed from there as well.

After fixing the code, update the relevant documentation files to reflect the removal of the NOTE block requirement.
