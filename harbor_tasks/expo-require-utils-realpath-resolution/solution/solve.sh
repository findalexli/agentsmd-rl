#!/bin/bash
set -e

# Navigate to the repository
REPO="/workspace/expo"
PKG="$REPO/packages/@expo/require-utils"

cd "$REPO"

# Check if already patched (idempotency)
if grep -q "toRealDirname" "$PKG/src/load.ts" 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply --whitespace=nowarn
diff --git a/packages/@expo/require-utils/CHANGELOG.md b/packages/@expo/require-utils/CHANGELOG.md
index eb8c2a0a593e0f..10b8311716e64f 100644
--- a/packages/@expo/require-utils/CHANGELOG.md
+++ b/packages/@expo/require-utils/CHANGELOG.md
@@ -12,6 +12,7 @@
 ### 🐛 Bug fixes

 - Prevent `.js` transform from discovering project Babel config ([#43726](https://github.com/expo/expo/pull/43726) by [@kitten](https://github.com/kitten))
+- Resolve realpath for evaluated modules' `node_modules` paths in `compileModule` ([#44599](https://github.com/expo/expo/pull/44599) by [@kitten](https://github.com/kitten))

 ### 💡 Others

diff --git a/packages/@expo/require-utils/src/load.ts b/packages/@expo/require-utils/src/load.ts
index c73104f229cacc..bc37b98f4ff669 100644
--- a/packages/@expo/require-utils/src/load.ts
+++ b/packages/@expo/require-utils/src/load.ts
@@ -84,10 +84,34 @@ export interface ModuleOptions {
   paths?: string[];
 }

+function toRealDirname(filePath: string): string {
+  let normalized = path.resolve(filePath);
+  // Try resolving the filename itself first
+  try {
+    normalized = fs.realpathSync(normalized);
+    return path.dirname(normalized);
+  } catch (error: any) {
+    normalized = path.dirname(normalized);
+    // If we're getting another error than an ENOENT, return the dirname unchanged
+    if (error?.code !== 'ENOENT') {
+      return normalized;
+    }
+  }
+  // Alternatively, if it's a fake path, resolve the directory directly instead
+  try {
+    return fs.realpathSync(normalized);
+  } catch {
+    return normalized;
+  }
+}
+
 function compileModule(code: string, filename: string, opts: ModuleOptions) {
   const format = toFormat(filename, false);
   const prependPaths = opts.paths ?? [];
-  const nodeModulePaths = nodeModule._nodeModulePaths(path.dirname(filename));
+  // See: https://github.com/nodejs/node/blob/ff080948666f28fbd767548d26bea034d30bc277/lib/internal/modules/cjs/loader.js#L767
+  // If we get a symlinked path instead of the realpath, we assume the realpath is needed for Node module resolution
+  const basePath = toRealDirname(filename);
+  const nodeModulePaths = nodeModule._nodeModulePaths(basePath);
   const paths = [...prependPaths, ...nodeModulePaths];
   try {
     const mod = Object.assign(new nodeModule.Module(filename, parent), { filename, paths });
PATCH

echo "Patch applied successfully"

# Try to rebuild the JS files if possible
cd "$PKG"

# Try different build approaches
if [ -f "package.json" ]; then
    # Check if there's a build script
    if grep -q '"build"' package.json; then
        echo "Attempting to build with npm/yarn..."
        npm run build 2>/dev/null || yarn build 2>/dev/null || echo "Build not available, source is updated"
    else
        echo "No build script found, source is updated"
    fi
else
    echo "No package.json found"
fi

echo "Done"
