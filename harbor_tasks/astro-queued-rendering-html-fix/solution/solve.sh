#!/bin/bash
set -e

cd /workspace/astro

# Check if already patched (idempotency check)
if grep -q "vnode = markHTMLString(vnode)" packages/astro/src/runtime/server/render/page.ts; then
    echo "Fix already applied, exiting."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/packages/astro/src/runtime/server/render/page.ts b/packages/astro/src/runtime/server/render/page.ts
index abc..def 100644
--- a/packages/astro/src/runtime/server/render/page.ts
+++ b/packages/astro/src/runtime/server/render/page.ts
@@ -2,6 +2,7 @@ import type { RouteData, SSRResult } from '../../../types/public/internal.js';
 import { renderToAsyncIterable, renderToReadableStream, renderToString } from './astro/render.js';
 import { encoder } from './common.js';
 import { type NonAstroPageComponent, renderComponentToString } from './component.js';
+import { markHTMLString } from '../escape.js';
 import { renderCspContent } from './csp.js';
 import type { AstroComponentFactory } from './index.js';
 import { isDeno, isNode } from './util.js';
@@ -32,7 +33,13 @@ export async function renderPage(
 			// then process it through the queue system

 			// Call the component function to get the vnode tree
-			const vnode = await (componentFactory as any)(pageProps);
+			let vnode = await (componentFactory as any)(pageProps);
+
+			// .html pages return plain strings that are already valid HTML.
+			// Mark them as safe HTML so the queue builder doesn't escape the content.
+			if ((componentFactory as any)['astro:html'] && typeof vnode === 'string') {
+				vnode = markHTMLString(vnode);
+			}

 			// Build a render queue from the vnode tree
 			const queue = await buildRenderQueue(
PATCH

# Rebuild the package to apply changes
pnpm -C packages/astro build

echo "Fix applied successfully."
