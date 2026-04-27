#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "The background task is started in `__aenter__` and after each reconnect, and can" "src/prefect/events/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/events/AGENTS.md b/src/prefect/events/AGENTS.md
@@ -9,6 +9,15 @@ Client-side event system for emitting, subscribing to, and defining automations
 - Automations combine triggers (event, metric, compound, sequence) with actions.
 - `DeploymentTriggerTypes` are the subset of triggers usable in `prefect.yaml` deployment definitions.
 
+## clients.py — Checkpointing Invariant
+
+`PrefectEventsClient` uses **two independent checkpointing mechanisms** to confirm server receipt of sent events:
+
+1. **Count-based** (`checkpoint_every`, default 700): checkpoints after N emitted events.
+2. **Time-based** (`checkpoint_interval`, default 30s): a background `asyncio.Task` that fires periodically regardless of event count. Prevents unbounded buffer growth for low-throughput connections.
+
+The background task is started in `__aenter__` and after each reconnect, and cancelled in `__aexit__`. If you subclass or mock `PrefectEventsClient`, ensure both checkpointing paths are exercised — the count threshold alone is not sufficient for low-volume scenarios.
+
 ## Structure
 
 - `schemas/` — Pydantic models: `Event`, `Resource`, `RelatedResource`, `Automation`, triggers, deployment triggers
PATCH

echo "Gold patch applied."
