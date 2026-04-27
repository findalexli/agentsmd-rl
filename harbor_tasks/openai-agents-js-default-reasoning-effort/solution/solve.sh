#!/bin/bash
# Apply the gold patch for openai/openai-agents-js#1131.
set -euo pipefail

cd /workspace/agents-js

# Idempotency: bail out early if the gold change is already applied.
if grep -q 'GPT_5_CHAT_MODEL_PATTERNS' packages/agents-core/src/defaultModel.ts 2>/dev/null; then
    echo "Gold patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/tidy-mice-wave.md b/.changeset/tidy-mice-wave.md
new file mode 100644
index 000000000..d7dc35f97
--- /dev/null
+++ b/.changeset/tidy-mice-wave.md
@@ -0,0 +1,5 @@
+---
+'@openai/agents-core': patch
+---
+
+fix: update default reasoning effort for newer models
diff --git a/packages/agents-core/src/defaultModel.ts b/packages/agents-core/src/defaultModel.ts
index be7bc51d2..604099f29 100644
--- a/packages/agents-core/src/defaultModel.ts
+++ b/packages/agents-core/src/defaultModel.ts
@@ -1,24 +1,55 @@
 import { loadEnv } from './config';
-import { ModelSettings } from './model';
+import { ModelSettings, ModelSettingsReasoningEffort } from './model';

 export const OPENAI_DEFAULT_MODEL_ENV_VARIABLE_NAME = 'OPENAI_DEFAULT_MODEL';
+const GPT_5_CHAT_MODEL_PATTERNS = [
+  /^gpt-5-chat-latest$/,
+  /^gpt-5\.1-chat-latest$/,
+  /^gpt-5\.2-chat-latest$/,
+  /^gpt-5\.3-chat-latest$/,
+] as const;

 /**
  * Returns True if the model name is a GPT-5 model and reasoning settings are required.
  */
 export function gpt5ReasoningSettingsRequired(modelName: string): boolean {
-  if (modelName.startsWith('gpt-5-chat')) {
-    // gpt-5-chat-latest does not require reasoning settings
+  if (GPT_5_CHAT_MODEL_PATTERNS.some((pattern) => pattern.test(modelName))) {
+    // Chat-latest aliases do not accept reasoning.effort.
     return false;
   }
   // matches any of gpt-5 models
   return modelName.startsWith('gpt-5');
 }

-const NONE_EFFORT_SUPPORTED_MODELS = new Set(['gpt-5.2', 'gpt-5.1']);
+const DEFAULT_REASONING_EFFORT_PATTERNS: Array<
+  readonly [
+    RegExp,
+    Exclude<ModelSettingsReasoningEffort, 'minimal' | 'xhigh' | null>,
+  ]
+> = [
+  [/^gpt-5(?:-\d{4}-\d{2}-\d{2})?$/, 'low'],
+  [/^gpt-5\.1(?:-\d{4}-\d{2}-\d{2})?$/, 'none'],
+  [/^gpt-5\.2(?:-\d{4}-\d{2}-\d{2})?$/, 'none'],
+  [/^gpt-5\.2-pro(?:-\d{4}-\d{2}-\d{2})?$/, 'medium'],
+  [/^gpt-5\.2-codex$/, 'low'],
+  [/^gpt-5\.3-codex$/, 'none'],
+  [/^gpt-5\.4(?:-\d{4}-\d{2}-\d{2})?$/, 'none'],
+  [/^gpt-5\.4-pro(?:-\d{4}-\d{2}-\d{2})?$/, 'medium'],
+  [/^gpt-5\.4-mini(?:-\d{4}-\d{2}-\d{2})?$/, 'none'],
+  [/^gpt-5\.4-nano(?:-\d{4}-\d{2}-\d{2})?$/, 'none'],
+];

-function isNoneEffortSupportedModel(modelName: string): boolean {
-  return NONE_EFFORT_SUPPORTED_MODELS.has(modelName);
+function getDefaultReasoningEffort(
+  modelName: string,
+):
+  | Exclude<ModelSettingsReasoningEffort, 'minimal' | 'xhigh' | null>
+  | undefined {
+  for (const [pattern, effort] of DEFAULT_REASONING_EFFORT_PATTERNS) {
+    if (pattern.test(modelName)) {
+      return effort;
+    }
+  }
+  return undefined;
 }

 /**
@@ -48,16 +79,16 @@ export function getDefaultModel(): string {
 export function getDefaultModelSettings(model?: string): ModelSettings {
   const _model = model ?? getDefaultModel();
   if (gpt5ReasoningSettingsRequired(_model)) {
-    if (isNoneEffortSupportedModel(_model)) {
+    const effort = getDefaultReasoningEffort(_model);
+    if (effort !== undefined) {
       return {
-        reasoning: { effort: 'none' },
+        reasoning: { effort },
         text: { verbosity: 'low' },
       };
     }
     return {
-      // We choose "low" instead of "minimal" because some built-in tools do not support "minimal".
-      // If you want to use "minimal" reasoning effort, pass your own model settings.
-      reasoning: { effort: 'low' },
+      // Keep the GPT-5 text verbosity default, but omit reasoning.effort for
+      // variants whose supported values are not confirmed yet.
       text: { verbosity: 'low' },
     };
   }
diff --git a/packages/agents-core/test/defaultModel.test.ts b/packages/agents-core/test/defaultModel.test.ts
index 47f0c91dd..fd572fc4a 100644
--- a/packages/agents-core/test/defaultModel.test.ts
+++ b/packages/agents-core/test/defaultModel.test.ts
@@ -16,15 +16,19 @@ beforeEach(() => {
   mockedLoadEnv.mockReturnValue({});
 });
 describe('gpt5ReasoningSettingsRequired', () => {
-  test('detects GPT-5 models while ignoring chat latest', () => {
+  test('detects GPT-5 models while ignoring chat latest families', () => {
     expect(gpt5ReasoningSettingsRequired('gpt-5')).toBe(true);
     expect(gpt5ReasoningSettingsRequired('gpt-5.1')).toBe(true);
     expect(gpt5ReasoningSettingsRequired('gpt-5.2')).toBe(true);
     expect(gpt5ReasoningSettingsRequired('gpt-5.2-codex')).toBe(true);
+    expect(gpt5ReasoningSettingsRequired('gpt-5.2-pro')).toBe(true);
+    expect(gpt5ReasoningSettingsRequired('gpt-5.4-pro')).toBe(true);
     expect(gpt5ReasoningSettingsRequired('gpt-5-mini')).toBe(true);
     expect(gpt5ReasoningSettingsRequired('gpt-5-nano')).toBe(true);
-    expect(gpt5ReasoningSettingsRequired('gpt-5-pro')).toBe(true);
     expect(gpt5ReasoningSettingsRequired('gpt-5-chat-latest')).toBe(false);
+    expect(gpt5ReasoningSettingsRequired('gpt-5.1-chat-latest')).toBe(false);
+    expect(gpt5ReasoningSettingsRequired('gpt-5.2-chat-latest')).toBe(false);
+    expect(gpt5ReasoningSettingsRequired('gpt-5.3-chat-latest')).toBe(false);
   });
   test('returns false for non GPT-5 models', () => {
     expect(gpt5ReasoningSettingsRequired('gpt-4o')).toBe(false);
@@ -45,7 +49,7 @@ describe('getDefaultModel', () => {
 describe('isGpt5Default', () => {
   test('returns true only when env points to GPT-5', () => {
     mockedLoadEnv.mockReturnValue({
-      [OPENAI_DEFAULT_MODEL_ENV_VARIABLE_NAME]: 'gpt-5-preview',
+      [OPENAI_DEFAULT_MODEL_ENV_VARIABLE_NAME]: 'gpt-5.4',
     });
     expect(isGpt5Default()).toBe(true);
     mockedLoadEnv.mockReturnValue({
@@ -55,30 +59,130 @@ describe('isGpt5Default', () => {
   });
 });
 describe('getDefaultModelSettings', () => {
-  test('returns reasoning defaults for GPT-5.2 models', () => {
+  test('returns none reasoning defaults for GPT-5.1 models', () => {
+    expect(getDefaultModelSettings('gpt-5.1')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5.1-2025-11-13')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+  });
+
+  test('returns none reasoning defaults for GPT-5.2 models', () => {
     expect(getDefaultModelSettings('gpt-5.2')).toEqual({
       reasoning: { effort: 'none' },
       text: { verbosity: 'low' },
     });
+    expect(getDefaultModelSettings('gpt-5.2-2025-12-11')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+  });
+
+  test('returns none reasoning defaults for GPT-5.3 codex models', () => {
+    expect(getDefaultModelSettings('gpt-5.3-codex')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
   });
-  test('returns reasoning defaults for GPT-5.2 codex models', () => {
+
+  test('returns none reasoning defaults for GPT-5.4 models', () => {
+    expect(getDefaultModelSettings('gpt-5.4')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+  });
+
+  test('returns none reasoning defaults for GPT-5.4 snapshot families', () => {
+    expect(getDefaultModelSettings('gpt-5.4-2026-03-05')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5.4-mini-2026-03-17')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5.4-nano-2026-03-17')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+  });
+
+  test('returns none reasoning defaults for GPT-5.4 mini and nano models', () => {
+    expect(getDefaultModelSettings('gpt-5.4-mini')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5.4-nano')).toEqual({
+      reasoning: { effort: 'none' },
+      text: { verbosity: 'low' },
+    });
+  });
+
+  test('returns low-effort defaults for the base GPT-5 model', () => {
+    expect(getDefaultModelSettings('gpt-5')).toEqual({
+      reasoning: { effort: 'low' },
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5-2025-08-07')).toEqual({
+      reasoning: { effort: 'low' },
+      text: { verbosity: 'low' },
+    });
+  });
+
+  test('returns low-effort defaults for GPT-5.2 codex models', () => {
     expect(getDefaultModelSettings('gpt-5.2-codex')).toEqual({
       reasoning: { effort: 'low' },
       text: { verbosity: 'low' },
     });
   });
-  test('returns reasoning defaults for GPT-5.1 models', () => {
-    expect(getDefaultModelSettings('gpt-5.1')).toEqual({
-      reasoning: { effort: 'none' },
+
+  test('returns medium defaults for GPT-5 pro models', () => {
+    expect(getDefaultModelSettings('gpt-5.2-pro')).toEqual({
+      reasoning: { effort: 'medium' },
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5.2-pro-2025-12-11')).toEqual({
+      reasoning: { effort: 'medium' },
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5.4-pro')).toEqual({
+      reasoning: { effort: 'medium' },
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5.4-pro-2026-03-05')).toEqual({
+      reasoning: { effort: 'medium' },
       text: { verbosity: 'low' },
     });
   });
-  test('returns reasoning defaults for other GPT-5 models', () => {
+
+  test('omits reasoning defaults for GPT-5 variants without confirmed support', () => {
     expect(getDefaultModelSettings('gpt-5-mini')).toEqual({
-      reasoning: { effort: 'low' },
       text: { verbosity: 'low' },
     });
+    expect(getDefaultModelSettings('gpt-5-mini-2025-08-07')).toEqual({
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5-nano')).toEqual({
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5-nano-2025-08-07')).toEqual({
+      text: { verbosity: 'low' },
+    });
+    expect(getDefaultModelSettings('gpt-5.1-codex')).toEqual({
+      text: { verbosity: 'low' },
+    });
+  });
+
+  test('returns empty settings for GPT-5 chat latest aliases', () => {
+    expect(getDefaultModelSettings('gpt-5-chat-latest')).toEqual({});
+    expect(getDefaultModelSettings('gpt-5.1-chat-latest')).toEqual({});
+    expect(getDefaultModelSettings('gpt-5.2-chat-latest')).toEqual({});
+    expect(getDefaultModelSettings('gpt-5.3-chat-latest')).toEqual({});
   });
+
   test('returns empty settings for non GPT-5 models', () => {
     expect(getDefaultModelSettings('gpt-4o')).toEqual({});
   });
PATCH

echo "Gold patch applied."
