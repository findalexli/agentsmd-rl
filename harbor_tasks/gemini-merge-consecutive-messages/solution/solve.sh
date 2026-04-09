#!/bin/bash
set -e

cd /workspace/continue

# Apply the gold patch for Gemini consecutive message merging fix
cat <<'PATCH' | git apply -
diff --git a/core/llm/llms/Gemini.ts b/core/llm/llms/Gemini.ts
index 66766fbc812..fb080fb44f2 100644
--- a/core/llm/llms/Gemini.ts
+++ b/core/llm/llms/Gemini.ts
@@ -22,6 +22,7 @@ import {
   GeminiGenerationConfig,
   GeminiToolFunctionDeclaration,
   convertContinueToolToGeminiFunction,
+  mergeConsecutiveGeminiMessages,
 } from "./gemini-types";

 interface GeminiToolCallDelta extends ToolCallDelta {
@@ -326,6 +327,8 @@ class Gemini extends BaseLLM {
           };
         }),
     };
+
+    body.contents = mergeConsecutiveGeminiMessages(body.contents);
     if (options) {
       body.generationConfig = this.convertArgs(options);
     }
diff --git a/core/llm/llms/gemini-types.ts b/core/llm/llms/gemini-types.ts
index f1944930b37..8dde5a02f47 100644
--- a/core/llm/llms/gemini-types.ts
+++ b/core/llm/llms/gemini-types.ts
@@ -424,3 +424,27 @@ interface LogprobsResult {
 interface TopCandidates {
   candidates: Candidate[];
 }
+
+// Gemini requires strict user/model role alternation.
+export function mergeConsecutiveGeminiMessages(
+  contents: GeminiChatContent[],
+): GeminiChatContent[] {
+  if (contents.length === 0) {
+    return contents;
+  }
+
+  const merged: GeminiChatContent[] = [contents[0]];
+
+  for (let i = 1; i < contents.length; i++) {
+    const current = contents[i];
+    const previous = merged[merged.length - 1];
+
+    if (current.role === previous.role) {
+      previous.parts = [...previous.parts, ...current.parts];
+    } else {
+      merged.push(current);
+    }
+  }
+
+  return merged;
+}
diff --git a/packages/openai-adapters/src/apis/Gemini.test.ts b/packages/openai-adapters/src/apis/Gemini.test.ts
new file mode 100644
index 00000000000..3b47620bc71
--- /dev/null
+++ b/packages/openai-adapters/src/apis/Gemini.test.ts
@@ -0,0 +1,136 @@
+import { describe, expect, it } from "vitest";
+
+import { GeminiApi } from "./Gemini.js";
+
+describe("GeminiApi", () => {
+  const api = new GeminiApi({
+    provider: "gemini",
+    apiKey: "test-key",
+  });
+
+  describe("_convertBody merges consecutive same-role messages", () => {
+    it("merges consecutive tool responses into a single user turn", () => {
+      const result = api._convertBody(
+        {
+          model: "gemini-2.5-flash",
+          messages: [
+            { role: "user", content: "Use the tools" },
+            {
+              role: "assistant",
+              content: null,
+              tool_calls: [
+                {
+                  id: "call_1",
+                  type: "function" as const,
+                  function: { name: "tool_a", arguments: "{}" },
+                },
+                {
+                  id: "call_2",
+                  type: "function" as const,
+                  function: { name: "tool_b", arguments: "{}" },
+                },
+              ],
+            },
+            {
+              role: "tool" as const,
+              content: "result_a",
+              tool_call_id: "call_1",
+            },
+            {
+              role: "tool" as const,
+              content: "result_b",
+              tool_call_id: "call_2",
+            },
+          ],
+        },
+        false,
+        true,
+      );
+
+      // Should be: user, model(functionCalls), user(functionResponses merged)
+      expect(result.contents).toHaveLength(3);
+      expect(result.contents[0].role).toBe("user");
+      expect(result.contents[1].role).toBe("model");
+      expect(result.contents[2].role).toBe("user");
+      // Both function responses merged into one user turn
+      expect(result.contents[2].parts).toHaveLength(2);
+      expect(result.contents[2].parts[0]).toHaveProperty("functionResponse");
+      expect(result.contents[2].parts[1]).toHaveProperty("functionResponse");
+    });
+
+    it("merges tool responses with following user message", () => {
+      const result = api._convertBody(
+        {
+          model: "gemini-2.5-flash",
+          messages: [
+            { role: "user", content: "Use the tool" },
+            {
+              role: "assistant",
+              content: null,
+              tool_calls: [
+                {
+                  id: "call_1",
+                  type: "function" as const,
+                  function: { name: "tool_a", arguments: "{}" },
+                },
+              ],
+            },
+            {
+              role: "tool" as const,
+              content: "result_a",
+              tool_call_id: "call_1",
+            },
+            { role: "user", content: "Now do something else" },
+          ],
+        },
+        false,
+        true,
+      );
+
+      // tool response (user) + user message should merge
+      expect(result.contents).toHaveLength(3);
+      expect(result.contents[2].role).toBe("user");
+      expect(result.contents[2].parts).toHaveLength(2);
+    });
+
+    it("merges consecutive model messages", () => {
+      const result = api._convertBody(
+        {
+          model: "gemini-2.5-flash",
+          messages: [
+            { role: "user", content: "Hello" },
+            { role: "assistant", content: "First response" },
+            { role: "assistant", content: "Second response" },
+          ],
+        },
+        false,
+        true,
+      );
+
+      // Two assistant messages should merge into one model message
+      expect(result.contents).toHaveLength(2);
+      expect(result.contents[1].role).toBe("model");
+      expect(result.contents[1].parts).toHaveLength(2);
+    });
+
+    it("preserves already-alternating messages unchanged", () => {
+      const result = api._convertBody(
+        {
+          model: "gemini-2.5-flash",
+          messages: [
+            { role: "user", content: "Hello" },
+            { role: "assistant", content: "Hi there" },
+            { role: "user", content: "How are you?" },
+          ],
+        },
+        false,
+        true,
+      );
+
+      expect(result.contents).toHaveLength(3);
+      expect(result.contents[0].role).toBe("user");
+      expect(result.contents[1].role).toBe("model");
+      expect(result.contents[2].role).toBe("user");
+    });
+  });
+});
diff --git a/packages/openai-adapters/src/apis/Gemini.ts b/packages/openai-adapters/src/apis/Gemini.ts
index 87e2e398f31..f7298267849 100644
--- a/packages/openai-adapters/src/apis/Gemini.ts
+++ b/packages/openai-adapters/src/apis/Gemini.ts
@@ -32,6 +32,7 @@ import {
   GeminiChatContent,
   GeminiChatContentPart,
   GeminiToolFunctionDeclaration,
+  mergeConsecutiveGeminiMessages,
 } from "../util/gemini-types.js";
 import { safeParseArgs } from "../util/parseArgs.js";
 import {
@@ -144,7 +145,7 @@ export class GeminiApi implements BaseLlmApi {
       }
     });

-    const contents: (GeminiChatContent | null)[] = oaiBody.messages
+    const contents = oaiBody.messages
       .map((msg) => {
         if (msg.role === "system" && !isV1API) {
           return null; // Don't include system message in contents
@@ -234,12 +235,14 @@ export class GeminiApi implements BaseLlmApi {
               : msg.content.map(this._oaiPartToGeminiPart),
         };
       })
-      .filter((c) => c !== null);
+      .filter((c) => c !== null) as GeminiChatContent[];
+
+    const mergedContents = mergeConsecutiveGeminiMessages(contents);

     const sysMsg = oaiBody.messages.find((msg) => msg.role === "system");
     const finalBody: any = {
       generationConfig,
-      contents,
+      contents: mergedContents,
       // if there is a system message, reformat it for Gemini API
       ...(sysMsg &&
         !isV1API && {
diff --git a/packages/openai-adapters/src/util/gemini-types.ts b/packages/openai-adapters/src/util/gemini-types.ts
index c161987ffff..e4e3de92bbb 100644
--- a/packages/openai-adapters/src/util/gemini-types.ts
+++ b/packages/openai-adapters/src/util/gemini-types.ts
@@ -428,3 +428,27 @@ interface LogprobsResult {
 interface TopCandidates {
   candidates: Candidate[];
 }
+
+// Gemini requires strict user/model role alternation.
+export function mergeConsecutiveGeminiMessages(
+  contents: GeminiChatContent[],
+): GeminiChatContent[] {
+  if (contents.length === 0) {
+    return contents;
+  }
+
+  const merged: GeminiChatContent[] = [contents[0]];
+
+  for (let i = 1; i < contents.length; i++) {
+    const current = contents[i];
+    const previous = merged[merged.length - 1];
+
+    if (current.role === previous.role) {
+      previous.parts = [...previous.parts, ...current.parts];
+    } else {
+      merged.push(current);
+    }
+  }
+
+  return merged;
+}
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "mergeConsecutiveGeminiMessages" packages/openai-adapters/src/util/gemini-types.ts && echo "Patch applied successfully"
