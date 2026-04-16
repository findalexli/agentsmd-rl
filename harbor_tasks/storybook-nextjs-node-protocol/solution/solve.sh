#!/bin/bash
set -e

cd /workspace/storybook

# Check if already patched (idempotency check)
if grep -q "NODE_PROTOCOL_REGEX" code/frameworks/nextjs/src/nodePolyfills/webpack.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/code/frameworks/nextjs/src/nodePolyfills/webpack.ts b/code/frameworks/nextjs/src/nodePolyfills/webpack.ts
index 1234567..abcdefg 100644
--- a/code/frameworks/nextjs/src/nodePolyfills/webpack.ts
+++ b/code/frameworks/nextjs/src/nodePolyfills/webpack.ts
@@ -1,14 +1,26 @@
 import NodePolyfillPlugin from 'node-polyfill-webpack-plugin';
 import type { Configuration } from 'webpack';
+import webpack from 'webpack';
+
+const NODE_PROTOCOL_REGEX = /^node:/;

 export const configureNodePolyfills = (baseConfig: Configuration) => {
   // This is added as a way to avoid issues caused by Next.js 13.4.3
   // introduced by gzip-size
-  baseConfig.plugins = [...(baseConfig.plugins || []), new NodePolyfillPlugin()];
+  // Newer Next.js releases import builtins through the node: scheme, but webpack's
+  // polyfill and fallback handling only applies once the request is normalized.
+  baseConfig.plugins = [
+    ...(baseConfig.plugins || []),
+    new webpack.NormalModuleReplacementPlugin(NODE_PROTOCOL_REGEX, (resource) => {
+      resource.request = resource.request.replace(NODE_PROTOCOL_REGEX, '');
+    }),
+    new NodePolyfillPlugin(),
+  ];

   baseConfig.resolve = {
     ...baseConfig.resolve,
     fallback: {
+      ...baseConfig.resolve?.fallback,
       fs: false,
     },
   };
PATCH

echo "Patch applied successfully"
