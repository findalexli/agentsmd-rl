#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if the fix is already applied
if grep -q 'Response\.redirect' js/_website/functions/_shared.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/_website/functions/_shared.ts b/js/_website/functions/_shared.ts
index 3cf52699bd5..ff17d5a8948 100644
--- a/js/_website/functions/_shared.ts
+++ b/js/_website/functions/_shared.ts
@@ -23,41 +23,21 @@ function isLLMRequest(request: Request): boolean {
 	return AI_UA_PATTERNS.some((re) => re.test(ua));
 }

-const MARKDOWN_HEADERS = {
-	"Content-Type": "text/markdown; charset=utf-8",
-	"X-Robots-Tag": "noindex"
-};
-
 export async function serveDocMarkdown(context: any): Promise<Response> {
 	const { request, params, next } = context;
 	if (!isLLMRequest(request)) return next();

-	const origin = new URL(request.url).origin;
-	try {
-		const res = await fetch(`${origin}/api/markdown/${params.doc}`);
-		if (res.ok) {
-			const data: any = await res.json();
-			if (data.markdown) {
-				return new Response(data.markdown, { headers: MARKDOWN_HEADERS });
-			}
-		}
-	} catch {}
-	return next();
+	const url = new URL(request.url);
+	return Response.redirect(`${url.origin}/api/markdown/${params.doc}`, 302);
 }

 export async function serveGuideMarkdown(context: any): Promise<Response> {
 	const { request, params, next } = context;
 	if (!isLLMRequest(request)) return next();

-	const origin = new URL(request.url).origin;
-	try {
-		const res = await fetch(`${origin}/api/markdown/guide/${params.guide}`);
-		if (res.ok) {
-			const data: any = await res.json();
-			if (data.markdown) {
-				return new Response(data.markdown, { headers: MARKDOWN_HEADERS });
-			}
-		}
-	} catch {}
-	return next();
+	const url = new URL(request.url);
+	return Response.redirect(
+		`${url.origin}/api/markdown/guide/${params.guide}`,
+		302
+	);
 }

PATCH

echo "Patch applied successfully."
