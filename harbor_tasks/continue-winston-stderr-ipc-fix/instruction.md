# Fix Winston Logger IPC Stream Corruption and Binary Tests

## Problem

The binary mode of Continue is experiencing two related issues:

1. **IPC Stream Corruption**: Winston's Console transport writes directly to `process.stdout`, which corrupts the `\r\n`-delimited JSON IPC stream between the binary and the JetBrains plugin. This causes communication failures between the IDE and the core.

2. **Broken Binary Tests**: The existing binary tests are failing because:
   - `ReverseMessageIde` is no longer working correctly with the current protocol
   - Test expectations are stale (e.g., `models` → `modelsByRole`)
   - Binary responses are wrapped in `{ done, content, status }` but tests expect unwrapped data

## Files to Modify

- `core/util/Logger.ts` - Fix Winston to use stderr instead of stdout
- `binary/test/binary.test.ts` - Fix the test infrastructure

## Requirements

### Logger Fix

Modify the Winston Console transport configuration in `core/util/Logger.ts` to redirect all log levels (error, warn, info, debug) to stderr instead of stdout. This prevents log output from corrupting the IPC stream.

### Binary Test Fixes

1. **Add BinaryIdeHandler class**: Create a handler that responds to IDE messages from the binary subprocess with plain data matching the Kotlin `CoreMessenger` format `{ messageType, data, messageId }`. This bypasses the JS `_handleLine` auto-wrapper that would double-wrap responses.

2. **Add request() helper**: Create a helper function that unwraps binary responses from `{ done, content, status }` to get the actual content, matching how the Kotlin CoreMessenger reads responses.

3. **Update test assertions**: Fix stale expectations:
   - Change `models` to `modelsByRole`
   - Update expected files list to only include files that are actually created

4. **Add stderr handler**: Add logging for subprocess stderr output to aid debugging.

5. **Instantiate BinaryIdeHandler**: Create the handler in the `beforeAll` hook when using subprocess mode.

## Testing

The following must be verified:
- Winston Console transport uses `stderrLevels` for all log levels
- `BinaryIdeHandler` class exists with proper handler methods
- `request()` helper unwraps responses correctly
- All tests use the `request()` helper
- TypeScript compiles without errors for both `core` and `binary` packages
