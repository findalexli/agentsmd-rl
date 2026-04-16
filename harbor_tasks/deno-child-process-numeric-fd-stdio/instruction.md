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

1. **Numeric fd passthrough**: Numeric values in the `stdio` array should be treated as real OS file descriptors, duplicated and passed through to child processes. The enum representing stdio options should be renamed from `StdioOrRid` to `StdioOrFd`, with the `Rid(ResourceId)` variant replaced by `Fd(i32)`.

2. **Deserialization and error messages**: Numeric fd values must be parsed using signed integer logic (`as_i64()`). Error messages should reference "file descriptor", not "resource id":
   - Invalid number: `"Expected a non-negative integer file descriptor"`
   - Wrong type: `Expected a file descriptor, "inherit", "piped", or "null"`

3. **FD duplication**: When converting a numeric fd for child process use, duplicate it with `libc::dup()` and wrap the result via `from_raw_fd` for safe ownership transfer.

4. **Handle inheritance for stdout/stderr**: The IO extension should define a public struct `ChildProcessStdio` with `pub stdout: StdFile` and `pub stderr: StdFile` fields. This struct holds the runtime's actual output handles. The process extension should import it via `use deno_io::ChildProcessStdio` and access it via `state.borrow::<ChildProcessStdio>()` when handling inherit mode — replacing the old approach of constructing from hardcoded resource IDs.

5. **Extra stdio support**: The `extra_stdio` field in `SpawnArgs` should be typed as `Vec<StdioOrFd>` to accept both piped and numeric fd entries.

6. **Preserved behavior**: String variants `"inherit"`, `"piped"`, `"null"`, and `"ipc_for_internal_use"` must continue to work. The `ChildStdio` struct must retain `stdin`, `stdout`, and `stderr` fields typed with the renamed enum. The `FileResource` import is no longer needed in the process extension.

## Constraints

- `cargo check -p deno_io` and `cargo check -p deno_process` must pass.
- `cargo clippy -p deno_process -p deno_io -- -D warnings` must pass.
- `cargo fmt` must pass on modified files.
- `cargo test -p deno_io --lib` and `cargo test -p deno_process --lib` must pass.
