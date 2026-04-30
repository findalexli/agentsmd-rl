#!/bin/bash
set -euo pipefail

cd /workspace/openai-agents-js

if grep -q "get history(): AgentInputItem\[\]" packages/agents-core/src/runState.ts; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/agents-core/src/runState.ts b/packages/agents-core/src/runState.ts
index a18e6493d..cbb14d1bf 100644
--- a/packages/agents-core/src/runState.ts
+++ b/packages/agents-core/src/runState.ts
@@ -12,6 +12,7 @@ import {
 } from './items';
 import type { ModelResponse } from './model';
 import { RunContext } from './runContext';
+import { getTurnInput } from './run';
 import {
   AgentToolUseTracker,
   nextStepSchema,
@@ -327,6 +328,15 @@ export class RunState<TContext, TAgent extends Agent<any, any>> {
     this._trace = getCurrentTrace();
   }

+  /**
+   * The history of the agent run. This includes the input items and the new items generated during the run.
+   *
+   * This can be used as inputs for the next agent run.
+   */
+  get history(): AgentInputItem[] {
+    return getTurnInput(this._originalInput, this._generatedItems);
+  }
+
   /**
    * Returns all interruptions if the current step is an interruption otherwise returns an empty array.
    */
PATCH

echo "Patch applied."
