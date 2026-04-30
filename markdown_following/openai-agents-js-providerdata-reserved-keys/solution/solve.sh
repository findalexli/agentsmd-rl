#!/usr/bin/env bash
# solve.sh — apply the gold fix for openai/openai-agents-js#1064.
# Idempotent: a second run is a no-op.
set -euo pipefail

REPO=/workspace/openai-agents-js
cd "$REPO"

# Idempotency guard — distinctive line from the patch.
if grep -q "getProviderDataWithoutReservedKeys" \
        packages/agents-openai/src/utils/providerData.ts 2>/dev/null; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/chatcompletions-providerdata-filtering.md b/.changeset/chatcompletions-providerdata-filtering.md
new file mode 100644
index 000000000..c6ed7825b
--- /dev/null
+++ b/.changeset/chatcompletions-providerdata-filtering.md
@@ -0,0 +1,5 @@
+---
+'@openai/agents-openai': patch
+---
+
+fix: preserve canonical chat completions providerData fields
diff --git a/packages/agents-openai/src/openaiChatCompletionsConverter.ts b/packages/agents-openai/src/openaiChatCompletionsConverter.ts
index d6573c975..5e316da25 100644
--- a/packages/agents-openai/src/openaiChatCompletionsConverter.ts
+++ b/packages/agents-openai/src/openaiChatCompletionsConverter.ts
@@ -1,6 +1,7 @@
 import type {
   ChatCompletionAssistantMessageParam,
   ChatCompletionContentPart,
+  ChatCompletionContentPartInputAudio,
   ChatCompletionMessageParam,
   ChatCompletionTool,
   ChatCompletionToolChoiceOption,
@@ -12,6 +13,7 @@ import {
   protocol,
   UserError,
 } from '@openai/agents-core';
+import { getProviderDataWithoutReservedKeys } from './utils/providerData';
 
 export function convertToolChoice(
   toolChoice: 'auto' | 'required' | 'none' | (string & {}) | undefined | null,
@@ -38,13 +40,16 @@ export function extractAllAssistantContent(
       out.push({
         type: 'text',
         text: c.text,
-        ...c.providerData,
+        ...getProviderDataWithoutReservedKeys(c.providerData, ['type', 'text']),
       });
     } else if (c.type === 'refusal') {
       out.push({
         type: 'refusal',
         refusal: c.refusal,
-        ...c.providerData,
+        ...getProviderDataWithoutReservedKeys(c.providerData, [
+          'type',
+          'refusal',
+        ]),
       });
     } else if (c.type === 'audio' || c.type === 'image') {
       // ignoring audio as it is handled on the assistant message level
@@ -67,7 +72,11 @@ export function extractAllUserContent(
   const out: ChatCompletionContentPart[] = [];
   for (const c of content) {
     if (c.type === 'input_text') {
-      out.push({ type: 'text', text: c.text, ...c.providerData });
+      out.push({
+        type: 'text',
+        text: c.text,
+        ...getProviderDataWithoutReservedKeys(c.providerData, ['type', 'text']),
+      });
     } else if (c.type === 'input_image') {
       // The Chat Completions API only accepts image URLs. If we see a file reference we reject it
       // early so callers get an actionable error instead of a cryptic API response.
@@ -83,12 +92,19 @@ export function extractAllUserContent(
           `Only image URLs are supported for input_image: ${JSON.stringify(c)}`,
         );
       }
-      const { image_url, ...rest } = c.providerData || {};
+      const rest = getProviderDataWithoutReservedKeys(c.providerData, [
+        'type',
+        'image_url',
+      ]);
+      const imageUrl = getProviderDataWithoutReservedKeys(
+        c.providerData?.image_url,
+        ['url'],
+      );
       out.push({
         type: 'image_url',
         image_url: {
           url: imageSource,
-          ...image_url,
+          ...imageUrl,
         },
         ...rest,
       });
@@ -121,20 +137,31 @@ export function extractAllUserContent(
         file.filename = c.providerData.filename;
       }
 
-      const { filename: _filename, ...rest } = c.providerData || {};
+      const rest = getProviderDataWithoutReservedKeys(c.providerData, [
+        'type',
+        'file',
+        'filename',
+      ]);
       out.push({
         type: 'file',
         file,
         ...rest,
       });
     } else if (c.type === 'audio') {
-      const { input_audio, ...rest } = c.providerData || {};
+      const rest = getProviderDataWithoutReservedKeys(c.providerData, [
+        'type',
+        'input_audio',
+      ]);
+      const inputAudio = getProviderDataWithoutReservedKeys(
+        c.providerData?.input_audio,
+        ['data'],
+      );
       out.push({
         type: 'input_audio',
         input_audio: {
-          data: c.audio,
-          ...input_audio,
-        },
+          data: c.audio as string,
+          ...inputAudio,
+        } as ChatCompletionContentPartInputAudio['input_audio'],
         ...rest,
       });
     } else {
@@ -195,7 +222,12 @@ export function itemsToMessages(
         const assistant: ChatCompletionAssistantMessageParam = {
           role: 'assistant',
           content: extractAllAssistantContent(content),
-          ...providerData,
+          ...getProviderDataWithoutReservedKeys(providerData, [
+            'role',
+            'content',
+            'tool_calls',
+            'audio',
+          ]),
         };
 
         if (Array.isArray(content)) {
@@ -213,13 +245,19 @@ export function itemsToMessages(
         result.push({
           role,
           content: extractAllUserContent(content),
-          ...providerData,
+          ...getProviderDataWithoutReservedKeys(providerData, [
+            'role',
+            'content',
+          ]),
         });
       } else if (role === 'system') {
         result.push({
           role: 'system',
           content: content,
-          ...providerData,
+          ...getProviderDataWithoutReservedKeys(providerData, [
+            'role',
+            'content',
+          ]),
         });
       }
     } else if (item.type === 'reasoning') {
@@ -246,11 +284,21 @@ export function itemsToMessages(
             arguments: JSON.stringify({
               queries: fileSearch.providerData?.queries ?? [],
               status: fileSearch.status,
-              ...argumentData,
+              ...getProviderDataWithoutReservedKeys(argumentData, [
+                'queries',
+                'status',
+              ]),
             }),
-            ...remainingFunctionData,
+            ...getProviderDataWithoutReservedKeys(remainingFunctionData, [
+              'name',
+              'arguments',
+            ]),
           },
-          ...rest,
+          ...getProviderDataWithoutReservedKeys(rest, [
+            'id',
+            'type',
+            'function',
+          ]),
         });
         asst.tool_calls = toolCalls;
         continue;
@@ -276,16 +324,37 @@ export function itemsToMessages(
       const asst = ensureAssistantMessage();
       const toolCalls = asst.tool_calls ?? [];
       const funcCall = item;
+      const toolCallProviderData = getProviderDataWithoutReservedKeys(
+        funcCall.providerData,
+        ['id', 'type', 'function', 'role', 'content', 'tool_calls', 'audio'],
+      );
+      const functionProviderData = getProviderDataWithoutReservedKeys(
+        funcCall.providerData?.function,
+        ['name', 'arguments'],
+      );
       toolCalls.push({
         id: funcCall.callId,
         type: 'function',
         function: {
           name: funcCall.name,
           arguments: funcCall.arguments ?? '{}',
+          ...functionProviderData,
         },
+        ...toolCallProviderData,
       });
       asst.tool_calls = toolCalls;
-      Object.assign(asst, funcCall.providerData);
+      Object.assign(
+        asst,
+        getProviderDataWithoutReservedKeys(funcCall.providerData, [
+          'role',
+          'content',
+          'tool_calls',
+          'audio',
+          'id',
+          'type',
+          'function',
+        ]),
+      );
     } else if (item.type === 'function_call_result') {
       flushAssistantMessage();
       const funcOutput = item;
@@ -295,7 +364,11 @@ export function itemsToMessages(
         role: 'tool',
         tool_call_id: funcOutput.callId,
         content: toolContent,
-        ...funcOutput.providerData,
+        ...getProviderDataWithoutReservedKeys(funcOutput.providerData, [
+          'role',
+          'tool_call_id',
+          'content',
+        ]),
       });
     } else if (item.type === 'unknown') {
       result.push({
diff --git a/packages/agents-openai/src/utils/providerData.ts b/packages/agents-openai/src/utils/providerData.ts
index 6db93a2a4..7efe7d592 100644
--- a/packages/agents-openai/src/utils/providerData.ts
+++ b/packages/agents-openai/src/utils/providerData.ts
@@ -19,3 +19,29 @@ export function camelOrSnakeToSnakeCase<
   }
   return result;
 }
+
+function isRecord(value: unknown): value is Record<string, any> {
+  return typeof value === 'object' && value !== null && !Array.isArray(value);
+}
+
+/**
+ * Returns providerData with reserved top-level keys removed.
+ */
+export function getProviderDataWithoutReservedKeys(
+  value: unknown,
+  reservedKeys: readonly string[],
+): Record<string, any> {
+  if (!isRecord(value)) {
+    return {};
+  }
+
+  const reserved = new Set(reservedKeys);
+  const result: Record<string, any> = {};
+  for (const [key, entry] of Object.entries(value)) {
+    if (reserved.has(key)) {
+      continue;
+    }
+    result[key] = entry;
+  }
+  return result;
+}
diff --git a/packages/agents-openai/test/openaiChatCompletionsConverter.test.ts b/packages/agents-openai/test/openaiChatCompletionsConverter.test.ts
index ba768f934..c08cd8ba9 100644
--- a/packages/agents-openai/test/openaiChatCompletionsConverter.test.ts
+++ b/packages/agents-openai/test/openaiChatCompletionsConverter.test.ts
@@ -82,6 +82,56 @@ describe('content extraction helpers', () => {
     ]);
   });
 
+  test('extractAllUserContent preserves extras but ignores reserved providerData fields', () => {
+    const userContent: protocol.UserMessageItem['content'] = [
+      {
+        type: 'input_text',
+        text: 'u1',
+        providerData: {
+          type: 'override_type',
+          text: 'override_text',
+          extraText: true,
+        },
+      },
+      {
+        type: 'input_image',
+        image: 'http://img',
+        providerData: {
+          type: 'override_image',
+          image_url: { url: 'http://override', detail: 'high' },
+          extraImage: true,
+        },
+      },
+      {
+        type: 'audio',
+        audio: 'abc',
+        providerData: {
+          type: 'override_audio',
+          input_audio: { data: 'override', foo: 'bar' },
+          extraAudio: true,
+        },
+      },
+    ];
+
+    expect(extractAllUserContent(userContent)).toEqual([
+      {
+        type: 'text',
+        text: 'u1',
+        extraText: true,
+      },
+      {
+        type: 'image_url',
+        image_url: { url: 'http://img', detail: 'high' },
+        extraImage: true,
+      },
+      {
+        type: 'input_audio',
+        input_audio: { data: 'abc', foo: 'bar' },
+        extraAudio: true,
+      },
+    ]);
+  });
+
   test('extractAllUserContent throws on unknown entry', () => {
     const bad: any = [{ type: 'bad' }];
     expect(() => extractAllUserContent(bad)).toThrow();
@@ -460,6 +510,86 @@ describe('itemsToMessages', () => {
     expect((msgs[0] as any).from_first).toBe(true);
     expect((msgs[0] as any).from_second).toBe(true);
   });
+
+  test('preserves extra providerData without letting it overwrite canonical envelopes', () => {
+    const items: protocol.ModelItem[] = [
+      {
+        type: 'message',
+        role: 'user',
+        content: 'keep-user',
+        providerData: {
+          role: 'assistant',
+          content: 'override-user',
+          customUser: true,
+        },
+      } as protocol.UserMessageItem,
+      {
+        type: 'function_call',
+        id: '1',
+        callId: 'call1',
+        name: 'f',
+        arguments: '{}',
+        status: 'completed',
+        providerData: {
+          role: 'tool',
+          content: 'override-assistant',
+          tool_calls: [{ id: 'override' }],
+          type: 'function',
+          function: {
+            name: 'override_name',
+            arguments: '{"override":true}',
+            extraNested: true,
+          },
+          customAssistant: true,
+        },
+      } as protocol.FunctionCallItem,
+      {
+        type: 'function_call_result',
+        id: '2',
+        name: 'f',
+        callId: 'call1',
+        status: 'completed',
+        output: 'result',
+        providerData: {
+          role: 'assistant',
+          tool_call_id: 'override-call',
+          content: 'override-tool',
+          extraTool: true,
+        },
+      } as protocol.FunctionCallResultItem,
+    ];
+
+    expect(itemsToMessages(items)).toEqual([
+      {
+        role: 'user',
+        content: 'keep-user',
+        customUser: true,
+      },
+      {
+        role: 'assistant',
+        content: null,
+        tool_calls: [
+          {
+            id: 'call1',
+            type: 'function',
+            function: {
+              name: 'f',
+              arguments: '{}',
+              extraNested: true,
+            },
+            customAssistant: true,
+          },
+        ],
+        customAssistant: true,
+      },
+      {
+        role: 'tool',
+        tool_call_id: 'call1',
+        content: 'result',
+        extraTool: true,
+      },
+    ]);
+  });
 });
 
 describe('tool helpers', () => {
diff --git a/packages/agents-openai/test/utils/providerData.test.ts b/packages/agents-openai/test/utils/providerData.test.ts
index 3abf2ee02..cf3c548c0 100644
--- a/packages/agents-openai/test/utils/providerData.test.ts
+++ b/packages/agents-openai/test/utils/providerData.test.ts
@@ -1,5 +1,8 @@
 import { describe, it, expect } from 'vitest';
-import { camelOrSnakeToSnakeCase } from '../../src/utils/providerData';
+import {
+  camelOrSnakeToSnakeCase,
+  getProviderDataWithoutReservedKeys,
+} from '../../src/utils/providerData';
 
 describe('camelToSnakeCase', () => {
   it('converts flat camelCase keys to snake_case', () => {
@@ -68,3 +71,22 @@ describe('camelToSnakeCase', () => {
     });
   });
 });
+
+describe('reserved providerData filtering', () => {
+  it('removes reserved keys without touching other values', () => {
+    expect(
+      getProviderDataWithoutReservedKeys(
+        {
+          role: 'assistant',
+          content: 'override',
+          customFlag: true,
+          nested: { role: 'keep nested values' },
+        },
+        ['role', 'content'],
+      ),
+    ).toEqual({
+      customFlag: true,
+      nested: { role: 'keep nested values' },
+    });
+  });
+});
PATCH

echo "Patch applied."
