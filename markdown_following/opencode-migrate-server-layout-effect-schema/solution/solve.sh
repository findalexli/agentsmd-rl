#!/bin/bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: if the migration has already been applied, do nothing.
if [ -f packages/opencode/src/config/server.ts ] && \
   grep -q 'ConfigServer.Server.zod' packages/opencode/src/config/config.ts 2>/dev/null; then
    echo "Gold patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/opencode/src/config/config.ts b/packages/opencode/src/config/config.ts
index bfb0c2f1f40b..179c6a609397 100644
--- a/packages/opencode/src/config/config.ts
+++ b/packages/opencode/src/config/config.ts
@@ -25,18 +25,20 @@ import { Context, Duration, Effect, Exit, Fiber, Layer, Option } from "effect"
 import { EffectFlock } from "@opencode-ai/shared/util/effect-flock"
 import { InstanceRef } from "@/effect/instance-ref"
 import { ConfigAgent } from "./agent"
+import { ConfigCommand } from "./command"
+import { ConfigFormatter } from "./formatter"
+import { ConfigLayout } from "./layout"
+import { ConfigLSP } from "./lsp"
+import { ConfigManaged } from "./managed"
 import { ConfigMCP } from "./mcp"
 import { ConfigModelID } from "./model-id"
-import { ConfigPlugin } from "./plugin"
-import { ConfigManaged } from "./managed"
-import { ConfigCommand } from "./command"
 import { ConfigParse } from "./parse"
+import { ConfigPaths } from "./paths"
 import { ConfigPermission } from "./permission"
+import { ConfigPlugin } from "./plugin"
 import { ConfigProvider } from "./provider"
+import { ConfigServer } from "./server"
 import { ConfigSkills } from "./skills"
-import { ConfigPaths } from "./paths"
-import { ConfigFormatter } from "./formatter"
-import { ConfigLSP } from "./lsp"
 import { ConfigVariable } from "./variable"
 import { Npm } from "@/npm"

@@ -73,23 +75,9 @@ async function resolveLoadedPlugins<T extends { plugin?: ConfigPlugin.Spec[] }>(
   return config
 }

-export const Server = z
-  .object({
-    port: z.number().int().positive().optional().describe("Port to listen on"),
-    hostname: z.string().optional().describe("Hostname to listen on"),
-    mdns: z.boolean().optional().describe("Enable mDNS service discovery"),
-    mdnsDomain: z.string().optional().describe("Custom domain name for mDNS service (default: opencode.local)"),
-    cors: z.array(z.string()).optional().describe("Additional domains to allow for CORS"),
-  })
-  .strict()
-  .meta({
-    ref: "ServerConfig",
-  })
-
-export const Layout = z.enum(["auto", "stretch"]).meta({
-  ref: "LayoutConfig",
-})
-export type Layout = z.infer<typeof Layout>
+export const Server = ConfigServer.Server.zod
+export const Layout = ConfigLayout.Layout.zod
+export type Layout = ConfigLayout.Layout

 export const Info = z
   .object({
diff --git a/packages/opencode/src/config/layout.ts b/packages/opencode/src/config/layout.ts
new file mode 100644
index 000000000000..49c34b66398b
--- /dev/null
+++ b/packages/opencode/src/config/layout.ts
@@ -0,0 +1,10 @@
+import { Schema } from "effect"
+import { zod } from "@/util/effect-zod"
+import { withStatics } from "@/util/schema"
+
+export const Layout = Schema.Literals(["auto", "stretch"])
+  .annotate({ identifier: "LayoutConfig" })
+  .pipe(withStatics((s) => ({ zod: zod(s) })))
+export type Layout = Schema.Schema.Type<typeof Layout>
+
+export * as ConfigLayout from "./layout"
diff --git a/packages/opencode/src/config/provider.ts b/packages/opencode/src/config/provider.ts
index 4b08592a657a..212e716251fd 100644
--- a/packages/opencode/src/config/provider.ts
+++ b/packages/opencode/src/config/provider.ts
@@ -2,8 +2,6 @@ import { Schema } from "effect"
 import { zod } from "@/util/effect-zod"
 import { withStatics } from "@/util/schema"

-// Positive integer: emits JSON Schema `type: integer, exclusiveMinimum: 0`
-// via the effect-zod walker's well-known refinement translation.
 const PositiveInt = Schema.Number.check(Schema.isInt()).check(Schema.isGreaterThan(0))

 export const Model = Schema.Struct({
diff --git a/packages/opencode/src/config/server.ts b/packages/opencode/src/config/server.ts
new file mode 100644
index 000000000000..969a79964b37
--- /dev/null
+++ b/packages/opencode/src/config/server.ts
@@ -0,0 +1,20 @@
+import { Schema } from "effect"
+import { zod } from "@/util/effect-zod"
+
+export class Server extends Schema.Class<Server>("ServerConfig")({
+  port: Schema.optional(Schema.Number.check(Schema.isInt()).check(Schema.isGreaterThan(0))).annotate({
+    description: "Port to listen on",
+  }),
+  hostname: Schema.optional(Schema.String).annotate({ description: "Hostname to listen on" }),
+  mdns: Schema.optional(Schema.Boolean).annotate({ description: "Enable mDNS service discovery" }),
+  mdnsDomain: Schema.optional(Schema.String).annotate({
+    description: "Custom domain name for mDNS service (default: opencode.local)",
+  }),
+  cors: Schema.optional(Schema.mutable(Schema.Array(Schema.String))).annotate({
+    description: "Additional domains to allow for CORS",
+  }),
+}) {
+  static readonly zod = zod(this)
+}
+
+export * as ConfigServer from "./server"
PATCH

echo "Gold patch applied."
