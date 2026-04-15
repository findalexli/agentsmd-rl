# Support numeric file descriptors in child_process stdio array

## Problem

When using Node.js `child_process` APIs in Deno, passing a numeric file descriptor (e.g., from `fs.openSync()`) in the `stdio` array does not work correctly. The runtime interprets numeric values as internal resource IDs, but `fs.openSync` returns real OS file descriptors that should be passed through directly.

For example, this pattern should work:

```ts
import { spawn } from "node:child_process";
import * as fs from "node:fs";

const fd = fs.openSync("/tmp/output.txt", "w");
const child = spawn("/bin/sh", ["-c", "echo hello >&3"], {
  stdio: ["ignore", "pipe", "pipe", fd],
});
```

The child process should be able to write to the file descriptor provided by the caller. Additionally, when a child process inherits stdout/stderr, it should receive the runtime's redirected output handles (which may differ from the original OS handles during `deno test`), not hardcoded OS-level fd 1/2.

## Expected Behavior

1. **Numeric fd passthrough**: Numeric values in the `stdio` array should be passed through to the child process as-is (duplicated for the child). The implementation must use a signed integer type for deserialization, and error messages should reference "file descriptor", not "resource id".

2. **Inherit mode with redirected output**: When `stdio: "inherit"` is used, the child process should inherit the runtime's actual stdout/stderr handles, which may have been redirected (e.g., during `deno test` for output capture). This requires the runtime to capture its own stdout/stderr handles during initialization and provide them when spawning children.

## What to Look At

The following areas may need changes to support this feature:

- `ext/process/lib.rs` — Handles stdio configuration for child processes. The deserialization logic for numeric values needs to handle OS file descriptors. The inherit mode needs to use handles captured at runtime, not hardcoded values.
- `ext/io/lib.rs` — IO extension initialization. The runtime's stdout/stderr handles need to be captured so child processes can inherit redirected output.
- `ext/node/polyfills/internal/child_process.ts` — Node.js child_process polyfill. The comment explaining numeric stdio values may need updating.
- `tests/unit_node/child_process_test.ts` — A test exercising numeric fd in the stdio array should be present (or added).

## Constraints

- String variants (`inherit`, `piped`, `null`, `ipc_for_internal_use`) must continue to work.
- The `ChildStdio` struct fields (`stdin`, `stdout`, `stderr`) must still be typed with a stdio option type.
- All existing unit tests (`deno_io --lib`, `deno_process --lib`) must pass.
- `cargo check` and `cargo clippy` must pass with no warnings.
- `cargo fmt` must pass.