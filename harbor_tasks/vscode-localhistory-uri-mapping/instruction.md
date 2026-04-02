# Local History Commands Fail When Triggered from Diff Editor

## Bug Description

Local history commands such as "Compare with File", "Compare with Previous", and "Select for Compare" silently fail (have no effect) when triggered from a diff editor that is already showing two local history versions of a file.

## Context

The VS Code local history feature maintains a history of file changes. Users can:
- Open the timeline view for a file to see its history entries
- Compare different versions of the file
- Select a version and trigger commands like "Compare with Previous" or "Compare with File"

The issue occurs when these commands are triggered from within a diff editor that was opened to compare two local history entries. In this context, the resource URI has a special scheme (`vscode-local-history`), which causes the history lookup to fail silently.

## Expected Behavior

Local history commands should work regardless of which editor they are triggered from. The commands should correctly resolve the original file from the local history URI and find its history entries.

## Files to Investigate

- `src/vs/workbench/contrib/localHistory/browser/localHistoryCommands.ts` - contains the `findLocalHistoryEntry` function that looks up history entries
- `src/vs/workbench/contrib/localHistory/browser/localHistoryFileSystemProvider.ts` - provides the URI mapping utilities

Look at how `provideTimeline` handles this scenario and apply the same pattern to ensure `findLocalHistoryEntry` correctly maps URIs before querying the history service.

## Requirements

1. Fix the `findLocalHistoryEntry` function to handle `vscode-local-history` scheme URIs
2. Map the special scheme back to the original file URI before querying the history service
3. Follow existing code patterns in the local history module
4. Ensure TypeScript compilation passes after the fix
