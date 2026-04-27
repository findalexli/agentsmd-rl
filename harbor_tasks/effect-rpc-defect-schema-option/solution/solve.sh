#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

# Idempotency: skip if patch already applied
if grep -q 'defectSchema: this.defectSchema' packages/rpc/src/Rpc.ts 2>/dev/null; then
  echo "Gold patch already applied; skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/custom-defect-schema.md b/.changeset/custom-defect-schema.md
new file mode 100644
index 00000000000..3f447c147d1
--- /dev/null
+++ b/.changeset/custom-defect-schema.md
@@ -0,0 +1,5 @@
+---
+"@effect/rpc": patch
+---
+
+Add optional `defect` parameter to `Rpc.make` for customizing defect serialization per-RPC. Defaults to `Schema.Defect`, preserving existing behavior.
diff --git a/packages/platform-node/test/RpcServer.test.ts b/packages/platform-node/test/RpcServer.test.ts
index 657bc77f55d..374454c0d50 100644
--- a/packages/platform-node/test/RpcServer.test.ts
+++ b/packages/platform-node/test/RpcServer.test.ts
@@ -2,9 +2,9 @@ import { HttpClient, HttpClientRequest, HttpRouter, HttpServer, SocketServer } f
 import { NodeHttpServer, NodeSocket, NodeSocketServer, NodeWorker } from "@effect/platform-node"
 import { RpcClient, RpcSerialization, RpcServer } from "@effect/rpc"
 import { assert, describe, it } from "@effect/vitest"
-import { Effect, Layer } from "effect"
+import { Cause, Effect, Layer } from "effect"
 import * as CP from "node:child_process"
-import { RpcLive, User, UsersClient } from "./fixtures/rpc-schemas.js"
+import { RpcLive, RpcLiveDisableFatalDefects, User, UsersClient } from "./fixtures/rpc-schemas.js"
 import { e2eSuite } from "./rpc-e2e.js"

 describe("RpcServer", () => {
@@ -148,4 +148,38 @@ describe("RpcServer", () => {
         assert.deepStrictEqual(user, new User({ id: "1", name: "Logged in user" }))
       }).pipe(Effect.provide(UsersClient.layerTest)))
   })
+
+  describe("custom defect schema", () => {
+    const CustomDefectServer = HttpRouter.Default.serve().pipe(
+      Layer.provide(RpcLiveDisableFatalDefects),
+      Layer.provideMerge(RpcServer.layerProtocolHttp({ path: "/rpc" }))
+    )
+    const CustomDefectClient = UsersClient.layer.pipe(
+      Layer.provide(
+        RpcClient.layerProtocolHttp({
+          url: "",
+          transformClient: HttpClient.mapRequest(HttpClientRequest.appendUrl("/rpc"))
+        })
+      )
+    )
+    const CustomDefectLayer = CustomDefectClient.pipe(
+      Layer.provideMerge(CustomDefectServer),
+      Layer.provide([NodeHttpServer.layerTest, RpcSerialization.layerNdjson])
+    )
+
+    it.effect("preserves full defect with Schema.Unknown", () =>
+      Effect.gen(function*() {
+        const client = yield* UsersClient
+        const cause = yield* client.ProduceDefectCustom().pipe(
+          Effect.sandbox,
+          Effect.flip
+        )
+        const defect = Cause.squash(cause)
+        assert.deepStrictEqual(defect, {
+          message: "detailed error",
+          stack: "Error: detailed error\n  at handler.ts:1",
+          code: 42
+        })
+      }).pipe(Effect.provide(CustomDefectLayer)))
+  })
 })
diff --git a/packages/platform-node/test/fixtures/rpc-schemas.ts b/packages/platform-node/test/fixtures/rpc-schemas.ts
index de374c5e907..150cdad6b3a 100644
--- a/packages/platform-node/test/fixtures/rpc-schemas.ts
+++ b/packages/platform-node/test/fixtures/rpc-schemas.ts
@@ -59,6 +59,9 @@ export const UserRpcs = RpcGroup.make(
   }),
   Rpc.make("ProduceDefect"),
   Rpc.make("ProduceErrorDefect"),
+  Rpc.make("ProduceDefectCustom", {
+    defect: Schema.Unknown
+  }),
   Rpc.make("Never"),
   Rpc.make("nested.test"),
   Rpc.make("TimedMethod", {
@@ -134,6 +137,8 @@ const UsersLive = UserRpcs.toLayer(Effect.gen(function*() {
     GetEmits: () => Effect.sync(() => emits),
     ProduceDefect: () => Effect.die("boom"),
     ProduceErrorDefect: () => Effect.die(new Error("error defect message")),
+    ProduceDefectCustom: () =>
+      Effect.die({ message: "detailed error", stack: "Error: detailed error\n  at handler.ts:1", code: 42 }),
     Never: () => Effect.never.pipe(Effect.onInterrupt(() => Effect.sync(() => interrupts++))),
     "nested.test": () => Effect.void,
     TimedMethod: (_) => _.shouldFail ? Effect.die("boom") : Effect.succeed(1),
@@ -154,6 +159,14 @@ export const RpcLive = RpcServer.layer(UserRpcs).pipe(
   ])
 )

+export const RpcLiveDisableFatalDefects = RpcServer.layer(UserRpcs, { disableFatalDefects: true }).pipe(
+  Layer.provide([
+    UsersLive,
+    AuthLive,
+    TimingLive
+  ])
+)
+
 const AuthClient = RpcMiddleware.layerClient(AuthMiddleware, ({ request }) =>
   Effect.succeed({
     ...request,
diff --git a/packages/rpc/src/Rpc.ts b/packages/rpc/src/Rpc.ts
index 147c46be83e..57a04869fba 100644
--- a/packages/rpc/src/Rpc.ts
+++ b/packages/rpc/src/Rpc.ts
@@ -58,6 +58,7 @@ export interface Rpc<
   readonly payloadSchema: Payload
   readonly successSchema: Success
   readonly errorSchema: Error
+  readonly defectSchema: Schema.Schema<unknown, any>
   readonly annotations: Context_.Context<never>
   readonly middlewares: ReadonlySet<Middleware>

@@ -171,6 +172,7 @@ export interface AnyWithProps {
   readonly payloadSchema: AnySchema
   readonly successSchema: Schema.Schema.Any
   readonly errorSchema: Schema.Schema.All
+  readonly defectSchema: Schema.Schema<unknown, any>
   readonly annotations: Context_.Context<never>
   readonly middlewares: ReadonlySet<RpcMiddleware.TagClassAnyWithProps>
 }
@@ -541,6 +543,7 @@ const Proto = {
       payloadSchema: this.payloadSchema,
       successSchema,
       errorSchema: this.errorSchema,
+      defectSchema: this.defectSchema,
       annotations: this.annotations,
       middlewares: this.middlewares
     })
@@ -551,6 +554,7 @@ const Proto = {
       payloadSchema: this.payloadSchema,
       successSchema: this.successSchema,
       errorSchema,
+      defectSchema: this.defectSchema,
       annotations: this.annotations,
       middlewares: this.middlewares
     })
@@ -561,6 +565,7 @@ const Proto = {
       payloadSchema: Schema.isSchema(payloadSchema) ? payloadSchema as any : Schema.Struct(payloadSchema as any),
       successSchema: this.successSchema,
       errorSchema: this.errorSchema,
+      defectSchema: this.defectSchema,
       annotations: this.annotations,
       middlewares: this.middlewares
     })
@@ -571,6 +576,7 @@ const Proto = {
       payloadSchema: this.payloadSchema,
       successSchema: this.successSchema,
       errorSchema: this.errorSchema,
+      defectSchema: this.defectSchema,
       annotations: this.annotations,
       middlewares: new Set([...this.middlewares, middleware])
     })
@@ -581,6 +587,7 @@ const Proto = {
       payloadSchema: this.payloadSchema,
       successSchema: this.successSchema,
       errorSchema: this.errorSchema,
+      defectSchema: this.defectSchema,
       annotations: this.annotations,
       middlewares: this.middlewares
     })
@@ -591,6 +598,7 @@ const Proto = {
       payloadSchema: this.payloadSchema,
       successSchema: this.successSchema,
       errorSchema: this.errorSchema,
+      defectSchema: this.defectSchema,
       middlewares: this.middlewares,
       annotations: Context_.add(this.annotations, tag, value)
     })
@@ -601,6 +609,7 @@ const Proto = {
       payloadSchema: this.payloadSchema,
       successSchema: this.successSchema,
       errorSchema: this.errorSchema,
+      defectSchema: this.defectSchema,
       middlewares: this.middlewares,
       annotations: Context_.merge(this.annotations, context)
     })
@@ -618,6 +627,7 @@ const makeProto = <
   readonly payloadSchema: Payload
   readonly successSchema: Success
   readonly errorSchema: Error
+  readonly defectSchema: Schema.Schema<unknown, any>
   readonly annotations: Context_.Context<never>
   readonly middlewares: ReadonlySet<Middleware>
 }): Rpc<Tag, Payload, Success, Error, Middleware> => {
@@ -643,6 +653,7 @@ export const make = <
   readonly success?: Success
   readonly error?: Error
   readonly stream?: Stream
+  readonly defect?: Schema.Schema<unknown, any>
   readonly primaryKey?: [Payload] extends [Schema.Struct.Fields] ?
     ((payload: Schema.Simplify<Schema.Struct.Type<NoInfer<Payload>>>) => string) :
     never
@@ -678,6 +689,7 @@ export const make = <
       }) :
       successSchema,
     errorSchema: options?.stream ? Schema.Never : errorSchema,
+    defectSchema: options?.defect ?? Schema.Defect,
     annotations: Context_.empty(),
     middlewares: new Set<never>()
   }) as any
@@ -719,6 +731,7 @@ export const fromTaggedRequest = <S extends AnyTaggedRequestSchema>(
     payloadSchema: schema as any,
     successSchema: schema.success as any,
     errorSchema: schema.failure,
+    defectSchema: Schema.Defect,
     annotations: Context_.empty(),
     middlewares: new Set()
   })
@@ -747,7 +760,7 @@ export const exitSchema = <R extends Any>(
   const schema = Schema.Exit({
     success: Option.isSome(streamSchemas) ? Schema.Void : rpc.successSchema,
     failure: Schema.Union(...failures),
-    defect: Schema.Defect
+    defect: rpc.defectSchema
   })
   exitSchemaCache.set(self, schema)
   return schema as any
diff --git a/packages/rpc/src/RpcServer.ts b/packages/rpc/src/RpcServer.ts
index ddb7493c515..f69bfb62121 100644
--- a/packages/rpc/src/RpcServer.ts
+++ b/packages/rpc/src/RpcServer.ts
@@ -510,6 +510,7 @@ export const make: <Rpcs extends Rpc.Any>(
           return handleEncode(
             client,
             response.requestId,
+            schemas.encodeDefect,
             schemas.collector,
             Effect.provide(schemas.encodeChunk(response.values), schemas.context),
             (values) => ({ _tag: "Chunk", requestId: String(response.requestId), values })
@@ -522,6 +523,7 @@ export const make: <Rpcs extends Rpc.Any>(
           return handleEncode(
             client,
             response.requestId,
+            schemas.encodeDefect,
             schemas.collector,
             Effect.provide(schemas.encodeExit(response.exit), schemas.context),
             (exit) => ({ _tag: "Exit", requestId: String(response.requestId), exit })
@@ -552,6 +554,7 @@ export const make: <Rpcs extends Rpc.Any>(
     readonly decode: (u: unknown) => Effect.Effect<Rpc.Payload<Rpcs>, ParseError>
     readonly encodeChunk: (u: ReadonlyArray<unknown>) => Effect.Effect<NonEmptyReadonlyArray<unknown>, ParseError>
     readonly encodeExit: (u: unknown) => Effect.Effect<Schema.ExitEncoded<unknown, unknown, unknown>, ParseError>
+    readonly encodeDefect: (u: unknown) => Effect.Effect<unknown, ParseError>
     readonly context: Context.Context<never>
     readonly collector?: Transferable.CollectorService | undefined
   }
@@ -568,6 +571,7 @@ export const make: <Rpcs extends Rpc.Any>(
           Schema.Array(Option.isSome(streamSchemas) ? streamSchemas.value.success : Schema.Any)
         ) as any,
         encodeExit: Schema.encodeUnknown(Rpc.exitSchema(rpc as any)) as any,
+        encodeDefect: Schema.encodeUnknown(rpc.defectSchema) as any,
         context: entry.context
       }
       schemasCache.set(rpc, schemas)
@@ -584,6 +588,7 @@ export const make: <Rpcs extends Rpc.Any>(
   const handleEncode = <A, R>(
     client: Client,
     requestId: RequestId,
+    encodeDefect: (u: unknown) => Effect.Effect<unknown, ParseError>,
     collector: Transferable.CollectorService | undefined,
     effect: Effect.Effect<A, ParseError, R>,
     onSuccess: (a: A) => FromServerEncoded
@@ -594,7 +599,7 @@ export const make: <Rpcs extends Rpc.Any>(
         client.schemas.delete(requestId)
         const defect = Cause.squash(Cause.map(cause, TreeFormatter.formatErrorSync))
         return Effect.zipRight(
-          sendRequestDefect(client, requestId, defect),
+          sendRequestDefect(client, requestId, encodeDefect, defect),
           server.write(client.id, { _tag: "Interrupt", requestId, interruptors: [] })
         )
       })
@@ -602,19 +607,26 @@ export const make: <Rpcs extends Rpc.Any>(

   const encodeDefect = Schema.encodeSync(Schema.Defect)

-  const sendRequestDefect = (client: Client, requestId: RequestId, defect: unknown) =>
+  const sendRequestDefect = (
+    client: Client,
+    requestId: RequestId,
+    encodeDefect: (u: unknown) => Effect.Effect<unknown, ParseError>,
+    defect: unknown
+  ) =>
     Effect.catchAllCause(
-      send(client.id, {
-        _tag: "Exit",
-        requestId: String(requestId),
-        exit: {
-          _tag: "Failure",
-          cause: {
-            _tag: "Die",
-            defect: encodeDefect(defect)
+      encodeDefect(defect).pipe(Effect.flatMap((encodedDefect) =>
+        send(client.id, {
+          _tag: "Exit",
+          requestId: String(requestId),
+          exit: {
+            _tag: "Failure",
+            cause: {
+              _tag: "Die",
+              defect: encodedDefect
+            }
           }
-        }
-      }),
+        })
+      )),
       (cause) => sendDefect(client, Cause.squash(cause))
     )

@@ -661,7 +673,8 @@ export const make: <Rpcs extends Rpc.Any>(
         return Effect.matchEffect(
           Effect.provide(schemas.decode(request.payload), schemas.context),
           {
-            onFailure: (error) => sendRequestDefect(client, requestId, TreeFormatter.formatErrorSync(error)),
+            onFailure: (error) =>
+              sendRequestDefect(client, requestId, schemas.encodeDefect, TreeFormatter.formatErrorSync(error)),
             onSuccess: (payload) => {
               client.schemas.set(
                 requestId,
diff --git a/packages/rpc/test/Rpc.test.ts b/packages/rpc/test/Rpc.test.ts
index ab747dc678f..2d3cb3067fd 100644
--- a/packages/rpc/test/Rpc.test.ts
+++ b/packages/rpc/test/Rpc.test.ts
@@ -1,7 +1,7 @@
 import { Headers } from "@effect/platform"
 import { Rpc, RpcGroup } from "@effect/rpc"
 import { assert, describe, it } from "@effect/vitest"
-import { Effect, Schema } from "effect"
+import { Cause, Effect, Exit, Schema } from "effect"

 const TestGroup = RpcGroup.make(
   Rpc.make("one"),
@@ -20,4 +20,25 @@ describe("Rpc", () => {
       const result = yield* handler(void 0, Headers.empty)
       assert.strictEqual(result, "two")
     }))
+
+  it("exitSchema uses custom defect schema", () => {
+    const myRpc = Rpc.make("customDefect", {
+      success: Schema.String,
+      defect: Schema.Unknown
+    })
+
+    const schema = Rpc.exitSchema(myRpc)
+    const encode = Schema.encodeSync(schema)
+    const decode = Schema.decodeSync(schema)
+
+    const error = { message: "boom", stack: "Error: boom\n  at foo.ts:1", code: 42 }
+    const exit = Exit.die(error)
+
+    // Schema.Unknown preserves the full defect value, unlike the default Schema.Defect
+    const roundTripped = decode(encode(exit))
+
+    assert.isTrue(Exit.isFailure(roundTripped))
+    const defect = Cause.squash((roundTripped as Exit.Failure<any, any>).cause)
+    assert.deepStrictEqual(defect, error)
+  })
 })
PATCH

echo "Gold patch applied."
