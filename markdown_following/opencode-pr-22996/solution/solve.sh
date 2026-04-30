#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency guard: distinctive line introduced by the gold patch
if grep -q 'export function jsonc(text: string, filepath: string): unknown' \
   packages/opencode/src/config/parse.ts 2>/dev/null; then
  echo "Gold patch already applied; skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/opencode/src/cli/cmd/tui/config/tui.ts b/packages/opencode/src/cli/cmd/tui/config/tui.ts
index b55cf3b83f96..1a5e49badb6f 100644
--- a/packages/opencode/src/cli/cmd/tui/config/tui.ts
+++ b/packages/opencode/src/cli/cmd/tui/config/tui.ts
@@ -18,6 +18,7 @@ import { ConfigKeybinds } from "@/config/keybinds"
 import { InstallationLocal, InstallationVersion } from "@/installation/version"
 import { makeRuntime } from "@/cli/effect/runtime"
 import { Filesystem, Log } from "@/util"
+import { ConfigVariable } from "@/config/variable"

 const log = Log.create({ service: "tui.config" })

@@ -197,18 +198,15 @@ async function loadFile(filepath: string): Promise<Info> {
 }

 async function load(text: string, configFilepath: string): Promise<Info> {
-  return ConfigParse.load(Info, text, {
-    type: "path",
-    path: configFilepath,
-    missing: "empty",
-    normalize: (data) => {
+  return ConfigVariable.substitute({ text, type: "path", path: configFilepath, missing: "empty" })
+    .then((expanded) => ConfigParse.jsonc(expanded, configFilepath))
+    .then((data) => {
       if (!isRecord(data)) return {}

       // Flatten a nested "tui" key so users who wrote `{ "tui": { ... } }` inside tui.json
       // (mirroring the old opencode.json shape) still get their settings applied.
-      return normalize(data)
-    },
-  })
+      return ConfigParse.schema(Info, normalize(data), configFilepath)
+    })
     .then((data) => resolvePlugins(data, configFilepath))
     .catch((error) => {
       log.warn("invalid tui config", { path: configFilepath, error })
diff --git a/packages/opencode/src/config/config.ts b/packages/opencode/src/config/config.ts
index 2edc455df32f..ecc419e65aaf 100644
--- a/packages/opencode/src/config/config.ts
+++ b/packages/opencode/src/config/config.ts
@@ -38,6 +38,7 @@ import { ConfigSkills } from "./skills"
 import { ConfigPaths } from "./paths"
 import { ConfigFormatter } from "./formatter"
 import { ConfigLSP } from "./lsp"
+import { ConfigVariable } from "./variable"

 const log = Log.create({ service: "config" })

@@ -327,24 +328,16 @@ export const layer = Layer.effect(
       text: string,
       options: { path: string } | { dir: string; source: string },
     ) {
-      if (!("path" in options)) {
-        return yield* Effect.promise(() =>
-          ConfigParse.load(Info, text, {
-            type: "virtual",
-            dir: options.dir,
-            source: options.source,
-            normalize: normalizeLoadedConfig,
-          }),
-        )
-      }
-
-      const data = yield* Effect.promise(() =>
-        ConfigParse.load(Info, text, {
-          type: "path",
-          path: options.path,
-          normalize: normalizeLoadedConfig,
-        }),
+      const source = "path" in options ? options.path : options.source
+      const expanded = yield* Effect.promise(() =>
+        ConfigVariable.substitute(
+          "path" in options ? { text, type: "path", path: options.path } : { text, type: "virtual", ...options },
+        ),
       )
+      const parsed = ConfigParse.jsonc(expanded, source)
+      const data = ConfigParse.schema(Info, normalizeLoadedConfig(parsed, source), source)
+      if (!("path" in options)) return data
+
       yield* Effect.promise(() => resolveLoadedPlugins(data, options.path))
       if (!data.$schema) {
         data.$schema = "https://opencode.ai/config.json"
@@ -725,17 +718,16 @@ export const layer = Layer.effect(
     const updateGlobal = Effect.fn("Config.updateGlobal")(function* (config: Info) {
       const file = globalConfigFile()
       const before = (yield* readConfigFile(file)) ?? "{}"
-      const input = writable(config)

       let next: Info
       if (!file.endsWith(".jsonc")) {
-        const existing = ConfigParse.parse(Info, before, file)
-        const merged = mergeDeep(writable(existing), input)
+        const existing = ConfigParse.schema(Info, ConfigParse.jsonc(before, file), file)
+        const merged = mergeDeep(writable(existing), writable(config))
         yield* fs.writeFileString(file, JSON.stringify(merged, null, 2)).pipe(Effect.orDie)
         next = merged
       } else {
-        const updated = patchJsonc(before, input)
-        next = ConfigParse.parse(Info, updated, file)
+        const updated = patchJsonc(before, writable(config))
+        next = ConfigParse.schema(Info, ConfigParse.jsonc(updated, file), file)
         yield* fs.writeFileString(file, updated).pipe(Effect.orDie)
       }

diff --git a/packages/opencode/src/config/parse.ts b/packages/opencode/src/config/parse.ts
index 65cc483859b5..7472029ead54 100644
--- a/packages/opencode/src/config/parse.ts
+++ b/packages/opencode/src/config/parse.ts
@@ -1,80 +1,44 @@
 export * as ConfigParse from "./parse"

-import { type ParseError as JsoncParseError, parse as parseJsonc, printParseErrorCode } from "jsonc-parser"
+import { type ParseError as JsoncParseError, parse as parseJsoncImpl, printParseErrorCode } from "jsonc-parser"
 import z from "zod"
-import { ConfigVariable } from "./variable"
 import { InvalidError, JsonError } from "./error"

 type Schema<T> = z.ZodType<T>
-type VariableMode = "error" | "empty"

-export type LoadOptions =
-  | {
-      type: "path"
-      path: string
-      missing?: VariableMode
-      normalize?: (data: unknown, source: string) => unknown
-    }
-  | {
-      type: "virtual"
-      dir: string
-      source: string
-      missing?: VariableMode
-      normalize?: (data: unknown, source: string) => unknown
-    }
-
-function issues(text: string, errors: JsoncParseError[]) {
-  const lines = text.split("\n")
-  return errors
-    .map((e) => {
-      const beforeOffset = text.substring(0, e.offset).split("\n")
-      const line = beforeOffset.length
-      const column = beforeOffset[beforeOffset.length - 1].length + 1
-      const problemLine = lines[line - 1]
-
-      const error = `${printParseErrorCode(e.error)} at line ${line}, column ${column}`
-      if (!problemLine) return error
-
-      return `${error}\n   Line ${line}: ${problemLine}\n${"".padStart(column + 9)}^`
-    })
-    .join("\n")
-}
-
-export function parse<T>(schema: Schema<T>, text: string, filepath: string): T {
+export function jsonc(text: string, filepath: string): unknown {
   const errors: JsoncParseError[] = []
-  const data = parseJsonc(text, errors, { allowTrailingComma: true })
+  const data = parseJsoncImpl(text, errors, { allowTrailingComma: true })
   if (errors.length) {
+    const lines = text.split("\n")
+    const issues = errors
+      .map((e) => {
+        const beforeOffset = text.substring(0, e.offset).split("\n")
+        const line = beforeOffset.length
+        const column = beforeOffset[beforeOffset.length - 1].length + 1
+        const problemLine = lines[line - 1]
+
+        const error = `${printParseErrorCode(e.error)} at line ${line}, column ${column}`
+        if (!problemLine) return error
+
+        return `${error}\n   Line ${line}: ${problemLine}\n${"".padStart(column + 9)}^`
+      })
+      .join("\n")
     throw new JsonError({
       path: filepath,
-      message: `\n--- JSONC Input ---\n${text}\n--- Errors ---\n${issues(text, errors)}\n--- End ---`,
+      message: `\n--- JSONC Input ---\n${text}\n--- Errors ---\n${issues}\n--- End ---`,
     })
   }

+  return data
+}
+
+export function schema<T>(schema: Schema<T>, data: unknown, source: string): T {
   const parsed = schema.safeParse(data)
   if (parsed.success) return parsed.data

   throw new InvalidError({
-    path: filepath,
+    path: source,
     issues: parsed.error.issues,
   })
 }
-
-export async function load<T>(schema: Schema<T>, text: string, options: LoadOptions): Promise<T> {
-  const source = options.type === "path" ? options.path : options.source
-  const expanded = await ConfigVariable.substitute(
-    text,
-    options.type === "path" ? { type: "path", path: options.path } : options,
-    options.missing,
-  )
-  const data = parse(z.unknown(), expanded, source)
-  const normalized = options.normalize ? options.normalize(data, source) : data
-  const parsed = schema.safeParse(normalized)
-  if (!parsed.success) {
-    throw new InvalidError({
-      path: source,
-      issues: parsed.error.issues,
-    })
-  }
-
-  return parsed.data
-}
diff --git a/packages/opencode/src/config/variable.ts b/packages/opencode/src/config/variable.ts
index e016e33a210a..e52db6147c93 100644
--- a/packages/opencode/src/config/variable.ts
+++ b/packages/opencode/src/config/variable.ts
@@ -16,6 +16,11 @@ type ParseSource =
       dir: string
     }

+type SubstituteInput = ParseSource & {
+  text: string
+  missing?: "error" | "empty"
+}
+
 function source(input: ParseSource) {
   return input.type === "path" ? input.path : input.source
 }
@@ -25,8 +30,9 @@ function dir(input: ParseSource) {
 }

 /** Apply {env:VAR} and {file:path} substitutions to config text. */
-export async function substitute(text: string, input: ParseSource, missing: "error" | "empty" = "error") {
-  text = text.replace(/\{env:([^}]+)\}/g, (_, varName) => {
+export async function substitute(input: SubstituteInput) {
+  const missing = input.missing ?? "error"
+  let text = input.text.replace(/\{env:([^}]+)\}/g, (_, varName) => {
     return process.env[varName] || ""
   })

diff --git a/packages/opencode/test/config/config.test.ts b/packages/opencode/test/config/config.test.ts
index 3e90842e1885..d4870beaf032 100644
--- a/packages/opencode/test/config/config.test.ts
+++ b/packages/opencode/test/config/config.test.ts
@@ -2212,19 +2212,22 @@ describe("OPENCODE_CONFIG_CONTENT token substitution", () => {
 // parseManagedPlist unit tests — pure function, no OS interaction

 test("parseManagedPlist strips MDM metadata keys", async () => {
-  const config = ConfigParse.parse(
+  const config = ConfigParse.schema(
     Config.Info,
-    await ConfigManaged.parseManagedPlist(
-      JSON.stringify({
-        PayloadDisplayName: "OpenCode Managed",
-        PayloadIdentifier: "ai.opencode.managed.test",
-        PayloadType: "ai.opencode.managed",
-        PayloadUUID: "AAAA-BBBB-CCCC",
-        PayloadVersion: 1,
-        _manualProfile: true,
-        share: "disabled",
-        model: "mdm/model",
-      }),
+    ConfigParse.jsonc(
+      await ConfigManaged.parseManagedPlist(
+        JSON.stringify({
+          PayloadDisplayName: "OpenCode Managed",
+          PayloadIdentifier: "ai.opencode.managed.test",
+          PayloadType: "ai.opencode.managed",
+          PayloadUUID: "AAAA-BBBB-CCCC",
+          PayloadVersion: 1,
+          _manualProfile: true,
+          share: "disabled",
+          model: "mdm/model",
+        }),
+      ),
+      "test:mobileconfig",
     ),
     "test:mobileconfig",
   )
@@ -2237,14 +2240,17 @@ test("parseManagedPlist strips MDM metadata keys", async () => {
 })

 test("parseManagedPlist parses server settings", async () => {
-  const config = ConfigParse.parse(
+  const config = ConfigParse.schema(
     Config.Info,
-    await ConfigManaged.parseManagedPlist(
-      JSON.stringify({
-        $schema: "https://opencode.ai/config.json",
-        server: { hostname: "127.0.0.1", mdns: false },
-        autoupdate: true,
-      }),
+    ConfigParse.jsonc(
+      await ConfigManaged.parseManagedPlist(
+        JSON.stringify({
+          $schema: "https://opencode.ai/config.json",
+          server: { hostname: "127.0.0.1", mdns: false },
+          autoupdate: true,
+        }),
+      ),
+      "test:mobileconfig",
     ),
     "test:mobileconfig",
   )
@@ -2254,20 +2260,23 @@ test("parseManagedPlist parses server settings", async () => {
 })

 test("parseManagedPlist parses permission rules", async () => {
-  const config = ConfigParse.parse(
+  const config = ConfigParse.schema(
     Config.Info,
-    await ConfigManaged.parseManagedPlist(
-      JSON.stringify({
-        $schema: "https://opencode.ai/config.json",
-        permission: {
-          "*": "ask",
-          bash: { "*": "ask", "rm -rf *": "deny", "curl *": "deny" },
-          grep: "allow",
-          glob: "allow",
-          webfetch: "ask",
-          "~/.ssh/*": "deny",
-        },
-      }),
+    ConfigParse.jsonc(
+      await ConfigManaged.parseManagedPlist(
+        JSON.stringify({
+          $schema: "https://opencode.ai/config.json",
+          permission: {
+            "*": "ask",
+            bash: { "*": "ask", "rm -rf *": "deny", "curl *": "deny" },
+            grep: "allow",
+            glob: "allow",
+            webfetch: "ask",
+            "~/.ssh/*": "deny",
+          },
+        }),
+      ),
+      "test:mobileconfig",
     ),
     "test:mobileconfig",
   )
@@ -2281,13 +2290,16 @@ test("parseManagedPlist parses permission rules", async () => {
 })

 test("parseManagedPlist parses enabled_providers", async () => {
-  const config = ConfigParse.parse(
+  const config = ConfigParse.schema(
     Config.Info,
-    await ConfigManaged.parseManagedPlist(
-      JSON.stringify({
-        $schema: "https://opencode.ai/config.json",
-        enabled_providers: ["anthropic", "google"],
-      }),
+    ConfigParse.jsonc(
+      await ConfigManaged.parseManagedPlist(
+        JSON.stringify({
+          $schema: "https://opencode.ai/config.json",
+          enabled_providers: ["anthropic", "google"],
+        }),
+      ),
+      "test:mobileconfig",
     ),
     "test:mobileconfig",
   )
@@ -2295,9 +2307,12 @@ test("parseManagedPlist parses enabled_providers", async () => {
 })

 test("parseManagedPlist handles empty config", async () => {
-  const config = ConfigParse.parse(
+  const config = ConfigParse.schema(
     Config.Info,
-    await ConfigManaged.parseManagedPlist(JSON.stringify({ $schema: "https://opencode.ai/config.json" })),
+    ConfigParse.jsonc(
+      await ConfigManaged.parseManagedPlist(JSON.stringify({ $schema: "https://opencode.ai/config.json" })),
+      "test:mobileconfig",
+    ),
     "test:mobileconfig",
   )
   expect(config.$schema).toBe("https://opencode.ai/config.json")
PATCH

echo "Gold patch applied."
