#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'import npa from "npm-package-arg"' packages/opencode/src/plugin/shared.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/package.json b/packages/opencode/package.json
index d7f12549c018..40a0fed2fa1b 100644
--- a/packages/opencode/package.json
+++ b/packages/opencode/package.json
@@ -54,6 +54,7 @@
     "@types/bun": "catalog:",
     "@types/cross-spawn": "catalog:",
     "@types/mime-types": "3.0.1",
+    "@types/npm-package-arg": "6.1.4",
     "@types/npmcli__arborist": "6.3.3",
     "@types/semver": "^7.5.8",
     "@types/turndown": "5.0.5",
@@ -135,6 +136,7 @@
     "jsonc-parser": "3.3.1",
     "mime-types": "3.0.2",
     "minimatch": "10.0.3",
+    "npm-package-arg": "13.0.2",
     "open": "10.1.2",
     "opencode-gitlab-auth": "2.0.1",
     "opencode-poe-auth": "0.0.1",
diff --git a/packages/opencode/src/npm/index.ts b/packages/opencode/src/npm/index.ts
index 69bb2ca5284e..3568ff20e245 100644
--- a/packages/opencode/src/npm/index.ts
+++ b/packages/opencode/src/npm/index.ts
@@ -11,6 +11,7 @@ import { Arborist } from "@npmcli/arborist"

 export namespace Npm {
   const log = Log.create({ service: "npm" })
+  const illegal = process.platform === "win32" ? new Set(["<", ">", ":", '"', "|", "?", "*"]) : undefined

   export const InstallFailedError = NamedError.create(
     "NpmInstallFailedError",
@@ -19,8 +20,13 @@ export namespace Npm {
     }),
   )

+  export function sanitize(pkg: string) {
+    if (!illegal) return pkg
+    return Array.from(pkg, (char) => (illegal.has(char) || char.charCodeAt(0) < 32 ? "_" : char)).join("")
+  }
+
   function directory(pkg: string) {
-    return path.join(Global.Path.cache, "packages", pkg)
+    return path.join(Global.Path.cache, "packages", sanitize(pkg))
   }

   function resolveEntryPoint(name: string, dir: string) {
diff --git a/packages/opencode/src/plugin/shared.ts b/packages/opencode/src/plugin/shared.ts
index f92520d05dc2..6cda49786bc9 100644
--- a/packages/opencode/src/plugin/shared.ts
+++ b/packages/opencode/src/plugin/shared.ts
@@ -1,5 +1,6 @@
 import path from "path"
 import { fileURLToPath, pathToFileURL } from "url"
+import npa from "npm-package-arg"
 import semver from "semver"
 import { Npm } from "@/npm"
 import { Filesystem } from "@/util/filesystem"
@@ -12,11 +13,24 @@ export function isDeprecatedPlugin(spec: string) {
   return DEPRECATED_PLUGIN_PACKAGES.some((pkg) => spec.includes(pkg))
 }

+function parse(spec: string) {
+  try {
+    return npa(spec)
+  } catch {}
+}
+
 export function parsePluginSpecifier(spec: string) {
-  const lastAt = spec.lastIndexOf("@")
-  const pkg = lastAt > 0 ? spec.substring(0, lastAt) : spec
-  const version = lastAt > 0 ? spec.substring(lastAt + 1) : "latest"
-  return { pkg, version }
+  const hit = parse(spec)
+  if (hit?.type === "alias" && !hit.name) {
+    const sub = (hit as npa.AliasResult).subSpec
+    if (sub?.name) {
+      const version = !sub.rawSpec || sub.rawSpec === "*" ? "latest" : sub.rawSpec
+      return { pkg: sub.name, version }
+    }
+  }
+  if (!hit?.name) return { pkg: spec, version: "" }
+  if (hit.raw === hit.name) return { pkg: hit.name, version: "latest" }
+  return { pkg: hit.name, version: hit.rawSpec }
 }

 export type PluginSource = "file" | "npm"
@@ -190,9 +204,11 @@ export async function checkPluginCompatibility(target: string, opencodeVersion:
   }
 }

-export async function resolvePluginTarget(spec: string, parsed = parsePluginSpecifier(spec)) {
+export async function resolvePluginTarget(spec: string) {
   if (isPathPluginSpec(spec)) return resolvePathPluginTarget(spec)
-  const result = await Npm.add(parsed.pkg + "@" + parsed.version)
+  const hit = parse(spec)
+  const pkg = hit?.name && hit.raw === hit.name ? `${hit.name}@latest` : spec
+  const result = await Npm.add(pkg)
   return result.directory
 }

PATCH

# Install newly added npm-package-arg dependency
bun install

echo "Patch applied successfully."
