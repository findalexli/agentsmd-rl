# Scope Editor Service in Window Title to Own Editor Groups

The `BrowserTitlebarPart` in `src/vs/workbench/browser/parts/titlebar/titlebarPart.ts` injects `IEditorService` directly, which provides access to ALL editors across all windows (main window and auxiliary windows). This causes the main window's title bar to incorrectly reflect editors that have been moved to auxiliary windows.

For example, if you move an editor to a secondary window, the main window's title still updates based on that editor's state because `editorService.activeEditor` returns the globally active editor.

The fix should scope the editor service to the titlebar part's own `editorGroupsContainer` by:
1. Calling `editorService.createScoped(editorGroupsContainer)` to create a scoped service
2. Creating a child `IInstantiationService` with the scoped editor service via `ServiceCollection`
3. Using the scoped instantiation service for creating `WindowTitle` and other child components
4. Replacing `this.editorService.activeEditor` with `this.editorGroupsContainer.activeGroup.activeEditor`
