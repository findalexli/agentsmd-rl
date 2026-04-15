# Add Activity Indicator to Move VSCode Extension

## Problem

The Move IDE (VSCode extension for the Move language) lacks visibility into the language server's current state. Users cannot tell:
- Whether the server is actively processing/compiling
- When operations are taking longer than expected
- When a fatal error has occurred that stopped the server

## What You Need to Do

Implement an activity indicator in the VSCode status bar that:
1. Shows the server state: starting, idle, busy, slow, or stopped
2. Displays an animated indicator during active work (starting, busy, slow states)
3. Shows error/warning colors for stopped (red) and slow (yellow) states
4. Includes a tooltip with extension version, server version, and a restart command

### Server-Side Requirements (Rust)

The language server needs to send progress notifications to the client so the extension can track compilation state. These notifications use LSP's `$/progress` mechanism with a specific token string.

The server must:
- Send progress begin notification when compilation starts
- Send progress end notification when compilation finishes
- Distinguish between non-fatal errors (missing manifest) and fatal errors (dependency failures)
- Exit cleanly on fatal errors so the client detects the stopped state

### Client-Side Requirements (TypeScript)

The VSCode extension needs a status bar indicator that tracks server health. This requires:

- A status bar item aligned to the left
- State-based coloring: red background when stopped, yellow when slow
- A state machine with these states: `starting`, `idle`, `busy`, `slow`, `stopped`
- Methods to handle: client state changes, compilation start/end events, request tracking, and rendering
- Wrapped request sending to track individual LSP request latency
- An error handler configured to prevent automatic restart on fatal errors
- A persistent output channel that survives server restarts

## Expected Behavior

### State Machine

The indicator follows this state model:
- **starting**: Initial state when client connects
- **idle**: Server running with no active work
- **busy**: Compilation in progress OR pending requests exist
- **slow**: Promoted from starting/busy when operations exceed ~10 seconds
- **stopped**: Terminal state when server process dies

### Progress Notification Flow

The server sends LSP `$/progress` notifications:
- Server sends progress `begin` → client shows busy
- Server sends progress `end` → client can return to idle (if no pending requests)

### Request Tracking

Each outgoing LSP request is tracked by ID:
- Request sent → busy (if idle)
- Response received → can return to idle (if no compilation in progress and no other pending requests)

### Error Handling

Fatal errors cause the server process to exit. The client detects this as the `Stopped` state and displays the red error indicator. The user can restart manually via the tooltip command.

## References

- The CLAUDE.md file in the repo root contains development guidelines
- The server uses the `lsp-server` crate for LSP protocol handling
- The client uses `vscode-languageclient` for LSP client functionality
