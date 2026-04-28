#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gemini-skills

# Idempotency guard
if grep -qF "description: Use this skill when building applications with Gemini models, Gemin" "skills/gemini-api-dev/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/gemini-api-dev/SKILL.md b/skills/gemini-api-dev/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: gemini-api-dev
-description: Use this skill when building applications with Gemini models, Gemini API, working with multimodal content (text, images, audio, video), implementing function calling, using structured outputs, or needing current model specifications. Covers SDK usage (google-genai for Python, @google/genai for JavaScript/TypeScript), model selection, and API capabilities.
+description: Use this skill when building applications with Gemini models, Gemini API, working with multimodal content (text, images, audio, video), implementing function calling, using structured outputs, or needing current model specifications. Covers SDK usage (google-genai for Python, @google/genai for JavaScript/TypeScript, com.google.genai:google-genai for Java, google.golang.org/genai for Go), model selection, and API capabilities.
 ---
 
 # Gemini API Development Skill
@@ -31,6 +31,21 @@ The Gemini API provides access to Google's most advanced AI models. Key capabili
 - **Python**: `google-genai` install with `pip install google-genai`
 - **JavaScript/TypeScript**: `@google/genai` install with `npm install @google/genai`
 - **Go**: `google.golang.org/genai` install with `go get google.golang.org/genai`
+- **Java**:
+  - groupId: `com.google.genai`, artifactId: `google-genai`
+  - Latest version can be found here: https://central.sonatype.com/artifact/com.google.genai/google-genai/versions (let's call it `LAST_VERSION`) 
+  - Install in `build.gradle`:
+    ```
+    implementation("com.google.genai:google-genai:${LAST_VERSION}")
+    ```
+  - Install Maven dependency in `pom.xml`:
+    ```
+    <dependency>
+	    <groupId>com.google.genai</groupId>
+	    <artifactId>google-genai</artifactId>
+	    <version>${LAST_VERSION}</version>
+	</dependency>
+    ```
 
 > [!WARNING]
 > Legacy SDKs `google-generativeai` (Python) and `@google/generative-ai` (JS) are deprecated. Migrate to the new SDKs above urgently by following the Migration Guide.
@@ -88,6 +103,26 @@ func main() {
 }
 ```
 
+### Java
+
+```java
+import com.google.genai.Client;
+import com.google.genai.types.GenerateContentResponse;
+
+public class GenerateTextFromTextInput {
+  public static void main(String[] args) {
+    Client client = new Client();
+    GenerateContentResponse response =
+        client.models.generateContent(
+            "gemini-3-flash-preview",
+            "Explain quantum computing",
+            null);
+
+    System.out.println(response.text());
+  }
+}
+```
+
 ## API spec (source of truth)
 
 **Always use the latest REST API discovery spec as the source of truth for API definitions** (request/response schemas, parameters, methods). Fetch the spec when implementing or debugging API integration:
PATCH

echo "Gold patch applied."
