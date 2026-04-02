#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if fix is already applied
if grep -q 'upsertTheme' packages/opencode/src/cli/cmd/tui/context/theme.tsx 2>/dev/null; then
  echo "Fix already applied"
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/specs/tui-plugins.md b/packages/opencode/specs/tui-plugins.md
index 31edcf114a2..5a7caa75b9d 100644
--- a/packages/opencode/specs/tui-plugins.md
+++ b/packages/opencode/specs/tui-plugins.md
@@ -269,7 +269,9 @@ Theme install behavior:

 - Relative theme paths are resolved from the plugin root.
 - Theme name is the JSON basename.
-- Install is skipped if that theme name already exists.
+- First install writes only when the destination file is missing.
+- If the theme name already exists, install is skipped unless plugin metadata state is `updated`.
+- On `updated`, host only rewrites themes previously tracked for that plugin and only when source `mtime`/`size` changed.
 - Local plugins persist installed themes under the local `.opencode/themes` area near the plugin config source.
 - Global plugins persist installed themes under the global `themes` dir.
 - Invalid or unreadable theme files are ignored.
diff --git a/packages/opencode/src/cli/cmd/tui/context/theme.tsx b/packages/opencode/src/cli/cmd/tui/context/theme.tsx
index dcef2cb466f..4857f7a4d20 100644
--- a/packages/opencode/src/cli/cmd/tui/context/theme.tsx
+++ b/packages/opencode/src/cli/cmd/tui/context/theme.tsx
@@ -183,6 +183,18 @@ export function addTheme(name: string, theme: unknown) {
   return true
 }

+export function upsertTheme(name: string, theme: unknown) {
+  if (!name) return false
+  if (!isTheme(theme)) return false
+  if (customThemes[name] !== undefined) {
+    customThemes[name] = theme
+  } else {
+    pluginThemes[name] = theme
+  }
+  syncThemes()
+  return true
+}
+
 export function resolveTheme(theme: ThemeJson, mode: "dark" | "light") {
   const defs = theme.defs ?? {}
   function resolveColor(c: ColorValue, chain: string[] = []): RGBA {
diff --git a/packages/opencode/src/cli/cmd/tui/plugin/runtime.ts b/packages/opencode/src/cli/cmd/tui/plugin/runtime.ts
index 0e1674bdac2..e992577a6ea 100644
--- a/packages/opencode/src/cli/cmd/tui/plugin/runtime.ts
+++ b/packages/opencode/src/cli/cmd/tui/plugin/runtime.ts
@@ -31,7 +31,7 @@ import {
 } from "@/plugin/shared"
 import { PluginMeta } from "@/plugin/meta"
 import { installPlugin as installModulePlugin, patchPluginConfig, readPluginManifest } from "@/plugin/install"
-import { addTheme, hasTheme } from "../context/theme"
+import { hasTheme, upsertTheme } from "../context/theme"
 import { Global } from "@/global"
 import { Filesystem } from "@/util/filesystem"
 import { Process } from "@/util/process"
@@ -49,7 +49,8 @@ type PluginLoad = {
   source: PluginSource | "internal"
   id: string
   module: TuiPluginModule
-  install_theme: TuiTheme["install"]
+  theme_meta: TuiConfig.PluginMeta
+  theme_root: string
 }

 type Api = HostPluginApi
@@ -64,6 +65,7 @@ type PluginEntry = {
   id: string
   load: PluginLoad
   meta: TuiPluginMeta
+  themes: Record<string, PluginMeta.Theme>
   plugin: TuiPlugin
   options: Config.PluginOptions | undefined
   enabled: boolean
@@ -143,12 +145,54 @@ function resolveRoot(root: string) {
   return path.resolve(process.cwd(), root)
 }

-function createThemeInstaller(meta: TuiConfig.PluginMeta, root: string, spec: string): TuiTheme["install"] {
+function createThemeInstaller(
+  meta: TuiConfig.PluginMeta,
+  root: string,
+  spec: string,
+  plugin: PluginEntry,
+): TuiTheme["install"] {
   return async (file) => {
     const raw = file.startsWith("file://") ? fileURLToPath(file) : file
     const src = path.isAbsolute(raw) ? raw : path.resolve(root, raw)
-    const theme = path.basename(src, path.extname(src))
-    if (hasTheme(theme)) return
+    const name = path.basename(src, path.extname(src))
+    const source_dir = path.dirname(meta.source)
+    const local_dir =
+      path.basename(source_dir) === ".opencode"
+        ? path.join(source_dir, "themes")
+        : path.join(source_dir, ".opencode", "themes")
+    const dest_dir = meta.scope === "local" ? local_dir : path.join(Global.Path.config, "themes")
+    const dest = path.join(dest_dir, `${name}.json`)
+    const stat = await Filesystem.statAsync(src)
+    const mtime = stat ? Math.floor(typeof stat.mtimeMs === "bigint" ? Number(stat.mtimeMs) : stat.mtimeMs) : undefined
+    const size = stat ? (typeof stat.size === "bigint" ? Number(stat.size) : stat.size) : undefined
+    const exists = hasTheme(name)
+    const prev = plugin.themes[name]
+
+    if (exists) {
+      if (plugin.meta.state !== "updated") return
+      if (!prev) {
+        if (await Filesystem.exists(dest)) {
+          plugin.themes[name] = {
+            src,
+            dest,
+            mtime,
+            size,
+          }
+          await PluginMeta.setTheme(plugin.id, name, plugin.themes[name]!).catch((error) => {
+            log.warn("failed to track tui plugin theme", {
+              path: spec,
+              id: plugin.id,
+              theme: src,
+              dest,
+              error,
+            })
+          })
+        }
+        return
+      }
+      if (prev.dest !== dest) return
+      if (prev.mtime === mtime && prev.size === size) return
+    }

     const text = await Filesystem.readText(src).catch((error) => {
       log.warn("failed to read tui plugin theme", { path: spec, theme: src, error })
@@ -170,20 +214,28 @@ function createThemeInstaller(meta: TuiConfig.PluginMeta, root: string, spec: st
       return
     }

-    const source_dir = path.dirname(meta.source)
-    const local_dir =
-      path.basename(source_dir) === ".opencode"
-        ? path.join(source_dir, "themes")
-        : path.join(source_dir, ".opencode", "themes")
-    const dest_dir = meta.scope === "local" ? local_dir : path.join(Global.Path.config, "themes")
-    const dest = path.join(dest_dir, `${theme}.json`)
-    if (!(await Filesystem.exists(dest))) {
+    if (exists || !(await Filesystem.exists(dest))) {
       await Filesystem.write(dest, text).catch((error) => {
         log.warn("failed to persist tui plugin theme", { path: spec, theme: src, dest, error })
       })
     }

-    addTheme(theme, data)
+    upsertTheme(name, data)
+    plugin.themes[name] = {
+      src,
+      dest,
+      mtime,
+      size,
+    }
+    await PluginMeta.setTheme(plugin.id, name, plugin.themes[name]!).catch((error) => {
+      log.warn("failed to track tui plugin theme", {
+        path: spec,
+        id: plugin.id,
+        theme: src,
+        dest,
+        error,
+      })
+    })
   }
 }

@@ -222,7 +274,6 @@ async function loadExternalPlugin(
   }

   const root = resolveRoot(source === "file" ? spec : target)
-  const install_theme = createThemeInstaller(meta, root, spec)
   const entry = await resolvePluginEntrypoint(spec, target, "tui").catch((error) => {
     fail("failed to resolve tui plugin entry", { path: spec, target, retry, error })
     return
@@ -253,7 +304,8 @@ async function loadExternalPlugin(
     source,
     id,
     module: mod,
-    install_theme,
+    theme_meta: meta,
+    theme_root: root,
   }
 }

@@ -297,14 +349,11 @@ function loadInternalPlugin(item: InternalTuiPlugin): PluginLoad {
     source: "internal",
     id: item.id,
     module: item,
-    install_theme: createThemeInstaller(
-      {
-        scope: "global",
-        source: target,
-      },
-      process.cwd(),
-      spec,
-    ),
+    theme_meta: {
+      scope: "global",
+      source: target,
+    },
+    theme_root: process.cwd(),
   }
 }

@@ -436,7 +485,7 @@ async function activatePluginEntry(state: RuntimeState, plugin: PluginEntry, per
   if (plugin.scope) return true

   const scope = createPluginScope(plugin.load, plugin.id)
-  const api = pluginApi(state, plugin.load, scope, plugin.id)
+  const api = pluginApi(state, plugin, scope, plugin.id)
   const ok = await Promise.resolve()
     .then(async () => {
       await plugin.plugin(api, plugin.options, plugin.meta)
@@ -479,9 +528,10 @@ async function deactivatePluginById(state: RuntimeState | undefined, id: string,
   return deactivatePluginEntry(state, plugin, persist)
 }

-function pluginApi(runtime: RuntimeState, load: PluginLoad, scope: PluginScope, base: string): TuiPluginApi {
+function pluginApi(runtime: RuntimeState, plugin: PluginEntry, scope: PluginScope, base: string): TuiPluginApi {
   const api = runtime.api
   const host = runtime.slots
+  const load = plugin.load
   const command: TuiPluginApi["command"] = {
     register(cb) {
       return scope.track(api.command.register(cb))
@@ -504,7 +554,7 @@ function pluginApi(runtime: RuntimeState, load: PluginLoad, scope: PluginScope,
   }

   const theme: TuiPluginApi["theme"] = Object.assign(Object.create(api.theme), {
-    install: load.install_theme,
+    install: createThemeInstaller(load.theme_meta, load.theme_root, load.spec, plugin),
   })

   const event: TuiPluginApi["event"] = {
@@ -563,13 +613,14 @@ function pluginApi(runtime: RuntimeState, load: PluginLoad, scope: PluginScope,
   }
 }

-function collectPluginEntries(load: PluginLoad, meta: TuiPluginMeta) {
+function collectPluginEntries(load: PluginLoad, meta: TuiPluginMeta, themes: Record<string, PluginMeta.Theme> = {}) {
   const options = load.item ? Config.pluginOptions(load.item) : undefined
   return [
     {
       id: load.id,
       load,
       meta,
+      themes,
       plugin: load.module.tui,
       options,
       enabled: true,
@@ -661,7 +712,8 @@ async function addExternalPluginEntries(state: RuntimeState, ready: PluginLoad[]
     }

     const row = createMeta(entry.source, entry.spec, entry.target, hit, entry.id)
-    for (const plugin of collectPluginEntries(entry, row)) {
+    const themes = hit?.entry.themes ? { ...hit.entry.themes } : {}
+    for (const plugin of collectPluginEntries(entry, row, themes)) {
       if (!addPluginEntry(state, plugin)) {
         ok = false
         continue
diff --git a/packages/opencode/src/plugin/meta.ts b/packages/opencode/src/plugin/meta.ts
index bf93870cb02..cbfaf6ae155 100644
--- a/packages/opencode/src/plugin/meta.ts
+++ b/packages/opencode/src/plugin/meta.ts
@@ -11,6 +11,13 @@ import { parsePluginSpecifier, pluginSource } from "./shared"
 export namespace PluginMeta {
   type Source = "file" | "npm"

+  export type Theme = {
+    src: string
+    dest: string
+    mtime?: number
+    size?: number
+  }
+
   export type Entry = {
     id: string
     source: Source
@@ -24,6 +31,7 @@ export namespace PluginMeta {
     time_changed: number
     load_count: number
     fingerprint: string
+    themes?: Record<string, Theme>
   }

   export type State = "first" | "updated" | "same"
@@ -35,7 +43,7 @@ export namespace PluginMeta {
   }

   type Store = Record<string, Entry>
-  type Core = Omit<Entry, "first_time" | "last_time" | "time_changed" | "load_count" | "fingerprint">
+  type Core = Omit<Entry, "first_time" | "last_time" | "time_changed" | "load_count" | "fingerprint" | "themes">
   type Row = Touch & { core: Core }

   function storePath() {
@@ -52,11 +60,11 @@ export namespace PluginMeta {
     return
   }

-  function modifiedAt(file: string) {
-    const stat = Filesystem.stat(file)
+  async function modifiedAt(file: string) {
+    const stat = await Filesystem.statAsync(file)
     if (!stat) return
-    const value = stat.mtimeMs
-    return Math.floor(typeof value === "bigint" ? Number(value) : value)
+    const mtime = stat.mtimeMs
+    return Math.floor(typeof mtime === "bigint" ? Number(mtime) : mtime)
   }

   function resolvedTarget(target: string) {
@@ -66,7 +74,7 @@ export namespace PluginMeta {

   async function npmVersion(target: string) {
     const resolved = resolvedTarget(target)
-    const stat = Filesystem.stat(resolved)
+    const stat = await Filesystem.statAsync(resolved)
     const dir = stat?.isDirectory() ? resolved : path.dirname(resolved)
     return Filesystem.readJson<{ version?: string }>(path.join(dir, "package.json"))
       .then((item) => item.version)
@@ -84,7 +92,7 @@ export namespace PluginMeta {
         source,
         spec,
         target,
-        modified: file ? modifiedAt(file) : undefined,
+        modified: file ? await modifiedAt(file) : undefined,
       }
     }

@@ -122,6 +130,7 @@ export namespace PluginMeta {
       time_changed: prev?.time_changed ?? now,
       load_count: (prev?.load_count ?? 0) + 1,
       fingerprint: fingerprint(core),
+      themes: prev?.themes,
     }
     const state: State = !prev ? "first" : prev.fingerprint === entry.fingerprint ? "same" : "updated"
     if (state === "updated") entry.time_changed = now
@@ -158,6 +167,20 @@ export namespace PluginMeta {
     })
   }

+  export async function setTheme(id: string, name: string, theme: Theme): Promise<void> {
+    const file = storePath()
+    await Flock.withLock(lock(file), async () => {
+      const store = await read(file)
+      const entry = store[id]
+      if (!entry) return
+      entry.themes = {
+        ...(entry.themes ?? {}),
+        [name]: theme,
+      }
+      await Filesystem.writeJson(file, store)
+    })
+  }
+
   export async function list(): Promise<Store> {
     const file = storePath()
     return Flock.withLock(lock(file), async () => read(file))
diff --git a/packages/opencode/src/util/filesystem.ts b/packages/opencode/src/util/filesystem.ts
index 37f00c6b9c8..d8318c481f4 100644
--- a/packages/opencode/src/util/filesystem.ts
+++ b/packages/opencode/src/util/filesystem.ts
@@ -1,4 +1,4 @@
-import { chmod, mkdir, readFile, writeFile } from "fs/promises"
+import { chmod, mkdir, readFile, stat as statFile, writeFile } from "fs/promises"
 import { createWriteStream, existsSync, statSync } from "fs"
 import { lookup } from "mime-types"
 import { realpathSync } from "fs"
@@ -25,6 +25,13 @@ export namespace Filesystem {
     return statSync(p, { throwIfNoEntry: false }) ?? undefined
   }

+  export async function statAsync(p: string): Promise<ReturnType<typeof statSync> | undefined> {
+    return statFile(p).catch((e) => {
+      if (isEnoent(e)) return undefined
+      throw e
+    })
+  }
+
   export async function size(p: string): Promise<number> {
     const s = stat(p)?.size ?? 0
     return typeof s === "bigint" ? Number(s) : s

PATCH
