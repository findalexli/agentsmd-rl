# File watcher CPU usage issue in large workspaces

## Issue Summary

Users report that VS Code's file watcher process consumes excessive CPU resources when working with large repositories. This appears to be related to how the default `files.watcherExclude` patterns are configured.

## Symptoms

- File watcher process spins at high CPU usage in large workspaces
- Issue is particularly noticeable in repositories with deep directory structures or large numbers of files
- The problem relates to pattern matching performance

## Code Location

The file watcher exclusion patterns are defined in the workbench configuration system:

- `src/vs/workbench/contrib/files/browser/files.contribution.ts` — Contains the default `watcherExclude` configuration
- `src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts` — May have related session configuration

## Investigation Notes

The glob patterns used for exclusions may be causing pathological regex behavior when the file watcher tries to match against large directory structures. Consider:

1. How glob patterns with `**` prefixes translate to regular expressions
2. Whether there are duplicate configurations between the workbench and sessions
3. Alternative pattern formulations that achieve the same exclusion behavior with better performance

## Expected Outcome

The file watcher should exclude the same directories (`.git/objects`, `.git/subtree-cache`, `.hg/store`) but without causing CPU stalls in large workspaces.

## References

- Related issue: #305923
