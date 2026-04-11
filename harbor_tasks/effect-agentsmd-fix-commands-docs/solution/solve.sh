#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

# Idempotent: skip if already applied
if grep -q '## Learning about "effect" v4' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.gitignore b/.gitignore
index 711fc014536..8682277c305 100644
--- a/.gitignore
+++ b/.gitignore
@@ -11,3 +11,4 @@ scratchpad/
 .idea/
 .env*
 .lalph/
+.repos/
diff --git a/AGENTS.md b/AGENTS.md
index 20ae79da349..3d016f4880b 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -17,7 +17,7 @@ This is the Effect library repository, focusing on functional programming patter
 ### Mandatory Validation Steps

 - Run `pnpm lint-fix` after editing files
-- Always run tests after making changes: `pnpm test <test_file.ts>`
+- Always run tests after making changes: `pnpm test run <test_file.ts>`
 - Run type checking: `pnpm check`
   - If type checking continues to fail, run `pnpm clean` to clear caches, then re-run `pnpm check`
 - Build the project: `pnpm build`
@@ -40,7 +40,7 @@ The `index.ts` files are automatically generated. Do not manually edit them. Use

 If you need to run some code for testing or debugging purposes, create a new
 file in the `scratchpad/` directory at the root of the repository. You can then
-run the file with `node scratchpad/your-file.ts`.
+run the file with `tsx scratchpad/your-file.ts`.

 Make sure to delete the file after you are done testing.

@@ -63,3 +63,10 @@ functionality to follow established patterns.

 Before writing tests, look at existing tests in the codebase for similar
 functionality to follow established patterns.
+
+## Learning about "effect" v4
+
+If you need to learn more about the new version of effect (version 4), you can
+access the repository here:
+
+\`.repos/effect-v4\`
diff --git a/eslint.config.mjs b/eslint.config.mjs
index c05998a035c..ff0e6bdf969 100644
--- a/eslint.config.mjs
+++ b/eslint.config.mjs
@@ -20,7 +20,14 @@ const compat = new FlatCompat({

 export default [
   {
-    ignores: ["**/dist", "**/build", "**/docs", "**/*.md"]
+    ignores: [
+      "**/dist",
+      "**/build",
+      "**/docs",
+      "**/.repos/**",
+      "**/.lalph/**",
+      "**/*.md"
+    ]
   },
   ...compat.extends(
     "eslint:recommended",
@@ -65,7 +72,8 @@ export default [
       "no-restricted-syntax": [
         "error",
         {
-          selector: "CallExpression[callee.property.name='push'] > SpreadElement.arguments",
+          selector:
+            "CallExpression[callee.property.name='push'] > SpreadElement.arguments",
           message: "Do not use spread arguments in Array.push"
         }
       ],
@@ -145,11 +153,7 @@ export default [
       "@effect/no-import-from-barrel-package": [
         "error",
         {
-          packageNames: [
-            "effect",
-            "@effect/platform",
-            "@effect/sql"
-          ]
+          packageNames: ["effect", "@effect/platform", "@effect/sql"]
         }
       ]
     }
diff --git a/packages/ai/ai/src/AiError.ts b/packages/ai/ai/src/AiError.ts
index 80ad483b65d..a5ba22f4ab4 100644
--- a/packages/ai/ai/src/AiError.ts
+++ b/packages/ai/ai/src/AiError.ts
@@ -162,7 +162,8 @@ export const HttpRequestDetails = Schema.Struct({
  * @example
  * \`\`\`ts
  * import { AiError } from "@effect/ai"
- * import { Effect } from "effect"
+ * import * as Effect from "effect/Effect"
+ * import * as Option from "effect/Option"
  *
  * const handleNetworkError = Effect.gen(function* () {
  *   const error = new AiError.HttpRequestError({
@@ -466,9 +467,9 @@ export class HttpResponseError extends Schema.TaggedError<HttpResponseError>(
  * @example
  * \`\`\`ts
  * import { AiError } from "@effect/ai"
- * import { Effect } from "effect"
+ * import * as Effect from "effect/Effect"
  *
- * const validateInput = (data: unknown) =>
+ * const validateInput = (data: unknown): Effect.Effect<string, AiError.MalformedInput> =>
  *   typeof data === "string" && data.length > 0
  *     ? Effect.succeed(data)
  *     : Effect.fail(new AiError.MalformedInput({
diff --git a/packages/ai/ai/src/Chat.ts b/packages/ai/ai/src/Chat.ts
index b6a3b250c9d..656944a623c 100644
--- a/packages/ai/ai/src/Chat.ts
+++ b/packages/ai/ai/src/Chat.ts
@@ -78,10 +78,10 @@ import type * as Tool from "./Tool.js"
  * @example
  * \`\`\`ts
  * import { Chat } from "@effect/ai"
- * import { Effect } from "effect"
+ * import * as Effect from "effect/Effect"
  *
  * const useChat = Effect.gen(function* () {
- *   const chat = yield* Chat
+ *   const chat = yield* Chat.Chat
  *   const response = yield* chat.generateText({
  *     prompt: "Explain quantum computing in simple terms"
  *   })
diff --git a/packages/ai/ai/src/EmbeddingModel.ts b/packages/ai/ai/src/EmbeddingModel.ts
index acf4f67f4ee..804a7b0584 100644
--- a/packages/ai/ai/src/EmbeddingModel.ts
+++ b/packages/ai/ai/src/EmbeddingModel.ts
@@ -69,10 +69,17 @@ import * as AiError from "./AiError.js"
  * @example
  * \`\`\`ts
  * import { EmbeddingModel } from "@effect/ai"
- * import { Effect } from "effect"
+ * import * as Effect from "effect/Effect"
+ *
+ * const cosineSimilarity = (a: ReadonlyArray<number>, b: ReadonlyArray<number>): number => {
+ *   const dot = a.reduce((sum, ai, i) => sum + ai * (b[i] ?? 0), 0)
+ *   const normA = Math.sqrt(a.reduce((sum, ai) => sum + ai * ai, 0))
+ *   const normB = Math.sqrt(b.reduce((sum, bi) => sum + bi * bi, 0))
+ *   return normA === 0 || normB === 0 ? 0 : dot / (normA * normB)
+ * }
  *
  * const useEmbeddings = Effect.gen(function* () {
- *   const embedder = yield* EmbeddingModel
+ *   const embedder = yield* EmbeddingModel.EmbeddingModel
  *
  *   const documentVector = yield* embedder.embed("This is a sample document")
  *   const queryVector = yield* embedder.embed("sample query")
diff --git a/packages/ai/ai/src/LanguageModel.ts b/packages/ai/ai/src/LanguageModel.ts
index c217eb2d204..c95c460bde1 100644
--- a/packages/ai/ai/src/LanguageModel.ts
+++ b/packages/ai/ai/src/LanguageModel.ts
@@ -83,10 +83,10 @@ import * as Toolkit from "./Toolkit.js"
  * @example
  * \`\`\`ts
  * import { LanguageModel } from "@effect/ai"
- * import { Effect } from "effect"
+ * import * as Effect from "effect/Effect"
  *
  * const useLanguageModel = Effect.gen(function* () {
- *   const model = yield* LanguageModel
+ *   const model = yield* LanguageModel.LanguageModel
  *   const response = yield* model.generateText({
  *     prompt: "What is machine learning?"
  *   })
diff --git a/packages/ai/ai/src/Telemetry.ts b/packages/ai/ai/src/Telemetry.ts
index 007928a2b68..d92f94042fb 100644
--- a/packages/ai/ai/src/Telemetry.ts
+++ b/packages/ai/ai/src/Telemetry.ts
@@ -519,11 +519,13 @@ export interface SpanTransformer {
  * @example
  * \`\`\`ts
  * import { Telemetry } from "@effect/ai"
- * import { Context, Effect } from "effect"
+ * import * as Effect from "effect/Effect"
+ *
+ * declare const myAIOperation: Effect.Effect<void>
  *
  * // Create a custom span transformer
  * const loggingTransformer: Telemetry.SpanTransformer = (options) => {
- *   console.log(\`AI request completed: \${options.model}\`)
+ *   console.log(\`AI request completed: \${options.response.length} part(s)\`)
  *   options.response.forEach((part, index) => {
  *     console.log(\`Part \${index}: \${part.type}\`)
  *   })
diff --git a/packages/effect/src/Schema.ts b/packages/effect/src/Schema.ts
index db74f0387a6..08779a018d5 100644
--- a/packages/effect/src/Schema.ts
+++ b/packages/effect/src/Schema.ts
@@ -5415,7 +5415,7 @@ export type JsonNumberSchemaId = typeof JsonNumberSchemaId
  * import * as assert from "node:assert"
  * import * as Schema from "effect/Schema"
  *
- * const is = Schema.is(S.JsonNumber)
+ * const is = Schema.is(Schema.JsonNumber)
  *
  * assert.deepStrictEqual(is(42), true)
  * assert.deepStrictEqual(is(Number.NaN), false)
diff --git a/packages/platform-node/src/NodeStream.ts b/packages/platform-node/src/NodeStream.ts
index c1b4eb818eb..0f143b8cfc1 100644
--- a/packages/platform-node/src/NodeStream.ts
+++ b/packages/platform-node/src/NodeStream.ts
@@ -3,6 +3,7 @@
  */

 /**
- * @category models
+ * @since 1.0.0
+ * @category re-exports
  */
 export * from "@effect/platform-node-shared/NodeStream"
diff --git a/packages/sql/tsconfig.test.json b/packages/sql/tsconfig.test.json
index 55d48cec532..88df34fca95 100644
--- a/packages/sql/tsconfig.test.json
+++ b/packages/sql/tsconfig.test.json
@@ -7,6 +7,7 @@
   ],
   "compilerOptions": {
     "tsBuildInfoFile": ".tsbuildinfo/test.tsbuildinfo",
-    "rootDir": "test"
+    "rootDir": "test",
+    "outDir": "build/test"
   }
 }
diff --git a/scripts/worktree-setup.sh b/scripts/worktree-setup.sh
index bd7d455c509..8b5740618e9 100755
--- a/scripts/worktree-setup.sh
+++ b/scripts/worktree-setup.sh
@@ -7,13 +7,3 @@ pnpm install

 # setup repositories
 git clone --depth 1 https://github.com/effect-ts/effect-smol.git .repos/effect-v4
-
-cat << EOF >> AGENTS.md
-
-## Learning about "effect" v4
-
-If you need to learn more about the new version of effect (version 4), you can
-access the repository here:
-
-\`.repos/effect-v4\`
-EOF

PATCH

echo "Patch applied successfully."
