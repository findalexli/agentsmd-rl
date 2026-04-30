#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

TARGET=packages/sql-sqlite-bun/src/SqliteClient.ts

# Idempotency: in the buggy file, `const statement = db.query(sql)` is at
# column 11 and immediately follows `useSafeIntegers = ...` (no surrounding
# `try {`). After the fix, the same line is at column 13 (one extra indent
# level) because it has been moved inside the try block. If we already see it
# at the deeper indent twice (once for `run`, once for `runValues`), the patch
# is already applied — no-op.
deeper=$(grep -c "^            const statement = db.query(sql)$" "$TARGET" || true)
if [ "$deeper" = "2" ]; then
  echo "solve.sh: patch already applied, no-op"
  exit 0
fi

# Inline the gold patch (no external fetches).
git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/fix-sqlite-bun-query-prepare.md b/.changeset/fix-sqlite-bun-query-prepare.md
new file mode 100644
index 00000000000..7931c573d6d
--- /dev/null
+++ b/.changeset/fix-sqlite-bun-query-prepare.md
@@ -0,0 +1,5 @@
+---
+"@effect/sql-sqlite-bun": patch
+---
+
+Wrap `db.query()` (prepare) errors in `SqlError` so they surface as catchable failures instead of defects.
diff --git a/packages/sql-sqlite-bun/src/SqliteClient.ts b/packages/sql-sqlite-bun/src/SqliteClient.ts
index f0ee147d134..71367ad5418 100644
--- a/packages/sql-sqlite-bun/src/SqliteClient.ts
+++ b/packages/sql-sqlite-bun/src/SqliteClient.ts
@@ -104,10 +104,10 @@ export const make = (
       ) =>
         Effect.withFiberRuntime<Array<any>, SqlError>((fiber) => {
           const useSafeIntegers = Context.get(fiber.currentContext, Client.SafeIntegers)
-          const statement = db.query(sql)
-          // @ts-ignore bun-types missing safeIntegers method, fixed in https://github.com/oven-sh/bun/pull/26627
-          statement.safeIntegers(useSafeIntegers)
           try {
+            const statement = db.query(sql)
+            // @ts-ignore bun-types missing safeIntegers method, fixed in https://github.com/oven-sh/bun/pull/26627
+            statement.safeIntegers(useSafeIntegers)
             return Effect.succeed((statement.all(...(params as any)) ?? []) as Array<any>)
           } catch (cause) {
             return Effect.fail(new SqlError({ cause, message: "Failed to execute statement" }))
@@ -120,10 +120,10 @@ export const make = (
       ) =>
         Effect.withFiberRuntime<Array<any>, SqlError>((fiber) => {
           const useSafeIntegers = Context.get(fiber.currentContext, Client.SafeIntegers)
-          const statement = db.query(sql)
-          // @ts-ignore bun-types missing safeIntegers method, fixed in https://github.com/oven-sh/bun/pull/26627
-          statement.safeIntegers(useSafeIntegers)
           try {
+            const statement = db.query(sql)
+            // @ts-ignore bun-types missing safeIntegers method, fixed in https://github.com/oven-sh/bun/pull/26627
+            statement.safeIntegers(useSafeIntegers)
             return Effect.succeed((statement.values(...(params as any)) ?? []) as Array<any>)
           } catch (cause) {
             return Effect.fail(new SqlError({ cause, message: "Failed to execute statement" }))
PATCH

echo "solve.sh: patch applied"
