# Bug Report: Titlebar creates unnecessary scoped editor service causing stale editor state

## Problem

In VS Code's titlebar implementation, the `BrowserTitlebarPart` creates a child instantiation service with a scoped `IEditorService` during construction. This scoped editor service is unnecessarily complex — it wraps the editor service in a way that introduces indirection without benefit. More critically, the toolbar update logic that checks whether to refresh editor actions uses `this.editorGroupsContainer.activeGroup.activeEditor` instead of querying the editor service directly, which can return stale or incorrect results in certain multi-group configurations.

## Expected Behavior

The titlebar should use the standard injected editor service directly and check active editor state through the canonical `IEditorService` API. Editor toolbar actions in the titlebar should reliably reflect the current active editor state.

## Actual Behavior

The titlebar constructs a child instantiation service with a scoped editor service override, adding unnecessary complexity. The editor toolbar context update checks active editor state through the editor groups container rather than the editor service, which can lead to incorrect toolbar state when editor groups are in certain configurations.

## Files to Look At

- `src/vs/workbench/browser/parts/titlebar/titlebarPart.ts`
