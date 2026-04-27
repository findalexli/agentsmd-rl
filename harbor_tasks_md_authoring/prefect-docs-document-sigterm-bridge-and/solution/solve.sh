#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- `engine/` \u2192 Result-to-state linking, SIGTERM bridge management, and control-in" "src/prefect/utilities/AGENTS.md" && grep -qF "- **All SIGTERM-state reads and writes must hold `_prefect_sigterm_bridge_lock`." "src/prefect/utilities/engine/AGENTS.md" && grep -qF "- `sanitize_subprocess_env(env) -> dict[str, str]` \u2014 strip `None` values from an" "src/prefect/utilities/processutils/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/utilities/AGENTS.md b/src/prefect/utilities/AGENTS.md
@@ -21,7 +21,7 @@ Each subpackage owns its own `AGENTS.md` with entry points and pitfalls specific
 - `callables/` → Function signature introspection, parameter coercion, parameter schema generation (see `callables/AGENTS.md`)
 - `asyncutils/` → Async/sync bridging, thread coordination, concurrency primitives (see `asyncutils/AGENTS.md`)
 - `templating/` → Placeholder detection and value application for Prefect's `{{ }}` templating (see `templating/AGENTS.md`)
-- `engine/` → Result-to-state linking and identity-verified `EngineContext` lookups (see `engine/AGENTS.md`)
+- `engine/` → Result-to-state linking, SIGTERM bridge management, and control-intent coordination (see `engine/AGENTS.md`)
 - `filesystem/` → File filtering, path normalization, `tmpchdir` (see `filesystem/AGENTS.md`)
 
 ## Flat modules
diff --git a/src/prefect/utilities/engine/AGENTS.md b/src/prefect/utilities/engine/AGENTS.md
@@ -1,19 +1,31 @@
 # engine
 
-Result-to-state linking, identity-verified `EngineContext` lookups, and helpers shared by the flow/task engines.
+Result-to-state linking, SIGTERM bridge management, and helpers shared by the flow/task engines.
 
 ## Purpose & Scope
 
-This module is the glue between Python return values (which callers receive) and the `State` objects that represent them on the server. It maintains the identity-keyed `run_results` map inside `EngineContext` and exposes safe accessors for linking and retrieving those states.
+Two responsibilities live here:
+
+1. **Result-to-state linking** — glue between Python return values (which callers receive) and the `State` objects that represent them on the server. Maintains the identity-keyed `run_results` map inside `EngineContext` and exposes safe accessors.
+
+2. **SIGTERM bridge** — installs and tears down Prefect's SIGTERM handler (`TerminationSignal`), coordinates control-intent acknowledgement with the runner, and exposes locked helpers so the engine can atomically commit cancellation intent before signalling readiness to the runner.
 
 Naming and hook-resolution helpers for custom flow/task run names live in sibling `../_engine.py` (flat module), not here.
 
 ## Entry Points
 
+**Result linking:**
 - `link_state_to_result(state, result, run_type)` — associate a `State` with a Python object under a specific `RunType` for later lookup via `get_state_for_result`.
 - `link_state_to_flow_run_result(state, result)` / `link_state_to_task_run_result(state, result)` — scoped variants used by the flow and task engines respectively.
 - `get_state_for_result(obj) -> tuple[State, RunType] | None` — identity-verified lookup that handles `id()` collisions safely.
 
+**SIGTERM bridge:**
+- `capture_sigterm()` — context manager that installs Prefect's SIGTERM bridge; outermost scope installs it, nested scopes reuse or reinstall as needed. The runner's control listener connects only while this context is active.
+- `is_prefect_sigterm_handler_installed() -> bool` — check (under lock) whether Prefect's bridge is the active SIGTERM handler.
+- `can_ack_control_intent() -> bool` — check (under the same lock) whether the child can safely acknowledge a queued control intent.
+- `commit_control_intent_and_ack(commit_intent, clear_intent, send_ack, trigger_cancel)` — atomically commit a control intent and write the ack byte to the runner, all under `_prefect_sigterm_bridge_lock`.
+
 ## Pitfalls
 
 - **Never access `EngineContext.run_results` directly via `id(obj)`.** Always call `get_state_for_result(obj)` — the accessor verifies object identity in addition to the ID match, avoiding false hits when Python reuses an id for a different object after GC.
+- **All SIGTERM-state reads and writes must hold `_prefect_sigterm_bridge_lock`.** The lock is a `threading.RLock` that serializes handler install/restore with ack writes. Reading `signal.getsignal(SIGTERM)` outside the lock creates a TOCTOU race where the handler is restored after the child decides it's safe to ack but before the runner observes the ack byte.
diff --git a/src/prefect/utilities/processutils/AGENTS.md b/src/prefect/utilities/processutils/AGENTS.md
@@ -8,6 +8,7 @@ Cross-platform subprocess primitives used by workers, runners, bundle execution,
 
 ## Entry Points
 
+- `sanitize_subprocess_env(env) -> dict[str, str]` — strip `None` values from an env mapping before passing to subprocess launch APIs; `None` means "omit this key", which `subprocess` and `anyio.open_process` do not accept.
 - `run_process(command, ...)` — async subprocess runner with output streaming and signal forwarding.
 - `consume_process_output(process, stdout_sink, stderr_sink)` — drain a running process's streams into writers.
 - `stream_text(source, *sinks)` — fan out a text stream to multiple sinks.
PATCH

echo "Gold patch applied."
