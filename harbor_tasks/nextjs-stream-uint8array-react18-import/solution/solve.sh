#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'webstreamToUint8Array' packages/next/src/server/stream-utils/node-web-streams-helper.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/server/app-render/stream-ops.node.ts b/packages/next/src/server/app-render/stream-ops.node.ts
index 4d1cd800f2580..74c775511ee85 100644
--- a/packages/next/src/server/app-render/stream-ops.node.ts
+++ b/packages/next/src/server/app-render/stream-ops.node.ts
@@ -357,16 +357,6 @@ export async function streamToBuffer(stream: AnyStream): Promise<Buffer> {
   return webStreamToBuffer(nodeReadableToWebReadableStream(stream))
 }

-export async function streamToUint8Array(
-  stream: AnyStream
-): Promise<Uint8Array> {
-  const chunks: Buffer[] = []
-  for await (const chunk of webToReadable(stream)) {
-    chunks.push(typeof chunk === 'string' ? Buffer.from(chunk) : chunk)
-  }
-  return Buffer.concat(chunks)
-}
-
 export async function streamToString(stream: AnyStream): Promise<string> {
   return webStreamToString(nodeReadableToWebReadableStream(stream))
 }
diff --git a/packages/next/src/server/app-render/stream-ops.ts b/packages/next/src/server/app-render/stream-ops.ts
index ae0614ba2e9c8..031cc409ee738 100644
--- a/packages/next/src/server/app-render/stream-ops.ts
+++ b/packages/next/src/server/app-render/stream-ops.ts
@@ -46,7 +46,6 @@ export const createOnHeadersCallback = _m.createOnHeadersCallback
 export const resumeAndAbort = _m.resumeAndAbort
 export const renderToFlightStream = _m.renderToFlightStream
 export const streamToString = _m.streamToString
-export const streamToUint8Array = _m.streamToUint8Array
 export const renderToFizzStream = _m.renderToFizzStream
 export const resumeToFizzStream = _m.resumeToFizzStream
 export const getServerPrerender = _m.getServerPrerender
diff --git a/packages/next/src/server/app-render/stream-ops.web.ts b/packages/next/src/server/app-render/stream-ops.web.ts
index b9107c4a35bed..e6c38589a85b0 100644
--- a/packages/next/src/server/app-render/stream-ops.web.ts
+++ b/packages/next/src/server/app-render/stream-ops.web.ts
@@ -20,7 +20,6 @@ import {
   continueStaticFallbackPrerender as webContinueStaticFallbackPrerender,
   continueDynamicHTMLResume as webContinueDynamicHTMLResume,
   streamToBuffer as webStreamToBuffer,
-  streamToUint8Array as webStreamToUint8Array,
   chainStreams as webChainStreams,
   createDocumentClosingStream as webCreateDocumentClosingStream,
 } from '../stream-utils/node-web-streams-helper'
@@ -159,12 +158,6 @@ export async function streamToBuffer(stream: AnyStream): Promise<Buffer> {
   return webStreamToBuffer(stream as ReadableStream<Uint8Array>)
 }

-export async function streamToUint8Array(
-  stream: AnyStream
-): Promise<Uint8Array> {
-  return webStreamToUint8Array(stream as ReadableStream<Uint8Array>)
-}
-
 export function chainStreams(...streams: AnyStream[]): AnyStream {
   return webChainStreams(...(streams as ReadableStream<Uint8Array>[]))
 }
diff --git a/packages/next/src/server/dev/serialized-errors.ts b/packages/next/src/server/dev/serialized-errors.ts
index 64f8c32b66a69..b19ffd38818ed 100644
--- a/packages/next/src/server/dev/serialized-errors.ts
+++ b/packages/next/src/server/dev/serialized-errors.ts
@@ -3,7 +3,7 @@ import {
   type HmrMessageSentToBrowser,
 } from './hot-reloader-types'
 import type { AnyStream } from '../app-render/stream-ops'
-import { streamToUint8Array } from '../app-render/stream-ops'
+import { streamToUint8Array } from '../stream-utils/node-web-streams-helper'

 const errorsRscStreamsByHtmlRequestId = new Map<string, AnyStream>()

diff --git a/packages/next/src/server/stream-utils/node-web-streams-helper.ts b/packages/next/src/server/stream-utils/node-web-streams-helper.ts
index 7ba1061f17ee7..aed8b3980260b 100644
--- a/packages/next/src/server/stream-utils/node-web-streams-helper.ts
+++ b/packages/next/src/server/stream-utils/node-web-streams-helper.ts
@@ -22,6 +22,7 @@ import {
   NEXT_INSTANT_PREFETCH_HEADER,
 } from '../../client/components/app-router-headers'
 import { computeCacheBustingSearchParam } from '../../shared/lib/router/utils/cache-busting-search-param'
+import type { AnyStream } from '../app-render/stream-ops'

 function voidCatch() {
   // this catcher is designed to be used with pipeTo where we expect the underlying
@@ -125,12 +126,58 @@ function concatUint8Arrays(chunks: Array<Uint8Array>): Uint8Array {
   return result
 }

-export async function streamToUint8Array(
+export async function webstreamToUint8Array(
   stream: ReadableStream<Uint8Array>
 ): Promise<Uint8Array> {
   return concatUint8Arrays(await streamToChunks(stream))
 }

+function webToReadable(
+  stream: ReadableStream<Uint8Array> | import('node:stream').Readable
+): import('node:stream').Readable {
+  let Readable: typeof import('node:stream').Readable
+  if (process.env.TURBOPACK) {
+    Readable = (require('node:stream') as typeof import('node:stream')).Readable
+  } else if (process.env.__NEXT_BUNDLER === 'Webpack') {
+    Readable = (
+      __non_webpack_require__('node:stream') as typeof import('node:stream')
+    ).Readable
+  } else {
+    Readable = (require('node:stream') as typeof import('node:stream')).Readable
+  }
+  if (stream instanceof Readable) {
+    return stream
+  }
+  return Readable.fromWeb(stream as import('stream/web').ReadableStream)
+}
+
+export async function nodestreamToUint8Array(
+  stream: AnyStream
+): Promise<Uint8Array> {
+  const chunks: Buffer[] = []
+  for await (const chunk of webToReadable(stream)) {
+    chunks.push(typeof chunk === 'string' ? Buffer.from(chunk) : chunk)
+  }
+  return Buffer.concat(chunks)
+}
+
+export async function streamToUint8Array(stream: AnyStream) {
+  let Readable: typeof import('node:stream').Readable
+  if (process.env.TURBOPACK) {
+    Readable = (require('node:stream') as typeof import('node:stream')).Readable
+  } else if (process.env.__NEXT_BUNDLER === 'Webpack') {
+    Readable = (
+      __non_webpack_require__('node:stream') as typeof import('node:stream')
+    ).Readable
+  } else {
+    Readable = (require('node:stream') as typeof import('node:stream')).Readable
+  }
+  if (stream instanceof Readable) {
+    return nodestreamToUint8Array(stream)
+  }
+  return webstreamToUint8Array(stream)
+}
+
 export async function streamToBuffer(
   stream: ReadableStream<Uint8Array>
 ): Promise<Buffer> {

PATCH

echo "Patch applied successfully."
