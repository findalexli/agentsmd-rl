#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if the fix is already applied, skip
if grep -q 'text/markdown' js/_website/src/routes/api/markdown/\[doc\]/+server.ts 2>/dev/null; then
    echo "Fix already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/_website/src/lib/components/DocsCopyMarkdown.svelte b/js/_website/src/lib/components/DocsCopyMarkdown.svelte
index 0feb1161a65..7ef52213b22 100644
--- a/js/_website/src/lib/components/DocsCopyMarkdown.svelte
+++ b/js/_website/src/lib/components/DocsCopyMarkdown.svelte
@@ -43,8 +43,7 @@
 		try {
 			const response = await fetch(`/api/markdown/${doc_name}`);
 			if (response.ok) {
-				const data = await response.json();
-				return data.markdown || "";
+				return (await response.text()) || "";
 			}
 		} catch (error) {
 			console.error("Error fetching markdown:", error);
diff --git a/js/_website/src/routes/api/markdown/[doc]/+server.ts b/js/_website/src/routes/api/markdown/[doc]/+server.ts
index 2d9ad99c35f..93618fcf04b 100644
--- a/js/_website/src/routes/api/markdown/[doc]/+server.ts
+++ b/js/_website/src/routes/api/markdown/[doc]/+server.ts
@@ -1,4 +1,3 @@
-import { json } from "@sveltejs/kit";
 import { readFileSync } from "fs";
 import { resolve as pathResolve } from "path";
 import { svxToMarkdown } from "$lib/utils/svx-to-markdown";
@@ -6,6 +5,11 @@ import docs_json from "$lib/templates/docs.json";

 export const prerender = true;

+const MARKDOWN_HEADERS = {
+	"Content-Type": "text/markdown; charset=utf-8",
+	"X-Robots-Tag": "noindex"
+};
+
 export function entries() {
 	return docs_json.pages.gradio.flatMap((category) =>
 		category.pages.map((page) => ({ doc: page.name }))
@@ -28,7 +32,7 @@ export async function GET({ params }) {
 	}

 	if (!svxPath) {
-		return json({ markdown: "", error: "Doc not found" }, { status: 404 });
+		return new Response("Doc not found", { status: 404 });
 	}

 	try {
@@ -37,12 +41,9 @@ export async function GET({ params }) {

 		const markdown = await svxToMarkdown(svxContent, name);

-		return json({ markdown });
+		return new Response(markdown, { headers: MARKDOWN_HEADERS });
 	} catch (error) {
 		console.error("Error generating markdown:", error);
-		return json(
-			{ markdown: "", error: "Error generating markdown" },
-			{ status: 500 }
-		);
+		return new Response("Error generating markdown", { status: 500 });
 	}
 }
diff --git a/js/_website/src/routes/api/markdown/guide/[guide]/+server.ts b/js/_website/src/routes/api/markdown/guide/[guide]/+server.ts
index bfff285b1ca..820ed3f36c6 100644
--- a/js/_website/src/routes/api/markdown/guide/[guide]/+server.ts
+++ b/js/_website/src/routes/api/markdown/guide/[guide]/+server.ts
@@ -1,9 +1,13 @@
-import { json } from "@sveltejs/kit";
 import guide_names from "$lib/json/guides/guide_names.json";
 import { cleanGuideHtml } from "$lib/utils/clean-guide-html";

 export const prerender = true;

+const MARKDOWN_HEADERS = {
+	"Content-Type": "text/markdown; charset=utf-8",
+	"X-Robots-Tag": "noindex"
+};
+
 export function entries() {
 	return guide_names.guide_urls.map((guide) => ({ guide }));
 }
@@ -17,11 +21,13 @@ export async function GET({ params }) {
 		const markdown = data.guide?.content;

 		if (!markdown) {
-			return json({ markdown: "", error: "Guide not found" }, { status: 404 });
+			return new Response("Guide not found", { status: 404 });
 		}

-		return json({ markdown: await cleanGuideHtml(markdown) });
+		return new Response(await cleanGuideHtml(markdown), {
+			headers: MARKDOWN_HEADERS
+		});
 	} catch {
-		return json({ markdown: "", error: "Guide not found" }, { status: 404 });
+		return new Response("Guide not found", { status: 404 });
 	}
 }

PATCH

echo "Patch applied successfully."
