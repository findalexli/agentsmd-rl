#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

# Idempotent: skip if already applied
if grep -q '## Changesets' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/.changeset/polite-spiders-kneel.md b/.changeset/polite-spiders-kneel.md
new file mode 100644
index 00000000000..a4edfb61100
--- /dev/null
+++ b/.changeset/polite-spiders-kneel.md
@@ -0,0 +1,5 @@
+---
+"@effect/cluster": patch
+---
+
+backport effect v4 MessageStorage improvements
diff --git a/AGENTS.md b/AGENTS.md
index 3d016f4880b..72fea10f29f 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -36,6 +36,11 @@ to automatically format code according to the project's style guidelines.
 The `index.ts` files are automatically generated. Do not manually edit them. Use
 `pnpm codegen` to regenerate barrel files after adding or removing modules.

+## Changesets
+
+All pull requests must include a changeset in the `.changeset/` directory.
+This is important for maintaining a clear changelog and ensuring proper versioning of packages.
+
 ## Running test code

 If you need to run some code for testing or debugging purposes, create a new
diff --git a/packages/cluster/src/MessageStorage.ts b/packages/cluster/src/MessageStorage.ts
index 37b052becab..492c3ac1287 100644
--- a/packages/cluster/src/MessageStorage.ts
+++ b/packages/cluster/src/MessageStorage.ts
@@ -251,7 +251,7 @@ export type Encoded = {
    * - Un-acknowledged chunk replies
    * - WithExit replies
    */
-  readonly repliesFor: (requestIds: Array<string>) => Effect.Effect<
+  readonly repliesFor: (requestIds: Arr.NonEmptyArray<string>) => Effect.Effect<
     Array<Reply.ReplyEncoded<any>>,
     PersistenceError
   >
@@ -259,7 +259,7 @@ export type Encoded = {
   /**
    * Retrieves the replies for the specified request ids.
    */
-  readonly repliesForUnfiltered: (requestIds: Array<string>) => Effect.Effect<
+  readonly repliesForUnfiltered: (requestIds: Arr.NonEmptyArray<string>) => Effect.Effect<
     Array<Reply.ReplyEncoded<any>>,
     PersistenceError
   >
@@ -275,7 +275,7 @@ export type Encoded = {
    * - All Interrupt's for unprocessed requests
    */
   readonly unprocessedMessages: (
-    shardIds: ReadonlyArray<string>,
+    shardIds: Arr.NonEmptyArray<string>,
     now: number
   ) => Effect.Effect<
     Array<{
@@ -289,7 +289,7 @@ export type Encoded = {
    * Retrieves the unprocessed messages by id.
    */
   readonly unprocessedMessagesById: (
-    messageIds: ReadonlyArray<Snowflake.Snowflake>,
+    messageIds: Arr.NonEmptyArray<Snowflake.Snowflake>,
     now: number
   ) => Effect.Effect<
     Array<{
@@ -317,7 +317,7 @@ export type Encoded = {
    * Reset the mailbox state for the provided shards.
    */
   readonly resetShards: (
-    shardIds: ReadonlyArray<string>
+    shardIds: Arr.NonEmptyArray<string>
   ) => Effect.Effect<void, PersistenceError>
 }

@@ -504,28 +504,31 @@ export const makeEncoded: (encoded: Encoded) => Effect.Effect<
         requestIds.push(id)
         map.set(id, message)
       }
-      if (requestIds.length === 0) return []
+      if (!Arr.isNonEmptyArray(requestIds)) return []
       const encodedReplies = yield* encoded.repliesFor(requestIds)
       return yield* decodeReplies(map, encodedReplies)
     }),
-    repliesForUnfiltered: (ids) => encoded.repliesForUnfiltered(Array.from(ids, String)),
+    repliesForUnfiltered: (ids) => {
+      const requestIds = Array.from(ids, String)
+      return Arr.isNonEmptyArray(requestIds)
+        ? encoded.repliesForUnfiltered(requestIds)
+        : Effect.succeed([])
+    },
     requestIdForPrimaryKey(options) {
       const primaryKey = Envelope.primaryKeyByAddress(options)
       return encoded.requestIdForPrimaryKey(primaryKey)
     },
     unprocessedMessages: (shardIds) => {
-      const shards = Array.from(shardIds)
-      if (shards.length === 0) return Effect.succeed([])
+      const shards = Array.from(shardIds, (id) => id.toString())
+      if (!Arr.isNonEmptyArray(shards)) return Effect.succeed([])
       return Effect.flatMap(
-        Effect.suspend(() =>
-          encoded.unprocessedMessages(shards.map((id) => id.toString()), clock.unsafeCurrentTimeMillis())
-        ),
+        Effect.suspend(() => encoded.unprocessedMessages(shards, clock.unsafeCurrentTimeMillis())),
         decodeMessages
       )
     },
     unprocessedMessagesById(messageIds) {
       const ids = Array.from(messageIds)
-      if (ids.length === 0) return Effect.succeed([])
+      if (!Arr.isNonEmptyArray(ids)) return Effect.succeed([])
       return Effect.flatMap(
         Effect.suspend(() => encoded.unprocessedMessagesById(ids, clock.unsafeCurrentTimeMillis())),
         decodeMessages
@@ -533,7 +536,12 @@ export const makeEncoded: (encoded: Encoded) => Effect.Effect<
     },
     resetAddress: encoded.resetAddress,
     clearAddress: encoded.clearAddress,
-    resetShards: (shardIds) => encoded.resetShards(Array.from(shardIds, (id) => id.toString()))
+    resetShards: (shardIds) => {
+      const shards = Array.from(shardIds, (id) => id.toString())
+      return Arr.isNonEmptyArray(shards)
+        ? encoded.resetShards(shards)
+        : Effect.void
+    }
   })

   const decodeMessages = (
diff --git a/packages/cluster/src/SqlMessageStorage.ts b/packages/cluster/src/SqlMessageStorage.ts
index 28465e08814..4326c3832b4 100644
--- a/packages/cluster/src/SqlMessageStorage.ts
+++ b/packages/cluster/src/SqlMessageStorage.ts
@@ -308,7 +308,7 @@ export const make = Effect.fnUntraced(function*(options?: {
   })

   const getUnprocessedMessages = sql.onDialectOrElse({
-    pg: () => (shardIds: ReadonlyArray<string>, now: number) =>
+    pg: () => (shardIds: Arr.NonEmptyArray<string>, now: number) =>
       sql<MessageJoinRow>`
         WITH messages AS (
           UPDATE ${messagesTableSql} m
@@ -333,7 +333,7 @@ export const make = Effect.fnUntraced(function*(options?: {
         )
         SELECT * FROM messages ORDER BY rowid ASC
       `,
-    orElse: () => (shardIds: ReadonlyArray<string>, now: number) =>
+    orElse: () => (shardIds: Arr.NonEmptyArray<string>, now: number) =>
       sql<MessageJoinRow>`
         SELECT m.*, r.id as reply_reply_id, r.kind as reply_kind, r.payload as reply_payload, r.sequence as reply_sequence
         FROM ${messagesTableSql} m
@@ -514,7 +514,7 @@ export const make = Effect.fnUntraced(function*(options?: {
     ),

     unprocessedMessagesById(ids, now) {
-      const idArr = Array.from(ids, (id) => String(id))
+      const idArr = ids.map((id) => String(id))
       return sql<MessageRow & ReplyJoinRow>`
         SELECT m.*, r.id as reply_id, r.kind as reply_kind, r.payload as reply_payload, r.sequence as reply_sequence
         FROM ${messagesTableSql} m
diff --git a/packages/cluster/test/MessageStorage.test.ts b/packages/cluster/test/MessageStorage.test.ts
index f58130f7a31..20703937f39 100644
--- a/packages/cluster/test/MessageStorage.test.ts
+++ b/packages/cluster/test/MessageStorage.test.ts
@@ -108,6 +108,34 @@ describe("MessageStorage", () => {
         yield* fiber.await
       }).pipe(Effect.provide(MemoryLive)))
   })
+
+  describe("makeEncoded", () => {
+    it.effect("guards empty id lists before delegating", () =>
+      Effect.gen(function*() {
+        const encoded = {
+          saveEnvelope: () => Effect.succeed(MessageStorage.SaveResultEncoded.Success()),
+          saveReply: () => Effect.void,
+          clearReplies: () => Effect.void,
+          requestIdForPrimaryKey: () => Effect.succeed(Option.none()),
+          repliesFor: () => Effect.succeed([]),
+          repliesForUnfiltered: () => Effect.die("unexpected repliesForUnfiltered call"),
+          unprocessedMessages: () => Effect.succeed([]),
+          unprocessedMessagesById: () => Effect.succeed([]),
+          resetAddress: () => Effect.void,
+          clearAddress: () => Effect.void,
+          resetShards: () => Effect.die("unexpected resetShards call")
+        }
+
+        const storage = yield* MessageStorage.makeEncoded(encoded).pipe(
+          Effect.provide(Snowflake.layerGenerator)
+        )
+
+        const replies = yield* storage.repliesForUnfiltered([])
+        expect(replies).toEqual([])
+
+        yield* storage.resetShards([])
+      }))
+  })
 })

 export const GetUserRpc = Rpc.make("GetUser", {

PATCH

echo "Patch applied successfully."
