#!/bin/bash
set -e

cd /workspace/continue_repo

# Apply the gold patch
git apply --ignore-whitespace <<'PATCH'
diff --git a/core/llm/llms/Ollama.ts b/core/llm/llms/Ollama.ts
index 9473a50cd7e..95945f70841 100644
--- a/core/llm/llms/Ollama.ts
+++ b/core/llm/llms/Ollama.ts
@@ -162,12 +162,23 @@ class Ollama extends BaseLLM implements ModelInstaller {

   private fimSupported: boolean = false;
   private templateSupportsTools: boolean | undefined = undefined;
+  private modelInfoPromise: Promise<void> | undefined = undefined;
+  private explicitContextLength: boolean;
+
   constructor(options: LLMOptions) {
     super(options);
+    this.explicitContextLength = options.contextLength !== undefined;
+  }
+
+  private ensureModelInfo(): Promise<void> {
+    if (this.modelInfoPromise !== undefined) {
+      return this.modelInfoPromise;
+    }

-    if (options.model === "AUTODETECT") {
-      return;
+    if (this.model === "AUTODETECT") {
+      return Promise.resolve();
     }
+
     const headers: Record<string, string> = {
       "Content-Type": "application/json",
     };
@@ -176,7 +187,7 @@ class Ollama extends BaseLLM implements ModelInstaller {
       headers.Authorization = `Bearer ${this.apiKey}`;
     }

-    this.fetch(this.getEndpoint("api/show"), {
+    this.modelInfoPromise = this.fetch(this.getEndpoint("api/show"), {
       method: "POST",
       headers: headers,
       body: JSON.stringify({ name: this._getModel() }),
@@ -194,15 +205,16 @@ class Ollama extends BaseLLM implements ModelInstaller {
           const params = [];
           for (const line of body.parameters.split("\n")) {
             let parts = line.match(/^(\S+)\s+((?:".*")|\S+)$/);
-            if (parts.length < 2) {
+            if (!parts || parts.length < 2) {
               continue;
             }
             let key = parts[1];
             let value = parts[2];
             switch (key) {
               case "num_ctx":
-                this._contextLength =
-                  options.contextLength ?? Number.parseInt(value);
+                if (!this.explicitContextLength) {
+                  this._contextLength = Number.parseInt(value);
+                }
                 break;
               case "stop":
                 if (!this.completionOptions.stop) {
@@ -237,6 +249,8 @@ class Ollama extends BaseLLM implements ModelInstaller {
       .catch((e) => {
         // console.warn("Error calling the Ollama /api/show endpoint: ", e);
       });
+
+    return this.modelInfoPromise;
   }

   // Map of "continue model name" to Ollama actual model name
@@ -410,6 +424,7 @@ class Ollama extends BaseLLM implements ModelInstaller {
     signal: AbortSignal,
     options: CompletionOptions,
   ): AsyncGenerator<string> {
+    await this.ensureModelInfo();
     const headers: Record<string, string> = {
       "Content-Type": "application/json",
     };
@@ -488,6 +503,7 @@ class Ollama extends BaseLLM implements ModelInstaller {
     signal: AbortSignal,
     options: CompletionOptions,
   ): AsyncGenerator<ChatMessage> {
+    await this.ensureModelInfo();
     const ollamaMessages = this._reorderMessagesForToolCompat(
       messages.map(this._convertToOllamaMessage),
     );
@@ -654,6 +670,7 @@ class Ollama extends BaseLLM implements ModelInstaller {
     signal: AbortSignal,
     options: CompletionOptions,
   ): AsyncGenerator<string> {
+    await this.ensureModelInfo();
     const headers: Record<string, string> = {
       "Content-Type": "application/json",
     };
PATCH

echo "Patch applied successfully"