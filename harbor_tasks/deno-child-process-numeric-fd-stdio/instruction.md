# Support numeric file descriptors in child_process stdio array

## Problem

When using Node.js `child_process` APIs in Deno, passing a numeric file descriptor (e.g., from `fs.openSync()`) in the `stdio` array does not work correctly. The runtime currently interprets numeric values as internal resource IDs (RIDs) rather than real OS file descriptors.

For example, this pattern should work but currently fails:

```ts
import { spawn } from "node:child_process";
import * as fs from "node:fs";

const fd = fs.openSync("/tmp/output.txt", "w");
const child = spawn("/bin/sh", ["-c", "echo hello >&3"], {
  stdio: ["ignore", "pipe", "pipe", fd],
});
```

The child process should be able to write to the file descriptor provided by the caller. Currently, this fails because:
1. The runtime treats numeric values as internal resource IDs
2. There's no mechanism to pass real OS file descriptors through to child processes
3. When inheriting stdout/stderr, the runtime uses hardcoded OS handles instead of the actual redirected handles (important during `deno test` output capture)

## Expected Behavior

After the fix:

1. **Numeric fd passthrough**: Numeric values in the `stdio` array should be treated as real OS file descriptors that can be passed through to child processes.

2. **Deserialization**: The deserialization logic for the stdio configuration must properly parse numeric values as signed integers (not unsigned) and validate they are non-negative file descriptors.

3. **Error messages**: Error messages for invalid numeric values should reference "file descriptor", not "resource id".

4. **Handle inheritance for stdout/stderr**: When child processes inherit stdout/stderr, they should receive the runtime's actual output handles (which may be redirected during `deno test` output capture), not hardcoded OS-level handles.

5. **String variants preserved**: String variants like `"inherit"`, `"piped"`, `"null"`, and `"ipc_for_internal_use"` must continue to work correctly.

6. **Test coverage**: A new test `spawnWithNumericFdInStdioArray` should be added to `tests/unit_node/child_process_test.ts` that:
   - Opens a temporary file with `fs.openSync()`
   - Spawns a child process with the fd in the stdio array
   - Verifies the child can write to that fd
   - Confirms the expected content was written

## Constraints

- `cargo check -p deno_io` and `cargo check -p deno_process` must pass.
- `cargo clippy -p deno_process -p deno_io -- -D warnings` must pass.
- `cargo fmt` must pass on modified files.
- `cargo test -p deno_io --lib` and `cargo test -p deno_process --lib` must pass.
- The new Node.js compatibility test in `tests/unit_node/child_process_test.ts` must pass.

## Relevant Code Areas

The implementation spans two extension crates:

1. **ext/process/lib.rs**: Contains the process spawning logic and stdio handling
2. **ext/io/lib.rs**: Contains I/O resources and the stdio handle management

The fix requires changes to how the runtime:
- Deserializes numeric values in stdio configurations
- Duplicates and passes file descriptors to child processes on Unix
- Accesses the actual stdout/stderr handles for inheritance mode
- Handles extra stdio entries (fd 3 and beyond)
