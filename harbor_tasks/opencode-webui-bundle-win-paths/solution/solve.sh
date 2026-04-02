#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

TARGET="packages/opencode/script/build.ts"

# Idempotency check: if the fix is already applied, skip
if grep -q '\.sort()' "$TARGET" && grep -q 'const dist = path.join' "$TARGET" 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/opencode/script/build.ts b/packages/opencode/script/build.ts
index 653c67d8de7a..7341810768c9 100755
--- a/packages/opencode/script/build.ts
+++ b/packages/opencode/script/build.ts
@@ -68,17 +68,24 @@ const skipEmbedWebUi = process.argv.includes("--skip-embed-web-ui")
 const createEmbeddedWebUIBundle = async () => {
   console.log(`Building Web UI to embed in the binary`)
   const appDir = path.join(import.meta.dirname, "../../app")
+  const dist = path.join(appDir, "dist")
   await $`bun run --cwd ${appDir} build`
-  const allFiles = await Array.fromAsync(new Bun.Glob("**/*").scan({ cwd: path.join(appDir, "dist") }))
-  const fileMap = `
-    // Import all files as file_$i with type: "file"
-    ${allFiles.map((filePath, i) => `import file_${i} from "${path.join(appDir, "dist", filePath)}" with { type: "file" };`).join("\n")}
-    // Export with original mappings
-    export default {
-      ${allFiles.map((filePath, i) => `"${filePath}": file_${i},`).join("\n")}
-    }
-    `.trim()
-  return fileMap
+  const files = (await Array.fromAsync(new Bun.Glob("**/*").scan({ cwd: dist })))
+    .map((file) => file.replaceAll("\\", "/"))
+    .sort()
+  const imports = files.map((file, i) => {
+    const spec = path.relative(dir, path.join(dist, file)).replaceAll("\\", "/")
+    return `import file_${i} from ${JSON.stringify(spec.startsWith(".") ? spec : `./${spec}`)} with { type: "file" };`
+  })
+  const entries = files.map((file, i) => `  ${JSON.stringify(file)}: file_${i},`)
+  return [
+    `// Import all files as file_$i with type: "file"`,
+    ...imports,
+    `// Export with original mappings`,
+    `export default {`,
+    ...entries,
+    `}`,
+  ].join("\n")
 }

 const embeddedFileMap = skipEmbedWebUi ? null : await createEmbeddedWebUIBundle()
PATCH

echo "Patch applied successfully."
