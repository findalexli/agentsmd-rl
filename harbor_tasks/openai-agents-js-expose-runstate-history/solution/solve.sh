#!/bin/bash
set -euo pipefail

cd /workspace/openai-agents-js

git apply <<'PATCH'
diff --git a/.changeset/expose-runstate-history.md b/.changeset/expose-runstate-history.md
new file mode 100644
index 000000000..8983e90e1
--- /dev/null
+++ b/.changeset/expose-runstate-history.md
@@ -0,0 +1,5 @@
+---
+'@openai/agents-core': patch
+---
+
+feat: expose the `history` getter on `RunState` to access input and generated items.
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
diff --git a/packages/agents-core/test/runState.test.ts b/packages/agents-core/test/runState.test.ts
index 4d9a57ef0..c6c67765e 100644
--- a/packages/agents-core/test/runState.test.ts
+++ b/packages/agents-core/test/runState.test.ts
@@ -8,7 +8,10 @@ import {
 } from '../src/runState';
 import { RunContext } from '../src/runContext';
 import { Agent } from '../src/agent';
-import { RunToolApprovalItem as ToolApprovalItem } from '../src/items';
+import {
+  RunToolApprovalItem as ToolApprovalItem,
+  RunMessageOutputItem,
+} from '../src/items';
 import { computerTool } from '../src/tool';
 import * as protocol from '../src/types/protocol';
 import { TEST_MODEL_MESSAGE, FakeComputer } from './stubs';
@@ -31,6 +34,32 @@ describe('RunState', () => {
     expect(state._context.context).toEqual({ foo: 'bar' });
   });

+  it('returns history including original input and generated items', () => {
+    const context = new RunContext();
+    const agent = new Agent({ name: 'HistAgent' });
+    const state = new RunState(context, 'input', agent, 1);
+    state._generatedItems.push(
+      new RunMessageOutputItem(TEST_MODEL_MESSAGE, agent),
+    );
+
+    expect(state.history).toEqual([
+      { type: 'message', role: 'user', content: 'input' },
+      TEST_MODEL_MESSAGE,
+    ]);
+  });
+
+  it('preserves history after serialization', async () => {
+    const context = new RunContext();
+    const agent = new Agent({ name: 'HistAgent2' });
+    const state = new RunState(context, 'input', agent, 1);
+    state._generatedItems.push(
+      new RunMessageOutputItem(TEST_MODEL_MESSAGE, agent),
+    );
+
+    const restored = await RunState.fromString(agent, state.toString());
+    expect(restored.history).toEqual(state.history);
+  });
+
   it('toJSON and toString produce valid JSON', () => {
     const context = new RunContext();
     const agent = new Agent({ name: 'Agent1' });
PATCH

pnpm -F agents-core build

# Idempotency check
grep -q 'get history(): AgentInputItem\[\]' packages/agents-core/src/runState.ts || {
  echo "ERROR: Patch did not apply correctly"
  exit 1
}
