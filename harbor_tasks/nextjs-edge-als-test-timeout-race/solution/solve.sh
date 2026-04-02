#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency check: if nextTestSetup is already imported, patch was applied
if grep -q 'nextTestSetup' test/e2e/edge-async-local-storage/index.test.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/test/e2e/edge-async-local-storage/index.test.ts b/test/e2e/edge-async-local-storage/index.test.ts
index d426c3f6068e1f..cc747af35e3d2c 100644
--- a/test/e2e/edge-async-local-storage/index.test.ts
+++ b/test/e2e/edge-async-local-storage/index.test.ts
@@ -1,64 +1,22 @@
-import { createNext } from 'e2e-utils'
-import { NextInstance } from 'e2e-utils'
+import { nextTestSetup } from 'e2e-utils'
 import { fetchViaHTTP } from 'next-test-utils'

 describe('edge api can use async local storage', () => {
-  let next: NextInstance
+  const { next } = nextTestSetup({
+    files: __dirname,
+  })

   const cases = [
     {
       title: 'a single instance',
-      code: `
-        export const config = { runtime: 'edge' }
-        const storage = new AsyncLocalStorage()
-
-        export default async function handler(request) {
-          const id = request.headers.get('req-id')
-          return storage.run({ id }, async () => {
-            await getSomeData()
-            return Response.json(storage.getStore())
-          })
-        }
-
-        async function getSomeData() {
-          try {
-            const response = await fetch('https://example.vercel.sh')
-            await response.text()
-          } finally {
-            return true
-          }
-        }
-      `,
-      expectResponse: (response, id) =>
+      route: '/api/single',
+      expectResponse: (response: any, id: string) =>
         expect(response).toMatchObject({ status: 200, json: { id } }),
     },
     {
       title: 'multiple instances',
-      code: `
-        export const config = { runtime: 'edge' }
-        const topStorage = new AsyncLocalStorage()
-
-        export default async function handler(request) {
-          const id = request.headers.get('req-id')
-          return topStorage.run({ id }, async () => {
-            const nested = await getSomeData(id)
-            return Response.json({ ...nested, ...topStorage.getStore() })
-          })
-        }
-
-        async function getSomeData(id) {
-          const nestedStorage = new AsyncLocalStorage()
-          return nestedStorage.run('nested-' + id, async () => {
-            try {
-              const response = await fetch('https://example.vercel.sh')
-              await response.text()
-            } finally {
-              return { nestedId: nestedStorage.getStore() }
-            }
-          })
-        }
-      `,
-      expectResponse: (response, id) =>
+      route: '/api/multiple',
+      expectResponse: (response: any, id: string) =>
         expect(response).toMatchObject({
           status: 200,
           json: { id: id, nestedId: `nested-${id}` },
@@ -66,40 +24,28 @@ describe('edge api can use async local storage', () => {
     },
   ]

-  afterEach(() => next.destroy())
-
   it.each(cases)(
-    'cans use $title per request',
-    async ({ code, expectResponse }) => {
-      next = await createNext({
-        files: {
-          'pages/index.js': `
-            export default function () { return <div>Hello, world!</div> }
-          `,
-          'pages/api/async.js': code,
-        },
-      })
+    'can use $title per request',
+    async ({ route, expectResponse }) => {
       const ids = Array.from({ length: 100 }, (_, i) => `req-${i}`)

       const responses = await Promise.all(
         ids.map((id) =>
-          fetchViaHTTP(
-            next.url,
-            '/api/async',
-            {},
-            { headers: { 'req-id': id } }
-          ).then((response) =>
-            response.headers.get('content-type')?.startsWith('application/json')
-              ? response.json().then((json) => ({
-                  status: response.status,
-                  json,
-                  text: null,
-                }))
-              : response.text().then((text) => ({
-                  status: response.status,
-                  json: null,
-                  text,
-                }))
+          fetchViaHTTP(next.url, route, {}, { headers: { 'req-id': id } }).then(
+            (response) =>
+              response.headers
+                .get('content-type')
+                ?.startsWith('application/json')
+                ? response.json().then((json) => ({
+                    status: response.status,
+                    json,
+                    text: null,
+                  }))
+                : response.text().then((text) => ({
+                    status: response.status,
+                    json: null,
+                    text,
+                  }))
           )
         )
       )
diff --git a/test/e2e/edge-async-local-storage/pages/api/multiple.js b/test/e2e/edge-async-local-storage/pages/api/multiple.js
new file mode 100644
index 00000000000000..98a474da802390
--- /dev/null
+++ b/test/e2e/edge-async-local-storage/pages/api/multiple.js
@@ -0,0 +1,24 @@
+export const config = { runtime: 'edge' }
+// eslint-disable-next-line no-undef
+const topStorage = new AsyncLocalStorage()
+
+export default async function handler(request) {
+  const id = request.headers.get('req-id')
+  return topStorage.run({ id }, async () => {
+    const nested = await getSomeData(id)
+    return Response.json({ ...nested, ...topStorage.getStore() })
+  })
+}
+
+async function getSomeData(id) {
+  // eslint-disable-next-line no-undef
+  const nestedStorage = new AsyncLocalStorage()
+  return nestedStorage.run('nested-' + id, async () => {
+    try {
+      const response = await fetch('https://example.vercel.sh')
+      await response.text()
+    } finally {
+      return { nestedId: nestedStorage.getStore() }
+    }
+  })
+}
diff --git a/test/e2e/edge-async-local-storage/pages/api/single.js b/test/e2e/edge-async-local-storage/pages/api/single.js
new file mode 100644
index 00000000000000..79a89915cd7932
--- /dev/null
+++ b/test/e2e/edge-async-local-storage/pages/api/single.js
@@ -0,0 +1,20 @@
+export const config = { runtime: 'edge' }
+// eslint-disable-next-line no-undef
+const storage = new AsyncLocalStorage()
+
+export default async function handler(request) {
+  const id = request.headers.get('req-id')
+  return storage.run({ id }, async () => {
+    await getSomeData()
+    return Response.json(storage.getStore())
+  })
+}
+
+async function getSomeData() {
+  try {
+    const response = await fetch('https://example.vercel.sh')
+    await response.text()
+  } finally {
+    return true
+  }
+}

PATCH

echo "Patch applied successfully."
