#!/usr/bin/env bash
set -euo pipefail

cd /workspace/firebase-ios-sdk

# Idempotency guard
if grep -qF "- **`GenerativeModelSession.swift`**: Defines the `GenerativeModelSession` class" "FirebaseAI/Sources/AGENTS.md" && grep -qF "-   **`GenerationSchema+Gemini.swift`**: This file extends `GenerationSchema` to" "FirebaseAI/Sources/Extensions/Internal/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/FirebaseAI/Sources/AGENTS.md b/FirebaseAI/Sources/AGENTS.md
@@ -24,6 +24,7 @@ This directory contains the source code for the FirebaseAI library.
 - **`GenerativeAIRequest.swift`**: Defines the `GenerativeAIRequest` protocol for requests sent to the generative AI backend. It also defines `RequestOptions`.
 - **`GenerativeAIService.swift`**: Defines the `GenerativeAIService` struct, which is responsible for making requests to the generative AI backend. It handles things like authentication, URL construction, and response parsing.
 - **`GenerativeModel.swift`**: Defines the `GenerativeModel` class, which represents a remote multimodal model. It provides methods for generating content, counting tokens, and starting a chat via `startChat(history:)`, which returns a `Chat` instance.
+- **`GenerativeModelSession.swift`**: Defines the `GenerativeModelSession` class, which provides a simplified interface for single-turn interactions with a generative model. It's particularly useful for generating typed objects from a model's response using the `@Generable` macro, without the conversational turn-based structure of a `Chat`.
 - **`History.swift`**: Defines the `History` class, a thread-safe class for managing the chat history, used by the `Chat` class.
 - **`JSONValue.swift`**: Defines the `JSONValue` enum and `JSONObject` typealias for representing JSON values.
 - **`ModalityTokenCount.swift`**: Defines the `ModalityTokenCount` and `ContentModality` structs for representing token counting information for a single modality.
diff --git a/FirebaseAI/Sources/Extensions/Internal/AGENTS.md b/FirebaseAI/Sources/Extensions/Internal/AGENTS.md
@@ -0,0 +1,7 @@
+# Internal Extensions
+
+This directory contains internal extensions to data models and other types. These extensions provide functionality that is specific to the internal workings of the Firebase AI SDK and are not part of the public API.
+
+## Files
+
+-   **`GenerationSchema+Gemini.swift`**: This file extends `GenerationSchema` to provide a `toGeminiJSONSchema()` method. This method transforms the schema into a format that is compatible with the Gemini backend, including renaming properties like `x-order` to `propertyOrdering`. This file is conditionally compiled and is only available when `FoundationModels` can be imported.
PATCH

echo "Gold patch applied."
