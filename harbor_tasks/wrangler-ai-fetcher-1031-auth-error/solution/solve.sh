#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/workers-sdk
cd "$REPO"

# Idempotency: if the distinctive 1031 error message is already present, skip.
if grep -q "Authentication error (code 1031)" packages/wrangler/src/ai/fetcher.ts 2>/dev/null; then
    echo "solve.sh: gold patch already applied; nothing to do"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/ai-auth-error-message.md b/.changeset/ai-auth-error-message.md
new file mode 100644
index 0000000000..892135bc38
--- /dev/null
+++ b/.changeset/ai-auth-error-message.md
@@ -0,0 +1,7 @@
+---
+"wrangler": patch
+---
+
+Log a helpful error message when AI binding requests fail with a 403 authentication error
+
+Previously, when the AI proxy token expired during a long session, users received an unhelpful 403 error. Now, wrangler detects error code 1031 and suggests running `wrangler login` to refresh the token.
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

echo "solve.sh: gold patch applied"
