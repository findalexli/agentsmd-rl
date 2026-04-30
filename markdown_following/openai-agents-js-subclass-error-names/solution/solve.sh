#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/openai-agents-js
cd "$REPO"

# Idempotency guard: skip if the gold patch has already been applied.
if grep -qF 'this.name = new.target.name;' packages/agents-core/src/errors.ts; then
    echo "[solve] gold patch already applied"
else
    git apply --allow-empty <<'PATCH'
diff --git a/.changeset/bright-comets-spark.md b/.changeset/bright-comets-spark.md
new file mode 100644
index 000000000..dec7b5460
--- /dev/null
+++ b/.changeset/bright-comets-spark.md
@@ -0,0 +1,5 @@
+---
+'@openai/agents-core': patch
+---
+
+fix(agents-core): #670 set subclass error names
diff --git a/packages/agents-core/src/errors.ts b/packages/agents-core/src/errors.ts
index 4b1c75f78..35cced31b 100644
--- a/packages/agents-core/src/errors.ts
+++ b/packages/agents-core/src/errors.ts
@@ -21,6 +21,7 @@ export abstract class AgentsError extends Error {

   constructor(message: string, state?: RunState<any, Agent<any, any>>) {
     super(message);
+    this.name = new.target.name;
     this.state = state;
   }
 }
diff --git a/packages/agents-core/test/agent.test.ts b/packages/agents-core/test/agent.test.ts
index 9c2ae71e0..df1215640 100644
--- a/packages/agents-core/test/agent.test.ts
+++ b/packages/agents-core/test/agent.test.ts
@@ -177,7 +177,7 @@ describe('Agent', () => {

     const result1 = await tool.invoke({} as any, 'hey how are you?');
     expect(result1).toBe(
-      'An error occurred while running the tool. Please try again. Error: Error: Invalid JSON input for tool',
+      'An error occurred while running the tool. Please try again. Error: InvalidToolInputError: Invalid JSON input for tool',
     );
     setDefaultModelProvider(new FakeModelProvider());
     const result2 = await tool.invoke(
diff --git a/packages/agents-core/test/errors.test.ts b/packages/agents-core/test/errors.test.ts
index b4822ad56..c4852412b 100644
--- a/packages/agents-core/test/errors.test.ts
+++ b/packages/agents-core/test/errors.test.ts
@@ -50,4 +50,29 @@ describe('errors', () => {
       throw toolCallError;
     }).toThrow('Test error');
   });
+
+  test('should set error names', () => {
+    expect(new MaxTurnsExceededError('Test error', {} as any).name).toBe(
+      'MaxTurnsExceededError',
+    );
+    expect(new ModelBehaviorError('Test error', {} as any).name).toBe(
+      'ModelBehaviorError',
+    );
+    expect(new UserError('Test error', {} as any).name).toBe('UserError');
+    expect(
+      new InputGuardrailTripwireTriggered('Test error', {} as any, {} as any)
+        .name,
+    ).toBe('InputGuardrailTripwireTriggered');
+    expect(
+      new OutputGuardrailTripwireTriggered('Test error', {} as any, {} as any)
+        .name,
+    ).toBe('OutputGuardrailTripwireTriggered');
+    expect(
+      new GuardrailExecutionError('Test error', new Error('cause'), {} as any)
+        .name,
+    ).toBe('GuardrailExecutionError');
+    expect(
+      new ToolCallError('Test error', new Error('cause'), {} as any).name,
+    ).toBe('ToolCallError');
+  });
 });
PATCH
fi

# Rebuild agents-core dist (.js and .mjs) so the runtime exports reflect the source change.
pnpm exec tsc-multi
