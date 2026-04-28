#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "**Extending intents:** The only intent today is `\"cancel\"`. The byte map (`_BYTE" "src/prefect/runner/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/runner/AGENTS.md b/src/prefect/runner/AGENTS.md
@@ -11,7 +11,9 @@ Thin facade over single-responsibility extracted classes. New behavior belongs i
 | FlowRunExecutor | _flow_run_executor.py | Per-run lifecycle: submitting -> start -> wait -> crashed/hooks |
 | ProcessManager | _process_manager.py | Process map, PID tracking, kill with SIGTERM->SIGKILL |
 | StateProposer | _state_proposer.py | All API state transition proposals |
-| CancellationManager | _cancellation_manager.py | Kill -> hooks -> state -> event cancellation sequence |
+| CancellationManager | _cancellation_manager.py | control-channel signal -> kill -> hooks -> state -> event cancellation sequence |
+| CancelFinalizer | _cancel_finalizer.py | Persist Cancelled state after kill; fall back to Crashed if state cannot be confirmed |
+| ControlChannel | _control_channel.py | Runner-side TCP loopback IPC for delivering cancel intent to child processes before kill |
 | HookRunner | _hook_runner.py | on_cancellation / on_crashed hook execution |
 | EventEmitter | _event_emitter.py | Event emission via EventsClient; degrades to NullEventsClient on WebSocket rejection |
 | LimitManager | _limit_manager.py | Concurrency limiting |
@@ -61,6 +63,23 @@ Services enter in this order during `Runner.__aenter__` (teardown is exact rever
 
 This ordering is a hard constraint. Getting it wrong causes ClosedResourceError during shutdown. Place new services carefully in this sequence.
 
+## ControlChannel: Intent Before Kill
+
+`ControlChannel` (`_control_channel.py`) is a TCP loopback socket server that delivers a single-byte *intent* to child processes before the runner sends the actual kill signal. The child-side counterpart lives in `prefect._internal.control_listener`.
+
+**How cancellation uses it:**
+1. Runner signals `"cancel"` intent over the channel and waits up to 1 s for the child's `b'a'` ack.
+2. If the child acks, the intent is committed in the child before the SIGTERM arrives, so the engine's `except TerminationSignal` block can dispatch to `on_cancellation` hooks instead of `on_crashed`.
+3. Runner then proceeds through `ProcessManager.kill()` regardless of ack status.
+
+**POSIX vs Windows difference:**
+- POSIX: ack only means "SIGTERM bridge is armed and intent is seeded." The runner's real `SIGTERM` is still the only trigger that interrupts blocking code. Kill happens immediately after ack.
+- Windows: ack means the child has queued `_thread.interrupt_main(SIGTERM)`. The runner gives the child a 30 s grace window to self-exit before falling back to an external kill.
+
+**Failure modes:** If the child never connects or never acks within 1 s, `signal()` returns `False` and the runner falls through to the normal kill path — the engine treats the termination as a crash, same as today.
+
+**Extending intents:** The only intent today is `"cancel"`. The byte map (`_BYTE_FOR_INTENT` in `_control_channel.py` and `_INTENT_FOR_BYTE` in `_internal/control_listener.py`) must stay in sync — adding a new intent (`"suspend"`) is a matched one-line change on each side.
+
 ## ProcessStarter Strategy Pattern
 
 Each execution mode has a ProcessStarter implementation. To add a new execution mode, implement the ProcessStarter protocol and inject it into FlowRunExecutor -- do not add a new code path to Runner.
PATCH

echo "Gold patch applied."
