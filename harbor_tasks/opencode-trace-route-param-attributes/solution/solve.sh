#!/usr/bin/env bash
# Gold patch: opencode#23189 — auto-tag route spans with route params
set -euo pipefail

cd /workspace/opencode

# Idempotency: if the gold patch is already applied, exit successfully.
if grep -q "export function requestAttributes" \
        packages/opencode/src/server/routes/instance/trace.ts 2>/dev/null; then
    echo "Gold patch already applied, exiting."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/opencode/src/server/routes/instance/trace.ts b/packages/opencode/src/server/routes/instance/trace.ts
index 3e1f72d8b242..fca313b745c8 100644
--- a/packages/opencode/src/server/routes/instance/trace.ts
+++ b/packages/opencode/src/server/routes/instance/trace.ts
@@ -4,18 +4,31 @@ import { AppRuntime } from "@/effect/app-runtime"

 type AppEnv = Parameters<typeof AppRuntime.runPromise>[0] extends Effect.Effect<any, any, infer R> ? R : never

+// Build the base span attributes for an HTTP handler: method, path, and every
+// matched route param (sessionID, messageID, partID, providerID, ptyID, …)
+// prefixed with `opencode.`. This makes each request's root span searchable
+// by ID in motel without having to parse the path string.
+export interface RequestLike {
+  readonly req: {
+    readonly method: string
+    readonly url: string
+    param(): Record<string, string>
+  }
+}
+
+export function requestAttributes(c: RequestLike): Record<string, string> {
+  const attributes: Record<string, string> = {
+    "http.method": c.req.method,
+    "http.path": new URL(c.req.url).pathname,
+  }
+  for (const [key, value] of Object.entries(c.req.param())) {
+    attributes[`opencode.${key}`] = value
+  }
+  return attributes
+}
+
 export function runRequest<A, E>(name: string, c: Context, effect: Effect.Effect<A, E, AppEnv>) {
-  const url = new URL(c.req.url)
-  return AppRuntime.runPromise(
-    effect.pipe(
-      Effect.withSpan(name, {
-        attributes: {
-          "http.method": c.req.method,
-          "http.path": url.pathname,
-        },
-      }),
-    ),
-  )
+  return AppRuntime.runPromise(effect.pipe(Effect.withSpan(name, { attributes: requestAttributes(c) })))
 }

 export async function jsonRequest<C extends Context, A, E>(
diff --git a/packages/opencode/test/server/trace-attributes.test.ts b/packages/opencode/test/server/trace-attributes.test.ts
new file mode 100644
index 000000000000..376c81fc6269
--- /dev/null
+++ b/packages/opencode/test/server/trace-attributes.test.ts
@@ -0,0 +1,52 @@
+import { describe, expect, test } from "bun:test"
+import { requestAttributes } from "../../src/server/routes/instance/trace"
+
+function fakeContext(method: string, url: string, params: Record<string, string>) {
+  return {
+    req: {
+      method,
+      url,
+      param: () => params,
+    },
+  }
+}
+
+describe("requestAttributes", () => {
+  test("includes http method and path", () => {
+    const attrs = requestAttributes(fakeContext("GET", "http://localhost/session", {}))
+    expect(attrs["http.method"]).toBe("GET")
+    expect(attrs["http.path"]).toBe("/session")
+  })
+
+  test("strips query string from path", () => {
+    const attrs = requestAttributes(fakeContext("GET", "http://localhost/file/search?query=foo&limit=10", {}))
+    expect(attrs["http.path"]).toBe("/file/search")
+  })
+
+  test("tags route params with opencode.<param> prefix", () => {
+    const attrs = requestAttributes(
+      fakeContext("GET", "http://localhost/session/ses_abc/message/msg_def/part/prt_ghi", {
+        sessionID: "ses_abc",
+        messageID: "msg_def",
+        partID: "prt_ghi",
+      }),
+    )
+    expect(attrs["opencode.sessionID"]).toBe("ses_abc")
+    expect(attrs["opencode.messageID"]).toBe("msg_def")
+    expect(attrs["opencode.partID"]).toBe("prt_ghi")
+  })
+
+  test("produces no param attributes when no params are matched", () => {
+    const attrs = requestAttributes(fakeContext("POST", "http://localhost/config", {}))
+    expect(Object.keys(attrs).filter((k) => k.startsWith("opencode."))).toEqual([])
+  })
+
+  test("handles non-ID params (e.g. mcp :name) without mangling", () => {
+    const attrs = requestAttributes(
+      fakeContext("POST", "http://localhost/mcp/exa/connect", {
+        name: "exa",
+      }),
+    )
+    expect(attrs["opencode.name"]).toBe("exa")
+  })
+})
PATCH

echo "Gold patch applied successfully."
