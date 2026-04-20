#!/bin/bash
set -e

git config --global user.email "task@task.com"
git config --global user.name "Task"

cd /workspace/continue_dev

PATCH='From 7968dd106982ff5286df9a3915247d327b8a01e9 Mon Sep 17 00:00:00 2001
From: Dallin Romney <dallinromney@gmail.com>
Date: Wed, 25 Mar 2026 16:57:33 -0700
Subject: [PATCH] feat(openrouter): send HTTP-Referer and X-Title headers to identify app

* feat(openrouter): send HTTP-Referer and X-Title headers to identify app

Adds `HTTP-Referer: https://www.continue.dev/` and `X-Title: Continue`
headers to all OpenRouter API requests, as recommended by the OpenRouter
docs. This lets OpenRouter attribute requests to Continue in their
dashboard and App Showcase.

Headers are injected via both `requestOptions.headers` (for SDK-based
requests) and `getHeaders()` (for direct fetch calls). User-configured
headers take precedence.

Closes #4049

* refactor: remove redundant getHeaders() override

The OPENROUTER_HEADERS are already injected via requestOptions.headers
in the constructor. Since fetchwithRequestOptions merges
requestOptions.headers into all requests (including direct fetch calls
like fimStream and rerank), the getHeaders() override was redundant.
---
 packages/openai-adapters/src/apis/OpenRouter.ts | 12 ++++++++++++
 1 file changed, 12 insertions(+)

diff --git a/packages/openai-adapters/src/apis/OpenRouter.ts b/packages/openai-adapters/src/apis/OpenRouter.ts
index 3e70f7f885e..d6227affb2e 100644
--- a/packages/openai-adapters/src/apis/OpenRouter.ts
+++ b/packages/openai-adapters/src/apis/OpenRouter.ts
@@ -8,11 +8,23 @@ export interface OpenRouterConfig extends OpenAIConfig {
   cachingStrategy?: import("./AnthropicCachingStrategies.js").CachingStrategyName;
 }

+const OPENROUTER_HEADERS: Record<string, string> = {
+  "HTTP-Referer": "https://www.continue.dev/",
+  "X-Title": "Continue",
+};
+
 export class OpenRouterApi extends OpenAIApi {
   constructor(config: OpenRouterConfig) {
     super({
       ...config,
       apiBase: config.apiBase ?? "https://openrouter.ai/api/v1/",
+      requestOptions: {
+        ...config.requestOptions,
+        headers: {
+          ...OPENROUTER_HEADERS,
+          ...config.requestOptions?.headers,
+        },
+      },
     });
   }
'

echo "$PATCH" | git am

cd /workspace/continue_dev/packages/openai-adapters && npm run build