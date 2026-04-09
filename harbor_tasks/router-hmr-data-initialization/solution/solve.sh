#!/bin/bash
set -e

cd /workspace/router

# Check if already patched (idempotency check)
if grep -q "import.meta.hot.data ??= {}" packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts; then
    echo "Fix already applied, skipping..."
    exit 0
fi

# Apply the fix
patch -p1 <<'PATCH'
diff --git a/packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts b/packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts
index 5146202ad31..af05d48b31c 100644
--- a/packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts
+++ b/packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts
@@ -15,6 +15,7 @@ const buildStableSplitComponentStatements = template.statements(
   `
     const %%stableComponentIdent%% = import.meta.hot?.data?.[%%hotDataKey%%] ?? %%lazyRouteComponentIdent%%(%%localImporterIdent%%, %%exporterIdent%%)
     if (import.meta.hot) {
+      import.meta.hot.data ??= {}
       import.meta.hot.data[%%hotDataKey%%] = %%stableComponentIdent%%
     }
   `,
PATCH

echo "Fix applied successfully!"
