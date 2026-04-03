#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if already fixed (spyOn used instead of mock.module in thread.test.ts)
if grep -q 'spyOn(App, "tui")' packages/opencode/test/cli/tui/thread.test.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/test/cli/tui/thread.test.ts b/packages/opencode/test/cli/tui/thread.test.ts
index d3de7c3183d..176c2575a30 100644
--- a/packages/opencode/test/cli/tui/thread.test.ts
+++ b/packages/opencode/test/cli/tui/thread.test.ts
@@ -1,7 +1,15 @@
-import { describe, expect, mock, test } from "bun:test"
+import { afterEach, describe, expect, mock, spyOn, test } from "bun:test"
 import fs from "fs/promises"
 import path from "path"
 import { tmpdir } from "../../fixture/fixture"
+import * as App from "../../../src/cli/cmd/tui/app"
+import { Rpc } from "../../../src/util/rpc"
+import { UI } from "../../../src/cli/ui"
+import * as Timeout from "../../../src/util/timeout"
+import * as Network from "../../../src/cli/network"
+import * as Win32 from "../../../src/cli/cmd/tui/win32"
+import { TuiConfig } from "../../../src/config/tui"
+import { Instance } from "../../../src/project/instance"

 const stop = new Error("stop")
 const seen = {
@@ -9,81 +17,43 @@ const seen = {
   inst: [] as string[],
 }

-mock.module("../../../src/cli/cmd/tui/app", () => ({
-  tui: async (input: { directory: string }) => {
-    seen.tui.push(input.directory)
+function setup() {
+  // Intentionally avoid mock.module() here: Bun keeps module overrides in cache
+  // and mock.restore() does not reset mock.module values. If this switches back
+  // to module mocks, later suites can see mocked @/config/tui and fail (e.g.
+  // plugin-loader tests expecting real TuiConfig.waitForDependencies). See:
+  // https://github.com/oven-sh/bun/issues/7823 and #12823.
+  spyOn(App, "tui").mockImplementation(async (input) => {
+    if (input.directory) seen.tui.push(input.directory)
     throw stop
-  },
-}))
-
-mock.module("@/util/rpc", () => ({
-  Rpc: {
-    client: () => ({
-      call: async () => ({ url: "http://127.0.0.1" }),
-      on: () => {},
-    }),
-  },
-}))
-
-mock.module("@/cli/ui", () => ({
-  UI: {
-    error: () => {},
-  },
-}))
-
-mock.module("@/util/log", () => ({
-  Log: {
-    init: async () => {},
-    create: () => ({
-      error: () => {},
-      info: () => {},
-      warn: () => {},
-      debug: () => {},
-      time: () => ({ stop: () => {} }),
-    }),
-    Default: {
-      error: () => {},
-      info: () => {},
-      warn: () => {},
-      debug: () => {},
-    },
-  },
-}))
-
-mock.module("@/util/timeout", () => ({
-  withTimeout: <T>(input: Promise<T>) => input,
-}))
-
-mock.module("@/cli/network", () => ({
-  withNetworkOptions: <T>(input: T) => input,
-  resolveNetworkOptions: async () => ({
+  })
+  spyOn(Rpc, "client").mockImplementation(() => ({
+    call: async () => ({ url: "http://127.0.0.1" }) as never,
+    on: () => () => {},
+  }))
+  spyOn(UI, "error").mockImplementation(() => {})
+  spyOn(Timeout, "withTimeout").mockImplementation((input) => input)
+  spyOn(Network, "resolveNetworkOptions").mockResolvedValue({
     mdns: false,
     port: 0,
     hostname: "127.0.0.1",
-  }),
-}))
-
-mock.module("../../../src/cli/cmd/tui/win32", () => ({
-  win32DisableProcessedInput: () => {},
-  win32InstallCtrlCGuard: () => undefined,
-}))
-
-mock.module("@/config/tui", () => ({
-  TuiConfig: {
-    get: () => ({}),
-  },
-}))
-
-mock.module("@/project/instance", () => ({
-  Instance: {
-    provide: async (input: { directory: string; fn: () => Promise<unknown> | unknown }) => {
-      seen.inst.push(input.directory)
-      return input.fn()
-    },
-  },
-}))
+    mdnsDomain: "opencode.local",
+    cors: [],
+  })
+  spyOn(Win32, "win32DisableProcessedInput").mockImplementation(() => {})
+  spyOn(Win32, "win32InstallCtrlCGuard").mockReturnValue(undefined)
+  spyOn(TuiConfig, "get").mockResolvedValue({})
+  spyOn(Instance, "provide").mockImplementation(async (input) => {
+    seen.inst.push(input.directory)
+    return input.fn()
+  })
+}

 describe("tui thread", () => {
+  afterEach(() => {
+    mock.restore()
+  })
+
   async function call(project?: string) {
     const { TuiThreadCommand } = await import("../../../src/cli/cmd/tui/thread")
     const args: Parameters<NonNullable<typeof TuiThreadCommand.handler>>[0] = {
@@ -107,6 +77,7 @@ describe("tui thread", () => {
   }

   async function check(project?: string) {
+    setup()
     await using tmp = await tmpdir({ git: true })
     const cwd = process.cwd()
     const pwd = process.env.PWD
diff --git a/packages/opencode/test/config/config.test.ts b/packages/opencode/test/config/config.test.ts
index aa49aa4bd50..ea0a5452000 100644
--- a/packages/opencode/test/config/config.test.ts
+++ b/packages/opencode/test/config/config.test.ts
@@ -821,9 +821,12 @@ test("dedupes concurrent config dependency installs for the same dir", async ()
   })
   const online = spyOn(Network, "online").mockReturnValue(false)
   const run = spyOn(BunProc, "run").mockImplementation(async (_cmd, opts) => {
-    calls += 1
-    start()
-    await gate
+    const hit = path.normalize(opts?.cwd ?? "") === path.normalize(dir)
+    if (hit) {
+      calls += 1
+      start()
+      await gate
+    }
     const mod = path.join(opts?.cwd ?? "", "node_modules", "@opencode-ai", "plugin")
     await fs.mkdir(mod, { recursive: true })
     await Filesystem.write(
@@ -883,12 +886,16 @@ test("serializes config dependency installs across dirs", async () => {

   const online = spyOn(Network, "online").mockReturnValue(false)
   const run = spyOn(BunProc, "run").mockImplementation(async (_cmd, opts) => {
-    calls += 1
-    open += 1
-    peak = Math.max(peak, open)
-    if (calls === 1) {
-      start()
-      await gate
+    const cwd = path.normalize(opts?.cwd ?? "")
+    const hit = cwd === path.normalize(a) || cwd === path.normalize(b)
+    if (hit) {
+      calls += 1
+      open += 1
+      peak = Math.max(peak, open)
+      if (calls === 1) {
+        start()
+        await gate
+      }
     }
     const mod = path.join(opts?.cwd ?? "", "node_modules", "@opencode-ai", "plugin")
     await fs.mkdir(mod, { recursive: true })
@@ -896,7 +903,9 @@ test("serializes config dependency installs across dirs", async () => {
       path.join(mod, "package.json"),
       JSON.stringify({ name: "@opencode-ai/plugin", version: "1.0.0" }),
     )
-    open -= 1
+    if (hit) {
+      open -= 1
+    }
     return {
       code: 0,
       stdout: Buffer.alloc(0),

PATCH
