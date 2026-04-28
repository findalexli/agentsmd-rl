#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workers-sdk

# Check if patch is already applied
if grep -q "const authError = body?.errors?.find" packages/wrangler/src/ai/fetcher.ts; then
	echo "Patch already applied, skipping."
	exit 0
fi

# Apply the full gold patch
git apply <<'PATCH'
diff --git a/packages/wrangler/src/__tests__/ai.local.test.ts b/packages/wrangler/src/__tests__/ai.local.test.ts
index 27cf75240b..a3d4d7cad1 100644
--- a/packages/wrangler/src/__tests__/ai.local.test.ts
+++ b/packages/wrangler/src/__tests__/ai.local.test.ts
@@ -4,6 +4,7 @@ import { Headers, Response } from "undici";
 import { afterEach, describe, it, vi } from "vitest";
 import { getAIFetcher } from "../ai/fetcher";
 import * as internal from "../cfetch/internal";
+import { logger } from "../logger";
 import * as user from "../user";

 const AIFetcher = getAIFetcher(COMPLIANCE_REGION_CONFIG_UNKNOWN);
@@ -68,5 +69,70 @@ describe("ai", () => {
 				});
 			});
 		});
+
+		describe("403 auth error handling", () => {
+			it("should log error on 403 with auth error code 1031", async ({
+				expect,
+			}) => {
+				vi.spyOn(user, "getAccountId").mockImplementation(async () => "123");
+				vi.spyOn(internal, "performApiFetch").mockImplementation(async () => {
+					return new Response(
+						JSON.stringify({
+							errors: [{ code: 1031, message: "Forbidden" }],
+						}),
+						{ status: 403 }
+					);
+				});
+				const errorSpy = vi.spyOn(logger, "error");
+
+				const resp = await AIFetcher(
+					new Request("http://internal.ai/ai/test/path", { method: "POST" })
+				);
+
+				expect(resp.status).toBe(403);
+				expect(errorSpy).toHaveBeenCalledWith(
+					"Authentication error (code 1031): Your API token may have expired or lacks the required permissions. Please refresh your token by running `wrangler login`."
+				);
+			});
+
+			it("should not log error on 403 without auth error code 1031", async ({
+				expect,
+			}) => {
+				vi.spyOn(user, "getAccountId").mockImplementation(async () => "123");
+				vi.spyOn(internal, "performApiFetch").mockImplementation(async () => {
+					return new Response(
+						JSON.stringify({
+							errors: [{ code: 9999, message: "Other error" }],
+						}),
+						{ status: 403 }
+					);
+				});
+				const errorSpy = vi.spyOn(logger, "error");
+
+				const resp = await AIFetcher(
+					new Request("http://internal.ai/ai/test/path", { method: "POST" })
+				);
+
+				expect(resp.status).toBe(403);
+				expect(errorSpy).not.toHaveBeenCalled();
+			});
+
+			it("should not throw on 403 with unparseable body", async ({
+				expect,
+			}) => {
+				vi.spyOn(user, "getAccountId").mockImplementation(async () => "123");
+				vi.spyOn(internal, "performApiFetch").mockImplementation(async () => {
+					return new Response("not json", { status: 403 });
+				});
+				const errorSpy = vi.spyOn(logger, "error");
+
+				const resp = await AIFetcher(
+					new Request("http://internal.ai/ai/test/path", { method: "POST" })
+				);
+
+				expect(resp.status).toBe(403);
+				expect(errorSpy).not.toHaveBeenCalled();
+			});
+		});
 	});
 });
diff --git a/packages/wrangler/src/ai/fetcher.ts b/packages/wrangler/src/ai/fetcher.ts
index c21563cd1b..a7201d0ca5 100644
--- a/packages/wrangler/src/ai/fetcher.ts
+++ b/packages/wrangler/src/ai/fetcher.ts
@@ -1,5 +1,6 @@
 import { Headers, Response } from "miniflare";
 import { performApiFetch } from "../cfetch";
+import { logger } from "../logger";
 import { getAccountId } from "../user";
 import type { ComplianceConfig } from "@cloudflare/workers-utils";
 import type { Request } from "miniflare";
@@ -34,6 +35,23 @@ export function getAIFetcher(complianceConfig: ComplianceConfig) {
 			}
 		);

+		if (res.status === 403) {
+			try {
+				const clonedRes = res.clone();
+				const body = (await clonedRes.json()) as {
+					errors?: Array<{ code?: number; message?: string }>;
+				};
+				const authError = body?.errors?.find((e) => e.code === 1031);
+				if (authError) {
+					logger.error(
+						"Authentication error (code 1031): Your API token may have expired or lacks the required permissions. Please refresh your token by running `wrangler login`."
+					);
+				}
+			} catch {
+				// If we can't parse the response body, fall through to return the original response
+			}
+		}
+
 		const respHeaders = new Headers(res.headers);
 		respHeaders.delete("Host");
 		respHeaders.delete("Content-Length");
PATCH

# Create the changeset file
mkdir -p .changeset
cat > .changeset/ai-auth-error-message.md <<'CHANGESET'
---
"wrangler": patch
---

Log a helpful error message when AI binding requests fail with a 403 authentication error

Previously, when the AI proxy token expired during a long session, users received an unhelpful 403 error. Now, wrangler detects error code 1031 and suggests running `wrangler login` to refresh the token.
CHANGESET

echo "Patch applied successfully."
