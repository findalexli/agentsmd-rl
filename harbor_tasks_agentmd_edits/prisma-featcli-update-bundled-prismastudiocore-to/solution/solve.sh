#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prisma

# Idempotent: skip if already applied
if grep -q "procedure === 'transaction'" packages/cli/src/Studio.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index b46901e7859d..1e20e1963655 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -65,6 +65,10 @@
 - **Test helpers**: `ctx.setConfigFile('<name>')` (from `__helpers__/prismaConfig.ts`) overrides the config used for the next CLI invocation and is automatically reset after each test, so no explicit cleanup is needed. Many migrate fixtures now provide one config per schema variant (e.g. `invalid-url.config.ts` next to `prisma/invalid-url.prisma`) and tests swap them via `ctx.setConfigFile(...)`. `ctx.setDatasource`/`ctx.resetDatasource` continue to override connection URLs when needed.

 - **CLI commands**: Most commands already accept `--config` for custom config paths. Upcoming work removes `--schema` / `--url` in favour of config-based resolution. When editing CLI help text, keep examples aligned with new config-first workflow.
+  - For isolated Studio verification, you can run `packages/cli/src/Studio.ts` directly via `pnpm exec tsx` and pass a config object that preserves `loadedFromFile`; this keeps SQLite URLs resolving relative to the config file while avoiding unrelated `packages/cli/src/bin.ts` imports.
+  - Recent `@prisma/studio-core` bumps can require keeping the CLI's HTML import map in `packages/cli/src/Studio.ts` aligned with new bare browser imports (for example `@radix-ui/react-toggle` and `chart.js/auto`), and the CLI shell can serve `/favicon.ico` directly if the Studio UI starts requesting one.
+  - `esm.sh` may resolve React-based browser dependencies against a newer canary React by default. When the Studio shell imports such packages via the HTML import map, pin them with `?deps=react@<shell-version>,react-dom@<shell-version>` or the command palette can crash with invalid-hook-call style errors.
+  - If Enter or click does not open a cell editor in Studio, verify that the current table and column are writable before assuming a keyboard regression; views/system tables and read-only columns legitimately stay non-editable.

 - **Driver adapters datasource**:
   - Helper `ctx.setDatasource()` in tests overrides config.datasource for connection-specific scenarios.
diff --git a/packages/cli/src/Studio.ts b/packages/cli/src/Studio.ts
index c1109c2d36d0..39d43a84870f 100644
--- a/packages/cli/src/Studio.ts
+++ b/packages/cli/src/Studio.ts
@@ -55,6 +55,19 @@ const DEFAULT_CONTENT_TYPE = 'application/octet-stream'

 const ADAPTER_FILE_NAME = 'adapter.js'
 const ADAPTER_FACTORY_FUNCTION_NAME = 'createAdapter'
+const REACT_VERSION = '19.2.0'
+const REACT_DOM_VERSION = REACT_VERSION
+const RADIX_REACT_TOGGLE_URL = `https://esm.sh/@radix-ui/react-toggle@1.1.10?deps=react@${REACT_VERSION},react-dom@${REACT_DOM_VERSION}`
+const CHART_JS_AUTO_URL = 'https://esm.sh/chart.js@4.5.1/auto'
+const PRISMA_LOGO_SVG = `<svg width="12" height="14" viewBox="0 0 12 14" fill="none" xmlns="http://www.w3.org/2000/svg">
+  <path
+    fill-rule="evenodd"
+    clip-rule="evenodd"
+    d="M0.396923 8.8719C0.25789 9.09869 0.260041 9.38484 0.402469 9.60951L2.98037 13.6761C3.14768 13.94 3.47018 14.0603 3.76949 13.9705L11.2087 11.7388C11.6147 11.617 11.8189 11.1641 11.6415 10.7792L6.8592 0.405309C6.62598 -0.100601 5.92291 -0.142128 5.63176 0.332808L0.396923 8.8719ZM6.73214 2.77688C6.6305 2.54169 6.2863 2.57792 6.23585 2.82912L4.3947 11.9965C4.35588 12.1898 4.53686 12.3549 4.72578 12.2985L9.86568 10.7642C10.0157 10.7194 10.093 10.5537 10.0309 10.41L6.73214 2.77688Z"
+    fill="currentColor"
+  />
+</svg>`
+const PRISMA_LOGO_SVG_DATA_URL = `data:image/svg+xml,${encodeURIComponent(PRISMA_LOGO_SVG)}`

 const ACCELERATE_UNSUPPORTED_MESSAGE =
   'Prisma Studio no longer supports Accelerate URLs (`prisma://` or `prisma+postgres://`). Use a direct database connection string instead.'
@@ -320,6 +333,10 @@ ${bold('Examples')}
       return ctx.text(INDEX_HTML, 200, { 'Content-Type': contentType })
     })

+    app.get('/favicon.ico', (ctx) => {
+      return ctx.body(PRISMA_LOGO_SVG, 200, { 'Content-Type': 'image/svg+xml' })
+    })
+
     app.get(`/${ADAPTER_FILE_NAME}`, (ctx) => {
       const contentType = FILE_EXTENSION_TO_CONTENT_TYPE[extname(ctx.req.path)]

@@ -376,6 +393,20 @@ ${bold('Examples')}
         ])
       }

+      if (procedure === 'transaction') {
+        if (!executor.executeTransaction) {
+          return ctx.json([serializeBffError(new Error('Executor does not support transactions'))])
+        }
+
+        const [error, results] = await executor.executeTransaction(request.queries)
+
+        if (error) {
+          return ctx.json([serializeBffError(error)])
+        }
+
+        return ctx.json([null, results])
+      }
+
       if (procedure === 'sql-lint') {
         if (!executor.lintSql) {
           return ctx.json([serializeBffError(new Error('Executor does not support SQL lint'))])
@@ -552,6 +583,7 @@ const INDEX_HTML =
   <head>
     <meta charset="UTF-8" />
     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
+    <link rel="icon" href="${PRISMA_LOGO_SVG_DATA_URL}" type="image/svg+xml">
     <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.1.17"></script>
     <link rel="stylesheet" href="/ui/index.css">
     <style>
@@ -569,10 +601,12 @@ const INDEX_HTML =
     <script type="importmap">
       {
         "imports": {
-          "react": "https://esm.sh/react@19.2.0",
-          "react/jsx-runtime": "https://esm.sh/react@19.2.0/jsx-runtime",
-          "react-dom": "https://esm.sh/react-dom@19.2.0",
-          "react-dom/client": "https://esm.sh/react-dom@19.2.0/client"
+          "react": "https://esm.sh/react@${REACT_VERSION}",
+          "react/jsx-runtime": "https://esm.sh/react@${REACT_VERSION}/jsx-runtime",
+          "react-dom": "https://esm.sh/react-dom@${REACT_DOM_VERSION}",
+          "react-dom/client": "https://esm.sh/react-dom@${REACT_DOM_VERSION}/client",
+          "@radix-ui/react-toggle": "${RADIX_REACT_TOGGLE_URL}",
+          "chart.js/auto": "${CHART_JS_AUTO_URL}"
         }
       }
     </script>

PATCH

echo "Patch applied successfully."
