# Fix hot reload race condition with vim's atomic save on macOS

## Problem

When using `bun --hot` on macOS with vim as the editor, editing the entrypoint file triggers a "Module not found" error instead of a successful hot reload. This happens because vim performs an atomic save: it renames the original file (e.g., `a.js` → `a.js~`), then creates a new file with the same name. On macOS, kqueue watches file descriptors (inodes), not paths — so when the file is renamed, the watcher immediately tries to reload, but the new file hasn't been created yet, resulting in an `ENOENT` error.

This is macOS-specific because Linux's inotify watches paths and handles the rename sequence differently.

## Expected Behavior

When vim saves the entrypoint file on macOS:
1. The hot reloader should recognize that a rename event on the entrypoint is likely part of an atomic save
2. It should defer the reload until the parent directory receives a write event confirming the file has been recreated
3. It should verify the file exists before triggering the reload
4. The reload should succeed without errors

## Files to Look At

- `src/bun.js/hot_reloader.zig` — Main hot reload event loop that processes file/directory change events
- `src/Watcher.zig` — Low-level file watcher that manages kqueue on macOS and inotify on Linux
- `src/bun.js/VirtualMachine.zig` — VM integration for hot reload, manages promise rejection and module reloading
- `src/bun.js.zig` — Entry point runner that initializes hot module reloading
- `src/fs.zig` — Filesystem path utilities used by the watcher
- `src/sys.zig` — System call wrappers including `faccessat` for file existence checks
- `src/bundler/bundle_v2.zig` — Bundler integration with the watcher
- `src/cli/test_command.zig` — Test runner integration with the watcher

## Hints

- The hot reloader needs to track the entrypoint file separately from dependencies, since dependencies have natural buffering from import graph traversal
- You'll need to propagate the entrypoint path through to the hot reloader initialization
- The fix involves deferring reload on rename events and waiting for a parent directory write event to confirm the file exists
- Consider adding a way for the VM to lazily register the entrypoint with the watcher after initial module evaluation
- A new `PathName.findExtname` utility may be needed to correctly extract extensions from changed file names in directory events

After fixing the code, update the project's Zig coding conventions in `src/CLAUDE.md` to reflect current best practices around `@import` usage.
