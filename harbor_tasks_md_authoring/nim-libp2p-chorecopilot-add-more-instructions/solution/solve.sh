#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nim-libp2p

# Idempotency guard
if grep -qF "- Do not use `asyncSpawn` unless the future reference is explicitly tracked. Run" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -184,8 +184,10 @@ The test runner (`libp2p.nimble`) always compiles with:
 - Async procedures return `Future[T]` or `Future[void]`
 - Manually created `Futures` should specify the exceptions they raise: `Future[someType].Raising([ListOfExceptionsHere]).init()`
 - `init()` procedure should always be called with identifier of future that explains purpose of future or where it was created. For example `init("Stream.readOnce")`
-- `cancel()` procedure of `Future` type is deprecated, code should ether call `cancelSoon()` for non blocking call or `cancelAndWait()` for blocking call till future is canceled.
+- `cancel()` procedure of `Future` type is deprecated, code should either call `cancelSoon()` for non-blocking call or `cancelAndWait()` for blocking call until the future is canceled/has been canceled.
 - Give suggestions if  `cancelSoon()` or `cancelAndWait()` should be called.
+- Do not use `asyncSpawn` unless the future reference is explicitly tracked. Running a future with `asyncSpawn` without tracking its reference risks the future being freed/deallocated when it becomes unreferenced.
+- Usage of `AsyncLock` must always be documented. Provide a clear explanation of why the lock is required in that context. This ensures that locking decisions are transparent, justified, and maintainable.
 
 ### Avoid `sleepAsync`
 - `sleepAsync` should be avoided when is used to fix race condition, or to wait on condition, becasue it is always source of flakyness.
@@ -237,6 +239,16 @@ The test runner (`libp2p.nimble`) always compiles with:
   - Symbols required by an interface, callback, or external API
   - Compile‑time only symbols used via `static`, `when`, or macro expansion
 
+#### Leverage the Type System
+- Enforce strong typing: Always prefer explicit, well-defined types over loosely typed or primitive representations.
+- Use `chronos.Duration` for durations
+  - All duration values must be represented using `chronos.Duration`.
+  - Do not use primitive types (`float`, `int`, etc.) for storing or passing durations. Replace them with `chronos.Duration`.
+- Avoid tuples in public interfaces
+  - Public APIs must not expose tuples.
+  - Instead, define a named type (e.g., object) with clear field names to ensure readability and maintainability.
+  - Exception: Tuples may be used only in functions that are internal to a single file and invoked in one place. They must never leak into shared or public APIs.
+
 #### Exceptions
 - For new or significantly modified public `*` functions, add an explicit `{.raises.}` annotation; existing public APIs may not yet follow this consistently.
 - If you must use exceptions, use specific exception types. Avoid raising or capturing `CatchableError`. Catching `CatchableError` implies that all errors are funnelled through the same exception handler.
PATCH

echo "Gold patch applied."
