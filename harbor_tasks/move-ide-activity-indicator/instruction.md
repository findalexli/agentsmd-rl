# Add Activity Indicator to Move VSCode Extension

## Problem

The Move IDE (VSCode extension for the Move language) lacks visibility into the language server's current state. Users cannot tell:
- Whether the server is actively processing/compiling
- When operations are taking longer than expected (slow state)
- When a fatal error has occurred that stopped the server

## What You Need to Do

Implement an activity indicator in the VSCode status bar that:
1. Shows the server state: starting → idle ↔ busy → slow → stopped
2. Displays an animated indicator during active work (starting, busy, slow states)
3. Shows error/warning colors for stopped (red) and slow (yellow) states
4. Includes a tooltip with extension version, server version, and a restart command

The implementation requires changes in both:
- **Rust (server-side)**: `external-crates/move/crates/move-analyzer/src/`
- **TypeScript (client-side)**: `external-crates/move/crates/move-analyzer/editors/code/src/`

### Server-Side Requirements

The language server needs to send progress notifications to the client:
- Send `$/progress` notifications with token `"symbolication"` when compilation starts and ends
- Distinguish between non-fatal errors (missing manifest) and fatal errors (dependency failures)
- On fatal errors, the server should exit cleanly so the client detects the stopped state

### Client-Side Requirements

The VSCode extension needs to:
- Create a new `ServerActivityMonitor` class that manages the status bar item
- Wire it to language client state changes (starting, running, stopped)
- Listen for server-sent `$progress` notifications to track compilation state
- Wrap `sendRequest` to track individual LSP request latency as a secondary busy signal
- Implement a state machine: starting → idle ↔ busy → slow, and stopped (terminal)
- Prevent auto-restart on fatal errors (let user restart manually via tooltip)
- Create a persistent output channel that survives server restarts

## Files to Modify

**Server-side (Rust):**
- `external-crates/move/crates/move-analyzer/src/analyzer.rs` - Handle new message types and send progress notifications
- `external-crates/move/crates/move-analyzer/src/symbols/runner.rs` - Send start/end messages and distinguish error types

**Client-side (TypeScript):**
- Create `external-crates/move/crates/move-analyzer/editors/code/src/activity_monitor.ts` - New file with ServerActivityMonitor class
- `external-crates/move/crates/move-analyzer/editors/code/src/context.ts` - Initialize and wire activity monitor
- `external-crates/move/crates/move-analyzer/editors/code/src/main.ts` - Initialize activity monitor with version info

## Key Design Points

1. **State machine transitions**:
   - `starting`: Initial state when client connects
   - `idle`: When client is running with no active work
   - `busy`: When compilation in progress OR pending requests exist
   - `slow`: Promoted from starting/busy after ~10 seconds
   - `stopped`: Terminal state when server process dies

2. **Progress notification flow**:
   - Server sends `SymbolicationStart` → Client shows busy
   - Server sends `SymbolicationEnd` → Client can return to idle (if no pending requests)

3. **Request tracking**:
   - Each outgoing LSP request gets a tracking ID
   - Request sent → busy (if idle)
   - Response received → can return to idle (if no compilation and no other pending requests)

## Testing

Run tests to verify:
```bash
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v
```

Or manually verify by building:
```bash
cd /workspace/sui
cargo check -p move-analyzer
```

## References

- The CLAUDE.md file in the repo root contains development guidelines
- The server uses the `lsp-server` crate for LSP protocol handling
- The client uses `vscode-languageclient` for LSP client functionality
