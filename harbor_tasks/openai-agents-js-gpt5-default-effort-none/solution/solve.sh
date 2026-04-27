#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openai-agents-js

# Idempotency: if the gold marker is already present, the patch has been applied.
if grep -q "NONE_EFFORT_SUPPORTED_MODELS" packages/agents-core/src/defaultModel.ts 2>/dev/null; then
    echo "Gold patch already applied; skipping."
    exit 0
fi

git apply <<'PATCH'
diff --git a/.changeset/gpt-5-2-default-reasoning-none.md b/.changeset/gpt-5-2-default-reasoning-none.md
new file mode 100644
index 000000000..6bf1e089b
--- /dev/null
+++ b/.changeset/gpt-5-2-default-reasoning-none.md
@@ -0,0 +1,5 @@
+---
+'@openai/agents-core': minor
+---
+
+feat(agents-core): update gpt-5.1/5.2 defaults and reasoning effort types
diff --git a/packages/agents-core/src/defaultModel.ts b/packages/agents-core/src/defaultModel.ts
index 20a3575c3..be7bc51d2 100644
--- a/packages/agents-core/src/defaultModel.ts
+++ b/packages/agents-core/src/defaultModel.ts
@@ -15,6 +15,12 @@ export function gpt5ReasoningSettingsRequired(modelName: string): boolean {
   return modelName.startsWith('gpt-5');
 }

+const NONE_EFFORT_SUPPORTED_MODELS = new Set(['gpt-5.2', 'gpt-5.1']);
+
+function isNoneEffortSupportedModel(modelName: string): boolean {
+  return NONE_EFFORT_SUPPORTED_MODELS.has(modelName);
+}
+
 /**
  * Returns True if the default model is a GPT-5 model.
  * This is used to determine if the default model settings are compatible with GPT-5 models.
@@ -42,10 +48,15 @@ export function getDefaultModel(): string {
 export function getDefaultModelSettings(model?: string): ModelSettings {
   const _model = model ?? getDefaultModel();
   if (gpt5ReasoningSettingsRequired(_model)) {
+    if (isNoneEffortSupportedModel(_model)) {
+      return {
+        reasoning: { effort: 'none' },
+        text: { verbosity: 'low' },
+      };
+    }
     return {
-      // We chose "low" instead of "minimal" because some of the built-in tools
-      // (e.g., file search, image generation, etc.) do not support "minimal"
-      // If you want to use "minimal" reasoning effort, you can pass your own model settings
+      // We choose "low" instead of "minimal" because some built-in tools do not support "minimal".
+      // If you want to use "minimal" reasoning effort, pass your own model settings.
       reasoning: { effort: 'low' },
       text: { verbosity: 'low' },
     };
diff --git a/packages/agents-core/src/model.ts b/packages/agents-core/src/model.ts
index 3cb021fa4..165d16bf0 100644
--- a/packages/agents-core/src/model.ts
+++ b/packages/agents-core/src/model.ts
@@ -27,15 +27,16 @@ export type ModelSettingsToolChoice =

 /**
  * Constrains effort on reasoning for [reasoning models](https://platform.openai.com/docs/guides/reasoning).
- * Currently supported values are `minimal`, `low`, `medium`, and `high`.
+ * Currently supported values are `none`, `minimal`, `low`, `medium`, `high`, and `xhigh`.
  * Reducing reasoning effort can result in faster responses and fewer tokens used on reasoning in a response.
  */
 export type ModelSettingsReasoningEffort =
-  | 'none' // for gpt-5.1
+  | 'none' // for gpt-5.1 and newer
   | 'minimal' // for gpt-5
   | 'low'
   | 'medium'
   | 'high'
+  | 'xhigh'
   | null;

 /**
@@ -44,7 +45,7 @@ export type ModelSettingsReasoningEffort =
 export type ModelSettingsReasoning = {
   /**
    * Constrains effort on reasoning for [reasoning models](https://platform.openai.com/docs/guides/reasoning).
-   * Currently supported values are `minimal`, `low`, `medium`, and `high`.
+   * Currently supported values are `none`, `minimal`, `low`, `medium`, `high`, and `xhigh`.
    * Reducing reasoning effort can result in faster responses and fewer tokens used on reasoning in a response.
    */
   effort?: ModelSettingsReasoningEffort | null;
diff --git a/packages/agents-core/test/defaultModel.test.ts b/packages/agents-core/test/defaultModel.test.ts
index 44cefbb9a..47f0c91dd 100644
--- a/packages/agents-core/test/defaultModel.test.ts
+++ b/packages/agents-core/test/defaultModel.test.ts
@@ -18,6 +18,9 @@ beforeEach(() => {
 describe('gpt5ReasoningSettingsRequired', () => {
   test('detects GPT-5 models while ignoring chat latest', () => {
     expect(gpt5ReasoningSettingsRequired('gpt-5')).toBe(true);
+    expect(gpt5ReasoningSettingsRequired('gpt-5.1')).toBe(true);
+    expect(gpt5ReasoningSettingsRequired('gpt-5.2')).toBe(true);
+    expect(gpt5ReasoningSettingsRequired('gpt-5.2-codex')).toBe(true);
     expect(gpt5ReasoningSettingsRequired('gpt-5-mini')).toBe(true);
     expect(gpt5ReasoningSettingsRequired('gpt-5-nano')).toBe(true);
     expect(gpt5ReasoningSettingsRequired('gpt-5-pro')).toBe(true);
@@ -52,7 +55,25 @@ describe('isGpt5Default', () => {
   });
 });
 describe('getDefaultModelSettings', () => {
-  test('returns reasoning defaults for GPT-5 models', () => {
+  test('returns reasoning defaults for GPT-5.2 models', () => {
+    expect(getDefaultModelSettings('gpt-5.2')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+  });
+  test('returns reasoning defaults for GPT-5.2 codex models', () => {
+    expect(getDefaultModelSettings('gpt-5.2-codex')).toEqual({
+      reasoning: { effort: 'low' },
+      text: { verbosity: 'low' },
+    });
+  });
+  test('returns reasoning defaults for GPT-5.1 models', () => {
+    expect(getDefaultModelSettings('gpt-5.1')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+  });
+  test('returns reasoning defaults for other GPT-5 models', () => {
     expect(getDefaultModelSettings('gpt-5-mini')).toEqual({
       reasoning: { effort: 'low' },
       text: { verbosity: 'low' },
PATCH

echo "Gold patch applied."
