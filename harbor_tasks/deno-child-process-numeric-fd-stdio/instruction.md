# Support numeric file descriptors in child_process stdio array

## Problem

When using Node.js `child_process` APIs in Deno, passing a numeric file descriptor (e.g., from `fs.openSync()`) in the `stdio` array does not work correctly. The runtime currently interprets numeric values as Deno internal resource IDs (from the old resource table), but since `fs.openSync` now returns real OS file descriptors, these numeric values should be treated as raw fds instead.

For example, this Node.js-compatible pattern fails:

```ts
import { spawn } from "node:child_process";
import * as fs from "node:fs";

const fd = fs.openSync("/tmp/output.txt", "w");
const child = spawn("/bin/sh", ["-c", "echo hello >&3"], {
  stdio: ["ignore", "pipe", "pipe", fd],
});
```

The child process cannot write to fd 3 because the runtime tries to look up the numeric value in the resource table instead of using it as an OS file descriptor.

## Expected Behavior

Numeric values in the `stdio` array should be treated as real OS file descriptors. The runtime should duplicate (`dup`) the fd for the child process, similar to how Node.js handles this. Additionally, when inheriting stdout/stderr, the child should receive the runtime's actual output handles (which may be redirected, e.g., during `deno test`), not the original OS stdout/stderr.

## Files to Look At

- `ext/process/lib.rs` — Contains the `StdioOrRid` enum and `as_stdio()` method that resolve stdio options for child processes. The type naming and fd handling logic need updating.
- `ext/io/lib.rs` — IO extension initialization where stdout/stderr handles are set up. Needs to store handles for child process inheritance.
- `ext/node/polyfills/internal/child_process.ts` — TypeScript polyfill for Node.js child_process. The comment about numeric values needs updating to reflect fd semantics.
- `tests/unit_node/child_process_test.ts` — Add a test exercising numeric fd in the stdio array.
