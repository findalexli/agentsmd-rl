#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prisma

# Idempotent: skip if already applied
if grep -q 'resourceFromAttributes' packages/instrumentation/README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/client/package.json b/packages/client/package.json
index 8ddb6253edd7..b8c6575e1e58 100644
--- a/packages/client/package.json
+++ b/packages/client/package.json
@@ -225,11 +225,11 @@
     "@libsql/client": "0.8.1",
     "@neondatabase/serverless": "0.10.2",
     "@opentelemetry/api": "1.9.0",
-    "@opentelemetry/context-async-hooks": "2.0.0",
-    "@opentelemetry/instrumentation": "0.57.2",
-    "@opentelemetry/resources": "1.30.1",
-    "@opentelemetry/sdk-trace-base": "1.30.1",
-    "@opentelemetry/semantic-conventions": "1.30.0",
+    "@opentelemetry/context-async-hooks": "2.1.0",
+    "@opentelemetry/instrumentation": "0.206.0",
+    "@opentelemetry/resources": "2.1.0",
+    "@opentelemetry/sdk-trace-base": "2.1.0",
+    "@opentelemetry/semantic-conventions": "1.37.0",
     "@planetscale/database": "1.19.0",
     "@prisma/adapter-better-sqlite3": "workspace:*",
     "@prisma/adapter-d1": "workspace:*",
diff --git a/packages/client/tests/functional/tracing-disabled/tests.ts b/packages/client/tests/functional/tracing-disabled/tests.ts
index 281981dd0bb0..eb8e346cd376 100644
--- a/packages/client/tests/functional/tracing-disabled/tests.ts
+++ b/packages/client/tests/functional/tracing-disabled/tests.ts
@@ -1,8 +1,8 @@
-import { context } from '@opentelemetry/api'
+import { context, trace } from '@opentelemetry/api'
 import { AsyncLocalStorageContextManager } from '@opentelemetry/context-async-hooks'
-import { Resource } from '@opentelemetry/resources'
+import { resourceFromAttributes } from '@opentelemetry/resources'
 import { BasicTracerProvider, InMemorySpanExporter, SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base'
-import { SEMRESATTRS_SERVICE_NAME, SEMRESATTRS_SERVICE_VERSION } from '@opentelemetry/semantic-conventions'
+import { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } from '@opentelemetry/semantic-conventions'

 import testMatrix from './_matrix'
 // @ts-ignore
@@ -19,14 +19,14 @@ beforeAll(() => {
   inMemorySpanExporter = new InMemorySpanExporter()

   const basicTracerProvider = new BasicTracerProvider({
-    resource: new Resource({
-      [SEMRESATTRS_SERVICE_NAME]: 'test-name',
-      [SEMRESATTRS_SERVICE_VERSION]: '1.0.0',
+    resource: resourceFromAttributes({
+      [ATTR_SERVICE_NAME]: 'test-name',
+      [ATTR_SERVICE_VERSION]: '1.0.0',
     }),
+    spanProcessors: [new SimpleSpanProcessor(inMemorySpanExporter)],
   })

-  basicTracerProvider.addSpanProcessor(new SimpleSpanProcessor(inMemorySpanExporter))
-  basicTracerProvider.register()
+  trace.setGlobalTracerProvider(basicTracerProvider)

   /* new PrismaInstrumentation is not enabled so spans should not be generated */
   // registerInstrumentations({
diff --git a/packages/client/tests/functional/tracing-filtered-spans/tests.ts b/packages/client/tests/functional/tracing-filtered-spans/tests.ts
index 9107b6903644..4ab2252ad878 100644
--- a/packages/client/tests/functional/tracing-filtered-spans/tests.ts
+++ b/packages/client/tests/functional/tracing-filtered-spans/tests.ts
@@ -1,7 +1,7 @@
-import { context } from '@opentelemetry/api'
+import { context, trace } from '@opentelemetry/api'
 import { AsyncLocalStorageContextManager } from '@opentelemetry/context-async-hooks'
 import { registerInstrumentations } from '@opentelemetry/instrumentation'
-import { Resource } from '@opentelemetry/resources'
+import { resourceFromAttributes } from '@opentelemetry/resources'
 import { BasicTracerProvider, InMemorySpanExporter, SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base'
 import { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } from '@opentelemetry/semantic-conventions'
 import { PrismaInstrumentation } from '@prisma/instrumentation'
@@ -23,14 +23,14 @@ beforeAll(() => {
   inMemorySpanExporter = new InMemorySpanExporter()

   const basicTracerProvider = new BasicTracerProvider({
-    resource: new Resource({
+    resource: resourceFromAttributes({
       [ATTR_SERVICE_NAME]: 'test-name',
       [ATTR_SERVICE_VERSION]: '1.0.0',
     }),
+    spanProcessors: [new SimpleSpanProcessor(inMemorySpanExporter)],
   })

-  basicTracerProvider.addSpanProcessor(new SimpleSpanProcessor(inMemorySpanExporter))
-  basicTracerProvider.register()
+  trace.setGlobalTracerProvider(basicTracerProvider)

   registerInstrumentations({
     instrumentations: [
diff --git a/packages/client/tests/functional/tracing-no-sampling/tests.ts b/packages/client/tests/functional/tracing-no-sampling/tests.ts
index fdd92bab2421..e83381980cae 100644
--- a/packages/client/tests/functional/tracing-no-sampling/tests.ts
+++ b/packages/client/tests/functional/tracing-no-sampling/tests.ts
@@ -1,14 +1,14 @@
-import { context } from '@opentelemetry/api'
+import { context, trace } from '@opentelemetry/api'
 import { AsyncLocalStorageContextManager } from '@opentelemetry/context-async-hooks'
 import { registerInstrumentations } from '@opentelemetry/instrumentation'
-import { Resource } from '@opentelemetry/resources'
+import { resourceFromAttributes } from '@opentelemetry/resources'
 import {
   BasicTracerProvider,
   InMemorySpanExporter,
   SimpleSpanProcessor,
   TraceIdRatioBasedSampler,
 } from '@opentelemetry/sdk-trace-base'
-import { SEMRESATTRS_SERVICE_NAME, SEMRESATTRS_SERVICE_VERSION } from '@opentelemetry/semantic-conventions'
+import { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } from '@opentelemetry/semantic-conventions'
 import { PrismaInstrumentation } from '@prisma/instrumentation'

 import { NewPrismaClient } from '../_utils/types'
@@ -29,14 +29,14 @@ beforeAll(() => {

   const basicTracerProvider = new BasicTracerProvider({
     sampler: new TraceIdRatioBasedSampler(0), // 0% sampling!!
-    resource: new Resource({
-      [SEMRESATTRS_SERVICE_NAME]: 'test-name',
-      [SEMRESATTRS_SERVICE_VERSION]: '1.0.0',
+    resource: resourceFromAttributes({
+      [ATTR_SERVICE_NAME]: 'test-name',
+      [ATTR_SERVICE_VERSION]: '1.0.0',
     }),
+    spanProcessors: [new SimpleSpanProcessor(inMemorySpanExporter)],
   })

-  basicTracerProvider.addSpanProcessor(new SimpleSpanProcessor(inMemorySpanExporter))
-  basicTracerProvider.register()
+  trace.setGlobalTracerProvider(basicTracerProvider)

   registerInstrumentations({
     instrumentations: [new PrismaInstrumentation()],
diff --git a/packages/client/tests/functional/tracing/tests.ts b/packages/client/tests/functional/tracing/tests.ts
index feef60593b8a..fa6ccbd017db 100644
--- a/packages/client/tests/functional/tracing/tests.ts
+++ b/packages/client/tests/functional/tracing/tests.ts
@@ -2,7 +2,7 @@ import { faker } from '@faker-js/faker'
 import { Attributes, context, SpanKind, trace } from '@opentelemetry/api'
 import { AsyncLocalStorageContextManager } from '@opentelemetry/context-async-hooks'
 import { registerInstrumentations } from '@opentelemetry/instrumentation'
-import { Resource } from '@opentelemetry/resources'
+import { resourceFromAttributes } from '@opentelemetry/resources'
 import {
   BasicTracerProvider,
   InMemorySpanExporter,
@@ -52,7 +52,7 @@ function buildTree(rootSpan: ReadableSpan, spans: ReadableSpan[]): Tree {
       // provide stable ordering guarantee.
       return normalizeNameForComparison(a.name).localeCompare(normalizeNameForComparison(b.name))
     })
-    .filter((span) => span.parentSpanId === rootSpan.spanContext().spanId)
+    .filter((span) => span.parentSpanContext?.spanId === rootSpan.spanContext().spanId)

   const tree: Tree = {
     name: rootSpan.name,
@@ -84,17 +84,17 @@ beforeAll(() => {
   context.setGlobalContextManager(contextManager)

   inMemorySpanExporter = new InMemorySpanExporter()
+  processor = new SimpleSpanProcessor(inMemorySpanExporter)

   const basicTracerProvider = new BasicTracerProvider({
-    resource: new Resource({
+    resource: resourceFromAttributes({
       [ATTR_SERVICE_NAME]: 'test-name',
       [ATTR_SERVICE_VERSION]: '1.0.0',
     }),
+    spanProcessors: [processor],
   })

-  processor = new SimpleSpanProcessor(inMemorySpanExporter)
-  basicTracerProvider.addSpanProcessor(processor)
-  basicTracerProvider.register()
+  trace.setGlobalTracerProvider(basicTracerProvider)

   registerInstrumentations({
     instrumentations: [new PrismaInstrumentation()],
@@ -129,7 +129,7 @@ testMatrix.setupTestSuite(
       await waitFor(async () => {
         await processor.forceFlush()
         const spans = inMemorySpanExporter.getFinishedSpans()
-        const rootSpans = spans.filter((span) => !span.parentSpanId)
+        const rootSpans = spans.filter((span) => !span.parentSpanContext?.spanId)
         const trees = rootSpans.map((rootSpan) => buildTree(rootSpan, spans))

         if (Array.isArray(expectedTree)) {
diff --git a/packages/instrumentation/README.md b/packages/instrumentation/README.md
index ea921234d1e4..e7f413c481fa 100644
--- a/packages/instrumentation/README.md
+++ b/packages/instrumentation/README.md
@@ -37,13 +37,13 @@ generator client {
 Exporting traces to [Jaeger Tracing](https://jaegertracing.io).

 ```ts
-import { context } from '@opentelemetry/api'
+import { context, trace } from '@opentelemetry/api'
 import { AsyncLocalStorageContextManager } from '@opentelemetry/context-async-hooks'
 import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http'
 import { registerInstrumentations } from '@opentelemetry/instrumentation'
-import { Resource } from '@opentelemetry/resources'
+import { resourceFromAttributes } from '@opentelemetry/resources'
 import { BasicTracerProvider, SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base'
-import { SEMRESATTRS_SERVICE_NAME, SEMRESATTRS_SERVICE_VERSION } from '@opentelemetry/semantic-conventions'
+import { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } from '@opentelemetry/semantic-conventions'
 import { PrismaInstrumentation } from '@prisma/instrumentation'

 import { PrismaClient } from '.prisma/client'
@@ -55,14 +55,14 @@ context.setGlobalContextManager(contextManager)
 const otlpTraceExporter = new OTLPTraceExporter()

 const provider = new BasicTracerProvider({
-  resource: new Resource({
-    [SEMRESATTRS_SERVICE_NAME]: 'test-tracing-service',
-    [SEMRESATTRS_SERVICE_VERSION]: '1.0.0',
+  resource: resourceFromAttributes({
+    [ATTR_SERVICE_NAME]: 'test-tracing-service',
+    [ATTR_SERVICE_VERSION]: '1.0.0',
   }),
+  spanProcessors: [new SimpleSpanProcessor(otlpTraceExporter)],
 })

-provider.addSpanProcessor(new SimpleSpanProcessor(otlpTraceExporter))
-provider.register()
+trace.setGlobalTracerProvider(provider)

 registerInstrumentations({
   instrumentations: [new PrismaInstrumentation()],
diff --git a/packages/query-plan-executor/package.json b/packages/query-plan-executor/package.json
index d575390460c5..70f1b59ee261 100644
--- a/packages/query-plan-executor/package.json
+++ b/packages/query-plan-executor/package.json
@@ -14,8 +14,8 @@
     "@hono/node-server": "1.19.0",
     "@hono/zod-validator": "0.7.2",
     "@opentelemetry/api": "1.9.0",
-    "@opentelemetry/context-async-hooks": "2.0.1",
-    "@opentelemetry/sdk-trace-base": "2.0.1",
+    "@opentelemetry/context-async-hooks": "2.1.0",
+    "@opentelemetry/sdk-trace-base": "2.1.0",
     "@prisma/adapter-pg": "workspace:*",
     "@prisma/adapter-mariadb": "workspace:*",
     "@prisma/adapter-mssql": "workspace:*",

PATCH

echo "Patch applied successfully."
