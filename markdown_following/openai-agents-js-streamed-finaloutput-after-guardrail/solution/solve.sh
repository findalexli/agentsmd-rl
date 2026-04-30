#!/usr/bin/env bash
# Gold solve for openai/openai-agents-js#1124.
# Applies the runtime fix from packages/agents-core/src/run.ts.
# Tests/changeset are intentionally omitted: they belong to the verifier or
# are not required for the runtime behavior under test.
set -euo pipefail

cd /workspace/openai-agents-js

# Idempotency: if the distinctive marker is already present, skip.
if grep -q "Do not leave blocked output visible through StreamedRunResult.finalOutput" \
        packages/agents-core/src/run.ts; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/agents-core/src/run.ts b/packages/agents-core/src/run.ts
index 4813228b..ef96e09e 100644
--- a/packages/agents-core/src/run.ts
+++ b/packages/agents-core/src/run.ts
@@ -1305,11 +1305,18 @@ export class Runner extends RunHooks<any, AgentOutputType<unknown>> {
         const currentStep = result.state._currentStep;
         switch (currentStep.type) {
           case 'next_step_final_output':
-            await runOutputGuardrails(
-              result.state,
-              this.outputGuardrailDefs,
-              currentStep.output,
-            );
+            try {
+              await runOutputGuardrails(
+                result.state,
+                this.outputGuardrailDefs,
+                currentStep.output,
+              );
+            } catch (error) {
+              // Do not leave blocked output visible through StreamedRunResult.finalOutput.
+              result.state._currentStep = undefined;
+              result.state._finalOutputSource = undefined;
+              throw error;
+            }
             result.state._currentTurnInProgress = false;
             await persistStreamInputIfNeeded();
             // Guardrails must succeed before persisting session memory to avoid storing blocked outputs.
PATCH

echo "Patch applied."
