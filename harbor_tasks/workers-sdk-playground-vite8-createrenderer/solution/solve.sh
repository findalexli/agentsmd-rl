#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workers-sdk

# Idempotent: skip if already applied
if grep -q '@cloudflare/style-provider/lib/index.js' packages/workers-playground/vite.config.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.changeset/workers-playground-fix-vite8-createrenderer.md b/.changeset/workers-playground-fix-vite8-createrenderer.md
new file mode 100644
index 0000000000..747fb6284c
--- /dev/null
+++ b/.changeset/workers-playground-fix-vite8-createrenderer.md
@@ -0,0 +1,9 @@
+---
+"@cloudflare/workers-playground": patch
+---
+
+fix: resolve TypeError: createRenderer is not a function when built with Vite 8
+
+Vite 8 switched its bundler from Rollup to rolldown. The `@cloudflare/style-provider` package ships a hybrid ESM+CJS build (its `es/` directory uses `require()` internally), which rolldown mishandles by generating an anonymous, unreachable module initializer — leaving `createRenderer` as `undefined` at runtime.
+
+Fixed by aliasing `@cloudflare/style-provider` to its CJS entry (`lib/index.js`) in `vite.config.ts`. Rolldown handles plain CJS correctly via its interop layer.
diff --git a/packages/workers-playground/vite.config.ts b/packages/workers-playground/vite.config.ts
index b096a4b206..0547329744 100644
--- a/packages/workers-playground/vite.config.ts
+++ b/packages/workers-playground/vite.config.ts
@@ -13,14 +13,26 @@ export default defineConfig(({ mode }) => {
 		],
 		resolve: {
 			alias: {
+				// @cloudflare/style-provider ships a hybrid ESM+CJS package: its es/ directory
+				// contains files that are nominally ESM but internally use require(). Vite 8's
+				// bundler (rolldown) mishandles this pattern and generates an anonymous,
+				// unreachable module initializer, leaving `createRenderer` as undefined at
+				// runtime (TypeError: createRenderer is not a function).
+				// Aliasing to the CJS build (lib/) avoids this — rolldown handles plain CJS
+				// correctly via its interop layer.
+				"@cloudflare/style-provider": "@cloudflare/style-provider/lib/index.js",
 				"react/jsx-runtime.js": "react/jsx-runtime",
 			},
 		},

 		appType: "spa",
-		base: "/playground",
 		build: {
 			chunkSizeWarningLimit: 1000,
+			// The application is actually hosted at `playground/`, but we can't use the `base` option.
+			// That would  cause Vite to put the assets directly in `dist/assets` and to refer to them via `/playground/assets/` in the generated HTML.
+			// But Wrangler will upload the assets as though they were in `/assets` and so the links in the HTML would be broken.
+			// By keeping the assets in `dist/playground/assets`, the links in the HTML will match the actual location of the assets when deployed.
+			assetsDir: "playground/assets",
 		},
 	};
 });

PATCH

echo "Patch applied successfully."
