#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if the flag already exists, patch is already applied
if grep -q 'OPENCODE_DISABLE_EMBEDDED_WEB_UI' packages/opencode/src/flag/flag.ts 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/script/build.ts b/packages/opencode/script/build.ts
index 4a94bf6c3e9..4b57ded9e43 100755
--- a/packages/opencode/script/build.ts
+++ b/packages/opencode/script/build.ts
@@ -63,6 +63,26 @@ console.log(`Loaded ${migrations.length} migrations`)
 const singleFlag = process.argv.includes("--single")
 const baselineFlag = process.argv.includes("--baseline")
 const skipInstall = process.argv.includes("--skip-install")
+const skipEmbedWebUi = process.argv.includes("--skip-embed-web-ui")
+
+
+const createEmbeddedWebUIBundle = async()=>{
+    console.log(`Building Web UI to embed in the binary`);
+    const appDir = path.join(import.meta.dirname, "../../app")
+    await $`bun run --cwd ${appDir} build`;
+    const allFiles = await Array.fromAsync(new Bun.Glob("**/*").scan({ cwd: path.join(appDir, "dist")}));
+    const fileMap = `
+    // Import all files as file_$i with type: "file"
+    ${allFiles.map((filePath, i) => `import file_${i} from "${path.join(appDir, "dist", filePath)}" with { type: "file" };`).join("\n")}
+    // Export with original mappings
+    export default {
+      ${allFiles.map((filePath, i)=>`"${filePath}": file_${i},`).join("\n")}
+    }
+    `.trim()
+    return fileMap;
+}
+
+const embeddedFileMap = skipEmbedWebUi ? null : await createEmbeddedWebUIBundle();

 const allTargets: {
   os: string
@@ -192,7 +212,10 @@ for (const item of targets) {
       execArgv: [`--user-agent=opencode/${Script.version}`, "--use-system-ca", "--"],
       windows: {},
     },
-    entrypoints: ["./src/index.ts", parserWorker, workerPath],
+    files: {
+      ...(embeddedFileMap ? { "opencode-web-ui.gen.ts": embeddedFileMap } : {}),
+    },
+    entrypoints: ["./src/index.ts", parserWorker, workerPath, ...(embeddedFileMap ? ["opencode-web-ui.gen.ts"] : [])],
     define: {
       OPENCODE_VERSION: `'${Script.version}'`,
       OPENCODE_MIGRATIONS: JSON.stringify(migrations),
diff --git a/packages/opencode/src/flag/flag.ts b/packages/opencode/src/flag/flag.ts
index 0c55187b9dc..b35f84c8e26 100644
--- a/packages/opencode/src/flag/flag.ts
+++ b/packages/opencode/src/flag/flag.ts
@@ -70,6 +70,7 @@ export namespace Flag {
   export const OPENCODE_EXPERIMENTAL_MARKDOWN = !falsy("OPENCODE_EXPERIMENTAL_MARKDOWN")
   export const OPENCODE_MODELS_URL = process.env["OPENCODE_MODELS_URL"]
   export const OPENCODE_MODELS_PATH = process.env["OPENCODE_MODELS_PATH"]
+  export const OPENCODE_DISABLE_EMBEDDED_WEB_UI = truthy("OPENCODE_DISABLE_EMBEDDED_WEB_UI")
   export const OPENCODE_DB = process.env["OPENCODE_DB"]
   export const OPENCODE_DISABLE_CHANNEL_DB = truthy("OPENCODE_DISABLE_CHANNEL_DB")
   export const OPENCODE_SKIP_MIGRATIONS = truthy("OPENCODE_SKIP_MIGRATIONS")
diff --git a/packages/opencode/src/server/server.ts b/packages/opencode/src/server/server.ts
index d260714d488..899dacee29d 100644
--- a/packages/opencode/src/server/server.ts
+++ b/packages/opencode/src/server/server.ts
@@ -56,6 +56,12 @@ initProjectors()

 export namespace Server {
   const log = Log.create({ service: "server" })
+  const DEFAULT_CSP =
+    "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; media-src 'self' data:; connect-src 'self' data:"
+  const embeddedUIPromise = Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI
+    ? Promise.resolve(null)
+    : // @ts-expect-error - generated file at build time
+      import("opencode-web-ui.gen.ts").then((module) => module.default as Record<string, string>).catch(() => null)

   export const Default = lazy(() => createApp({}))

@@ -504,24 +510,40 @@ export namespace Server {
         },
       )
       .all("/*", async (c) => {
+        const embeddedWebUI = await embeddedUIPromise
         const path = c.req.path

-        const response = await proxy(`https://app.opencode.ai${path}`, {
-          ...c.req,
-          headers: {
-            ...c.req.raw.headers,
-            host: "app.opencode.ai",
-          },
-        })
-        const match = response.headers.get("content-type")?.includes("text/html")
-          ? (await response.clone().text()).match(
-              /<script\b(?![^>]*\bsrc\s*=)[^>]*\bid=(['"])oc-theme-preload-script\1[^>]*>([\s\S]*?)<\/script>/i,
-            )
-          : undefined
-        const hash = match ? createHash("sha256").update(match[2]).digest("base64") : ""
-        response.headers.set("Content-Security-Policy", csp(hash))
-        return response
-      })
+        if (embeddedWebUI) {
+          const match = embeddedWebUI[path.replace(/^\//, "")] ?? embeddedWebUI["index.html"] ?? null
+          if (!match) return c.json({ error: "Not Found" }, 404)
+          const file = Bun.file(match)
+          if (await file.exists()) {
+            c.header("Content-Type", file.type)
+            if (file.type.startsWith("text/html")) {
+              c.header("Content-Security-Policy", DEFAULT_CSP)
+            }
+            return c.body(await file.arrayBuffer())
+          } else {
+            return c.json({ error: "Not Found" }, 404)
+          }
+        } else {
+          const response = await proxy(`https://app.opencode.ai${path}`, {
+            ...c.req,
+            headers: {
+              ...c.req.raw.headers,
+              host: "app.opencode.ai",
+            },
+          })
+          const match = response.headers.get("content-type")?.includes("text/html")
+            ? (await response.clone().text()).match(
+                /<script\b(?![^>]*\bsrc\s*=)[^>]*\bid=(['"])oc-theme-preload-script\1[^>]*>([\s\S]*?)<\/script>/i,
+              )
+            : undefined
+          const hash = match ? createHash("sha256").update(match[2]).digest("base64") : ""
+          response.headers.set("Content-Security-Policy", csp(hash))
+          return response
+        }
+      }) as unknown as Hono
   }

   export async function openapi() {

PATCH

echo "Patch applied successfully."
