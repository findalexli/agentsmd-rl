# Move IDE Activity Indicator Task

This task implements an activity indicator for the Move VSCode extension, similar to what rust-analyzer provides. The indicator shows the language server's current state in the VSCode status bar.

## Task Overview

The activity monitor displays server health with visual feedback:
- **starting**: Initial connection state (animated)
- **idle**: Server ready with no active work
- **busy**: Compilation or requests in progress (animated)
- **slow**: Operation taking longer than expected (yellow warning)
- **stopped**: Server process died (red error)

## Changes Required

### Server-Side (Rust)
- `move-analyzer/src/symbols/runner.rs`: Add `SymbolicatorMessage` enum with variants for:
  - `Diagnostics` - compilation results
  - `Error` - non-fatal errors (missing manifest)
  - `FatalError` - fatal errors (dependency failures)
  - `SymbolicationStart` - compilation started
  - `SymbolicationEnd` - compilation finished

- `move-analyzer/src/analyzer.rs`: Handle new message types and send `$progress` notifications

### Client-Side (TypeScript)
- `editors/code/src/activity_monitor.ts`: New `ServerActivityMonitor` class
- `editors/code/src/context.ts`: Wire activity monitor to language client
- `editors/code/src/main.ts`: Initialize with version info

## State Machine

```
starting ──► idle ◄──► busy ──► slow
               ▲                  │
               └──────────────────┘
stopped (terminal)
```

## Key Features

1. **Dual signal detection**: Monitors both `$progress` notifications and individual request latency
2. **Persistent output channel**: Survives server restarts for better UX
3. **No auto-restart**: Fatal errors require manual restart via tooltip
4. **Version info**: Tooltip shows both extension and server versions

## Verification

Tests verify:
- Rust code compiles with new types
- SymbolicatorMessage enum has all variants
- Channel sender type updated
- PROGRESS_TOKEN constants defined
- Progress notifications sent/received
- Fatal error handling with process exit
- Activity monitor state machine methods
- TypeScript request wrapping
- Error handler configuration
