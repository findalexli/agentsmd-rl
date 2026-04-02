#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if already fixed
if grep -q 'function pluginList(data: unknown)' packages/opencode/src/plugin/install.ts 2>/dev/null; then
    echo "Already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/plugin/install.ts b/packages/opencode/src/plugin/install.ts
index 9640a662bd8..8c0a6ee2744 100644
--- a/packages/opencode/src/plugin/install.ts
+++ b/packages/opencode/src/plugin/install.ts
@@ -94,6 +94,13 @@ function pluginSpec(item: unknown) {
   return item[0]
 }

+function pluginList(data: unknown) {
+  if (!data || typeof data !== "object" || Array.isArray(data)) return
+  const item = data as { plugin?: unknown }
+  if (!Array.isArray(item.plugin)) return
+  return item.plugin
+}
+
 function parseTarget(item: unknown): Target | undefined {
   if (item === "server" || item === "tui") return { kind: item }
   if (!Array.isArray(item)) return
@@ -118,9 +125,28 @@ function parseTargets(raw: unknown) {
   return [...map.values()]
 }

-function patchPluginList(list: unknown[], spec: string, next: unknown, force = false): { mode: Mode; list: unknown[] } {
+function patch(text: string, path: Array<string | number>, value: unknown, insert = false) {
+  return applyEdits(
+    text,
+    modify(text, path, value, {
+      formattingOptions: {
+        tabSize: 2,
+        insertSpaces: true,
+      },
+      isArrayInsertion: insert,
+    }),
+  )
+}
+
+function patchPluginList(
+  text: string,
+  list: unknown[] | undefined,
+  spec: string,
+  next: unknown,
+  force = false,
+): { mode: Mode; text: string } {
   const pkg = parsePluginSpecifier(spec).pkg
-  const rows = list.map((item, i) => ({
+  const rows = (list ?? []).map((item, i) => ({
     item,
     i,
     spec: pluginSpec(item),
@@ -133,16 +159,22 @@ function patchPluginList(list: unknown[], spec: string, next: unknown, force = f
   })

   if (!dup.length) {
+    if (!list) {
+      return {
+        mode: "add",
+        text: patch(text, ["plugin"], [next]),
+      }
+    }
     return {
       mode: "add",
-      list: [...list, next],
+      text: patch(text, ["plugin", list.length], next, true),
     }
   }

   if (!force) {
     return {
       mode: "noop",
-      list,
+      text,
     }
   }

@@ -150,29 +182,37 @@ function patchPluginList(list: unknown[], spec: string, next: unknown, force = f
   if (!keep) {
     return {
       mode: "noop",
-      list,
+      text,
     }
   }

   if (dup.length === 1 && keep.spec === spec) {
     return {
       mode: "noop",
-      list,
+      text,
     }
   }

-  const idx = new Set(dup.map((item) => item.i))
+  let out = text
+  if (typeof keep.item === "string") {
+    out = patch(out, ["plugin", keep.i], next)
+  }
+  if (Array.isArray(keep.item) && typeof keep.item[0] === "string") {
+    out = patch(out, ["plugin", keep.i, 0], spec)
+  }
+
+  const del = dup
+    .map((item) => item.i)
+    .filter((i) => i !== keep.i)
+    .sort((a, b) => b - a)
+
+  for (const i of del) {
+    out = patch(out, ["plugin", i], undefined)
+  }
+
   return {
     mode: "replace",
-    list: rows.flatMap((row) => {
-      if (!idx.has(row.i)) return [row.item]
-      if (row.i !== keep.i) return []
-      if (typeof row.item === "string") return [next]
-      if (Array.isArray(row.item) && typeof row.item[0] === "string") {
-        return [[spec, ...row.item.slice(1)]]
-      }
-      return [row.item]
-    }),
+    text: out,
   }
 }

@@ -289,10 +329,9 @@ async function patchOne(dir: string, target: Target, spec: string, force: boolea
     }
   }

-  const list: unknown[] =
-    data && typeof data === "object" && !Array.isArray(data) && Array.isArray(data.plugin) ? data.plugin : []
+  const list = pluginList(data)
   const item = target.opts ? [spec, target.opts] : spec
-  const out = patchPluginList(list, spec, item, force)
+  const out = patchPluginList(text, list, spec, item, force)
   if (out.mode === "noop") {
     return {
       ok: true,
@@ -304,13 +343,7 @@ async function patchOne(dir: string, target: Target, spec: string, force: boolea
     }
   }

-  const edits = modify(text, ["plugin"], out.list, {
-    formattingOptions: {
-      tabSize: 2,
-      insertSpaces: true,
-    },
-  })
-  const write = await dep.write(cfg, applyEdits(text, edits)).catch((error: unknown) => error)
+  const write = await dep.write(cfg, out.text).catch((error: unknown) => error)
   if (write instanceof Error) {
     return {
       ok: false,

PATCH

echo "Patch applied successfully."
