#!/bin/bash
set -e
cd /workspace/prisma

patch -p1 <<'PATCH'
diff --git a/packages/adapter-ppg/src/conversion.ts b/packages/adapter-ppg/src/conversion.ts
index 19edcce0984d..819520538990 100644
--- a/packages/adapter-ppg/src/conversion.ts
+++ b/packages/adapter-ppg/src/conversion.ts
@@ -149,7 +149,7 @@ export const ScalarColumnType = {
  * See the semantics of each of this code in:
  *   https://github.com/postgres/postgres/blob/master/src/include/catalog/pg_type.dat
  */
-const ArrayColumnType = {
+export const ArrayColumnType = {
   BIT_ARRAY: 1561,
   BOOL_ARRAY: 1000,
   BYTEA_ARRAY: 1001,
@@ -306,12 +306,17 @@ export const builtinParsers = Object.entries({
   parse: v,
 }))

-function normalize_bool(x: string) {
+function normalize_bool(x: string | null) {
   return x === null ? null : x === 'f' ? 'false' : 'true'
 }

-function normalize_array(element_normalizer: (x: string) => string): (str: string) => string[] {
-  return (str) => parseArray(str, element_normalizer)
+function normalize_array(
+  element_normalizer: (x: string) => string | null,
+): (str: string | null) => (string | null)[] | null {
+  return (str) => {
+    if (str === null) return null
+    return parseArray(str, element_normalizer)
+  }
 }

 /****************************/
@@ -339,11 +344,13 @@ function normalize_date(date: string): string {
  * ex: 1996-12-19T16:39:57-08:00
  */

-function normalize_timestamp(time: string): string {
+function normalize_timestamp(time: string | null): string | null {
+  if (time === null) return null
   return `${time.replace(' ', 'T')}+00:00`
 }

-function normalize_timestamptz(time: string): string {
+function normalize_timestamptz(time: string | null): string | null {
+  if (time === null) return null
   return time.replace(' ', 'T').replace(/[+-]\d{2}(:\d{2})?$/, '+00:00')
 }

@@ -355,7 +362,8 @@ function normalize_time(time: string): string {
   return time
 }

-function normalize_timez(time: string): string {
+function normalize_timez(time: string | null): string | null {
+  if (time === null) return null
   // Although it might be controversial, UTC is assumed in consistency with the behavior of rust postgres driver
   // in quaint. See quaint/src/connector/postgres/conversion.rs
   return time.replace(/[+-]\d{2}(:\d{2})?$/, '')
@@ -365,7 +373,8 @@ function normalize_timez(time: string): string {
 /* Money handling */
 /******************/

-function normalize_money(money: string): string {
+function normalize_money(money: string | null): string | null {
+  if (money === null) return null
   return money.slice(1)
 }

@@ -405,11 +414,13 @@ const builtInByteParser = getTypeParser(ScalarColumnType.BYTEA) as (_: string) =
 /*
  * BYTEA_ARRAY - arrays of arbitrary raw binary strings
  */
-function normalizeByteaArray(x: string) {
-  return parseArray(x).map(builtInByteParser)
+function normalizeByteaArray(x: string | null): (Buffer | null)[] | null {
+  if (x === null) return null
+  return parseArray(x).map((elem) => (elem === null ? null : builtInByteParser(elem)))
 }

-function convertBytes(serializedBytes: string): Buffer {
+function convertBytes(serializedBytes: string | null): Buffer | null {
+  if (serializedBytes === null) return null
   return parsePgBytes(serializedBytes)
 }
PATCH

# Idempotency check - look for a distinctive line from the patch
grep -q "export const ArrayColumnType" packages/adapter-ppg/src/conversion.ts
