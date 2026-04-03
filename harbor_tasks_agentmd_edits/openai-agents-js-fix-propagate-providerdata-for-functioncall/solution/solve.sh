#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openai-agents-js

# Idempotent: skip if already applied
if grep -q 'Object.assign(asst, funcCall.providerData)' packages/agents-openai/src/openaiChatCompletionsConverter.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 8979bd865..26eb3ec3d 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -104,9 +104,9 @@

 1. Fork the repository and create a branch with a descriptive name (e.g., `fix/missing-error`, `feat/new-tool`).
 2. Ensure your branch is up to date with `main`.
-3. Make your changes, add or update tests, and ensure that:
+3. Make your changes, add or update tests, and ensure that the following succeeds:
    ```bash
-   pnpm build && pnpm test && pnpm lint
+   pnpm build && pnpm -r build-check && pnpm test && pnpm lint
    ```
 4. If applicable, generate a changeset (`pnpm changeset`).
  5. Make sure you have [Trufflehog](https://github.com/trufflesecurity/trufflehog) installed to ensure no secrets are accidentally committed.
diff --git a/packages/agents-openai/src/openaiChatCompletionsConverter.ts b/packages/agents-openai/src/openaiChatCompletionsConverter.ts
index cca63ae94..2a5d2bd33 100644
--- a/packages/agents-openai/src/openaiChatCompletionsConverter.ts
+++ b/packages/agents-openai/src/openaiChatCompletionsConverter.ts
@@ -284,6 +284,7 @@ export function itemsToMessages(
         },
       });
       asst.tool_calls = toolCalls;
+      Object.assign(asst, funcCall.providerData);
     } else if (item.type === 'function_call_result') {
       flushAssistantMessage();
       const funcOutput = item;

PATCH

echo "Patch applied successfully."
