#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Check if already applied
if grep -q 'createWebhookInFlightLimiter' extensions/synology-chat/src/webhook-handler.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/extensions/synology-chat/src/test-http-utils.ts b/extensions/synology-chat/src/test-http-utils.ts
index b3125c6cce96..b7a1723dbc1e 100644
--- a/extensions/synology-chat/src/test-http-utils.ts
+++ b/extensions/synology-chat/src/test-http-utils.ts
@@ -55,6 +55,16 @@ export function makeRes(): ServerResponse & { _status: number; _body: string } {
       res._body = body ?? "";
     },
   } as unknown as ServerResponse & { _status: number; _body: string };
+  Object.defineProperty(res, "statusCode", {
+    configurable: true,
+    enumerable: true,
+    get() {
+      return res._status;
+    },
+    set(value: number) {
+      res._status = value;
+    },
+  });
   return res;
 }

diff --git a/extensions/synology-chat/src/webhook-handler.test.ts b/extensions/synology-chat/src/webhook-handler.test.ts
index 7848e9725e36..f111da0c139f 100644
--- a/extensions/synology-chat/src/webhook-handler.test.ts
+++ b/extensions/synology-chat/src/webhook-handler.test.ts
@@ -160,6 +160,33 @@ describe("createWebhookHandler", () => {
     }
   });

+  it("rejects excess concurrent pre-auth body reads from the same remote IP", async () => {
+    const handler = createWebhookHandler({
+      account: makeAccount({ accountId: "preauth-inflight-test-" + Date.now() }),
+      deliver: vi.fn(),
+      log,
+    });
+
+    const requests = Array.from({ length: 12 }, () => {
+      const req = makeStalledReq("POST");
+      (req.socket as { remoteAddress?: string }).remoteAddress = "203.0.113.10";
+      return req;
+    });
+    const responses = requests.map(() => makeRes());
+    const runs = requests.map((req, index) => handler(req, responses[index]));
+
+    await new Promise((resolve) => setTimeout(resolve, 0));
+
+    // Default maxInFlightPerKey is 8; 12 total requests leaves 4 rejected with 429.
+    expect(responses.filter((res) => res._status === 0)).toHaveLength(8);
+    expect(responses.filter((res) => res._status === 429)).toHaveLength(4);
+
+    for (const req of requests) {
+      req.emit("end");
+    }
+    await Promise.all(runs);
+  });
+
   it("returns 401 for invalid token", async () => {
     const handler = createWebhookHandler({
       account: makeAccount(),
diff --git a/extensions/synology-chat/src/webhook-handler.ts b/extensions/synology-chat/src/webhook-handler.ts
index 2e4a9a509893..8f737128251d 100644
--- a/extensions/synology-chat/src/webhook-handler.ts
+++ b/extensions/synology-chat/src/webhook-handler.ts
@@ -6,6 +6,8 @@
 import type { IncomingMessage, ServerResponse } from "node:http";
 import * as querystring from "node:querystring";
 import {
+  beginWebhookRequestPipelineOrReject,
+  createWebhookInFlightLimiter,
   isRequestBodyLimitError,
   readRequestBodyWithLimit,
   requestBodyErrorToText,
@@ -17,6 +19,7 @@ import type { SynologyWebhookPayload, ResolvedSynologyChatAccount } from "./type
 // One rate limiter per account, created lazily
 const rateLimiters = new Map<string, RateLimiter>();
 const invalidTokenRateLimiters = new Map<string, InvalidTokenRateLimiter>();
+const webhookInFlightLimiter = createWebhookInFlightLimiter();
 const PREAUTH_MAX_BODY_BYTES = 64 * 1024;
 const PREAUTH_BODY_TIMEOUT_MS = 5_000;
 const PREAUTH_MAX_REQUESTS_PER_MINUTE = 10;
@@ -118,6 +121,7 @@ export function clearSynologyWebhookRateLimiterStateForTest(): void {
     limiter.clear();
   }
   invalidTokenRateLimiters.clear();
+  webhookInFlightLimiter.clear();
 }

 export function getSynologyWebhookRateLimiterCountForTest(): number {
@@ -128,6 +132,14 @@ function getSynologyWebhookInvalidTokenRateLimitKey(req: IncomingMessage): strin
   return req.socket?.remoteAddress ?? "unknown";
 }

+function getSynologyWebhookInFlightKey(account: ResolvedSynologyChatAccount): string {
+  // Synology webhook ingress is typically a single upstream per account, and this
+  // handler does not have a trusted-proxy-aware client IP config. Keep the shared
+  // pre-auth concurrency budget scoped per account instead of keying on a fragile
+  // remoteAddress value that can collapse behind proxies or to "unknown".
+  return account.accountId;
+}
+
 /** Read the full request body as a string. */
 async function readBody(req: IncomingMessage): Promise<
   | { ok: true; body: string }
@@ -564,14 +576,30 @@ export function createWebhookHandler(deps: WebhookHandlerDeps) {
       respondJson(res, 405, { error: "Method not allowed" });
       return;
     }
-    const authorized = await parseAndAuthorizeSynologyWebhook({
+    const requestLifecycle = beginWebhookRequestPipelineOrReject({
       req,
       res,
-      account,
-      invalidTokenRateLimiter,
-      rateLimiter,
-      log,
+      inFlightLimiter: webhookInFlightLimiter,
+      inFlightKey: getSynologyWebhookInFlightKey(account),
     });
+    if (!requestLifecycle.ok) {
+      return;
+    }
+
+    let authorized: Awaited<ReturnType<typeof parseAndAuthorizeSynologyWebhook>>;
+    try {
+      authorized = await parseAndAuthorizeSynologyWebhook({
+        req,
+        res,
+        account,
+        invalidTokenRateLimiter,
+        rateLimiter,
+        log,
+      });
+    } finally {
+      // Only bound the pre-auth request pipeline; async reply delivery is outside webhook ingress.
+      requestLifecycle.release();
+    }
     if (!authorized.ok) {
       return;
     }

PATCH

echo "Patch applied successfully."
