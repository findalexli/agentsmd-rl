#!/bin/bash
set -e

cd /workspace/router

# Check if already applied
if grep -q "import.meta.hot.data ??= {}" packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the source fix
cat > /tmp/fix.patch << 'PATCH'
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

git apply /tmp/fix.patch
echo "Source patch applied successfully"

# Update snapshot files to include the data initialization
update_snapshot() {
    local file="$1"
    if [ -f "$file" ]; then
        # Add data initialization line after 'if (import.meta.hot) {'
        sed -i 's/if (import.meta.hot) {/if (import.meta.hot) {\n  import.meta.hot.data ??= {};/g' "$file"
        echo "Updated $file"
    fi
}

# Update all snapshot files
update_snapshot "packages/router-plugin/tests/add-hmr/snapshots/react/arrow-function@true.tsx"
update_snapshot "packages/router-plugin/tests/add-hmr/snapshots/react/function-declaration@true.tsx"
update_snapshot "packages/router-plugin/tests/add-hmr/snapshots/react/multi-component@true.tsx"
update_snapshot "packages/router-plugin/tests/add-hmr/snapshots/react/string-literal-keys@true.tsx"

# Disable nx cloud and daemon to avoid cache issues
export NX_CLOUD_ACCESS_TOKEN=""
export NX_CLOUD_ID=""
export NX_DAEMON="false"

# Rebuild the plugin so the fix takes effect
echo "Rebuilding router-plugin..."
npx nx run @tanstack/router-plugin:build --skip-nx-cache

echo "All patches applied successfully"
