#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'webToReadable cannot be used in the edge runtime' packages/next/src/server/stream-utils/node-web-streams-helper.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/errors.json b/packages/next/errors.json
index 2e4d2622d105a9..507a6bbffc9005 100644
--- a/packages/next/errors.json
+++ b/packages/next/errors.json
@@ -1145,5 +1145,8 @@
   "1144": "Prefetch inlining is enabled but no hints were found for route \"%s\". This is a bug in the Next.js build pipeline — prefetch-hints.json should contain an entry for every route that produces segment data.",
   "1145": "Internal Next.js Error: Prefetch inlining is enabled but no hints were found for route \"%s\". prefetch-hints.json should contain an entry for every route that produces segment data. This is a bug in Next.js.",
   "1146": "Internal Next.js Error: Prefetch inlining is enabled but no hint tree was provided during incremental static revalidation. The prefetch-hints.json manifest should contain an entry for this route. This is a bug in Next.js.",
-  "1147": "Turbopack database compaction is not supported on this platform"
+  "1147": "Turbopack database compaction is not supported on this platform",
+  "1148": "webToReadable cannot be used in the edge runtime",
+  "1149": "Node.js Readable cannot be teed in the edge runtime",
+  "1150": "Node.js Readable cannot be converted to a web stream in the edge runtime"
 }
diff --git a/packages/next/src/server/app-render/app-render-prerender-utils.ts b/packages/next/src/server/app-render/app-render-prerender-utils.ts
index 6b2349f4548b83..dbe31040e4f21c 100644
--- a/packages/next/src/server/app-render/app-render-prerender-utils.ts
+++ b/packages/next/src/server/app-render/app-render-prerender-utils.ts
@@ -30,21 +30,29 @@ export class ReactServerResult {
       return tee[1]
     }

-    let Readable: typeof import('node:stream').Readable
-    if (process.env.TURBOPACK) {
-      Readable = (require('node:stream') as typeof import('node:stream'))
-        .Readable
+    if (process.env.NEXT_RUNTIME === 'edge') {
+      throw new InvariantError(
+        'Node.js Readable cannot be teed in the edge runtime'
+      )
     } else {
-      Readable = (
-        __non_webpack_require__('node:stream') as typeof import('node:stream')
-      ).Readable
+      let Readable: typeof import('node:stream').Readable
+      if (process.env.TURBOPACK) {
+        Readable = (require('node:stream') as typeof import('node:stream'))
+          .Readable
+      } else {
+        Readable = (
+          __non_webpack_require__('node:stream') as typeof import('node:stream')
+        ).Readable
+      }
+      const webStream = Readable.toWeb(
+        this._stream
+      ) as ReadableStream<Uint8Array>
+      const tee = webStream.tee()
+      this._stream = Readable.fromWeb(
+        tee[0] as import('stream/web').ReadableStream
+      )
+      return Readable.fromWeb(tee[1] as import('stream/web').ReadableStream)
     }
-    const webStream = Readable.toWeb(this._stream) as ReadableStream<Uint8Array>
-    const tee = webStream.tee()
-    this._stream = Readable.fromWeb(
-      tee[0] as import('stream/web').ReadableStream
-    )
-    return Readable.fromWeb(tee[1] as import('stream/web').ReadableStream)
   }

   consume(): AnyStream {
diff --git a/packages/next/src/server/render-result.ts b/packages/next/src/server/render-result.ts
index 421c89220d927a..a9f4fe0e74c28e 100644
--- a/packages/next/src/server/render-result.ts
+++ b/packages/next/src/server/render-result.ts
@@ -248,16 +248,24 @@ export default class RenderResult<
     }

     if (isNodeReadable(this.response)) {
-      let Readable: typeof import('node:stream').Readable
-      if (process.env.TURBOPACK) {
-        Readable = (require('node:stream') as typeof import('node:stream'))
-          .Readable
+      if (process.env.NEXT_RUNTIME === 'edge') {
+        throw new InvariantError(
+          'Node.js Readable cannot be converted to a web stream in the edge runtime'
+        )
       } else {
-        Readable = (
-          __non_webpack_require__('node:stream') as typeof import('node:stream')
-        ).Readable
+        let Readable: typeof import('node:stream').Readable
+        if (process.env.TURBOPACK) {
+          Readable = (require('node:stream') as typeof import('node:stream'))
+            .Readable
+        } else {
+          Readable = (
+            __non_webpack_require__(
+              'node:stream'
+            ) as typeof import('node:stream')
+          ).Readable
+        }
+        return Readable.toWeb(this.response) as ReadableStream<Uint8Array>
       }
-      return Readable.toWeb(this.response) as ReadableStream<Uint8Array>
     }

     return this.response
@@ -283,16 +291,24 @@ export default class RenderResult<
     } else if (Buffer.isBuffer(this.response)) {
       return [streamFromBuffer(this.response)]
     } else if (isNodeReadable(this.response)) {
-      let Readable: typeof import('node:stream').Readable
-      if (process.env.TURBOPACK) {
-        Readable = (require('node:stream') as typeof import('node:stream'))
-          .Readable
+      if (process.env.NEXT_RUNTIME === 'edge') {
+        throw new InvariantError(
+          'Node.js Readable cannot be converted to a web stream in the edge runtime'
+        )
       } else {
-        Readable = (
-          __non_webpack_require__('node:stream') as typeof import('node:stream')
-        ).Readable
+        let Readable: typeof import('node:stream').Readable
+        if (process.env.TURBOPACK) {
+          Readable = (require('node:stream') as typeof import('node:stream'))
+            .Readable
+        } else {
+          Readable = (
+            __non_webpack_require__(
+              'node:stream'
+            ) as typeof import('node:stream')
+          ).Readable
+        }
+        return [Readable.toWeb(this.response) as ReadableStream<Uint8Array>]
       }
-      return [Readable.toWeb(this.response) as ReadableStream<Uint8Array>]
     } else {
       return [this.response]
     }
diff --git a/packages/next/src/server/stream-utils/node-web-streams-helper.ts b/packages/next/src/server/stream-utils/node-web-streams-helper.ts
index aed8b3980260bb..a0961f8df9bee6 100644
--- a/packages/next/src/server/stream-utils/node-web-streams-helper.ts
+++ b/packages/next/src/server/stream-utils/node-web-streams-helper.ts
@@ -135,20 +135,26 @@ export async function webstreamToUint8Array(
 function webToReadable(
   stream: ReadableStream<Uint8Array> | import('node:stream').Readable
 ): import('node:stream').Readable {
-  let Readable: typeof import('node:stream').Readable
-  if (process.env.TURBOPACK) {
-    Readable = (require('node:stream') as typeof import('node:stream')).Readable
-  } else if (process.env.__NEXT_BUNDLER === 'Webpack') {
-    Readable = (
-      __non_webpack_require__('node:stream') as typeof import('node:stream')
-    ).Readable
+  if (process.env.NEXT_RUNTIME === 'edge') {
+    throw new Error('webToReadable cannot be used in the edge runtime')
   } else {
-    Readable = (require('node:stream') as typeof import('node:stream')).Readable
-  }
-  if (stream instanceof Readable) {
-    return stream
+    let Readable: typeof import('node:stream').Readable
+    if (process.env.TURBOPACK) {
+      Readable = (require('node:stream') as typeof import('node:stream'))
+        .Readable
+    } else if (process.env.__NEXT_BUNDLER === 'Webpack') {
+      Readable = (
+        __non_webpack_require__('node:stream') as typeof import('node:stream')
+      ).Readable
+    } else {
+      Readable = (require('node:stream') as typeof import('node:stream'))
+        .Readable
+    }
+    if (stream instanceof Readable) {
+      return stream
+    }
+    return Readable.fromWeb(stream as import('stream/web').ReadableStream)
   }
-  return Readable.fromWeb(stream as import('stream/web').ReadableStream)
 }

 export async function nodestreamToUint8Array(
@@ -162,20 +168,29 @@ export async function nodestreamToUint8Array(
 }

 export async function streamToUint8Array(stream: AnyStream) {
-  let Readable: typeof import('node:stream').Readable
-  if (process.env.TURBOPACK) {
-    Readable = (require('node:stream') as typeof import('node:stream')).Readable
-  } else if (process.env.__NEXT_BUNDLER === 'Webpack') {
-    Readable = (
-      __non_webpack_require__('node:stream') as typeof import('node:stream')
-    ).Readable
+  if (process.env.NEXT_RUNTIME === 'edge') {
+    // Edge runtime always uses web streams
+    return webstreamToUint8Array(stream as ReadableStream<Uint8Array>)
   } else {
-    Readable = (require('node:stream') as typeof import('node:stream')).Readable
-  }
-  if (stream instanceof Readable) {
-    return nodestreamToUint8Array(stream)
+    let Readable: typeof import('node:stream').Readable
+    if (process.env.TURBOPACK) {
+      Readable = (require('node:stream') as typeof import('node:stream'))
+        .Readable
+    } else if (process.env.__NEXT_BUNDLER === 'Webpack') {
+      Readable = (
+        __non_webpack_require__('node:stream') as typeof import('node:stream')
+      ).Readable
+    } else {
+      Readable = (require('node:stream') as typeof import('node:stream'))
+        .Readable
+    }
+
+    if (stream instanceof Readable) {
+      return nodestreamToUint8Array(stream)
+    }
+
+    return webstreamToUint8Array(stream)
   }
-  return webstreamToUint8Array(stream)
 }

 export async function streamToBuffer(

PATCH

echo "Patch applied successfully."
