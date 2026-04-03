# Add Root Folder Rendering to Changes View Tree

The VS Code Changes View (`src/vs/sessions/contrib/changes/browser/changesView.ts`) displays file changes in a tree view, but it has two issues:

1. **No root folder node**: The tree shows files without a root folder context, making it hard to understand which workspace folder the changes belong to.
2. **No support for non-git workspaces**: When a workspace has no git repository, the Changes View cannot display any files because it relies entirely on git diff for file discovery.

The fix should:
- Add a `IChangesRootItem` type with `type: 'root'` to represent root folder nodes
- Add a `'none'` change type for files that exist but have no git changes
- Create a `buildTreeChildren` that accepts optional root info to wrap the tree
- Add `collectWorkspaceFiles` to enumerate files via `IFileService` when there's no git repo
- Add a `renderRootElement` method for rendering root folder nodes
- Handle the non-git path in the view model observables
