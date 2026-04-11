#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotent: skip if already applied
if grep -q 'flattenedFields: collection.flattenedFields' packages/db-mongodb/src/models/buildCollectionSchema.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 1204681c697..890995e7542 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -82,6 +82,47 @@ Payload is a monorepo structured around Next.js, containing the core CMS platfor

 ## Testing

+### Writing Tests - Required Practices
+
+**Tests MUST be self-contained and clean up after themselves:**
+
+- If you create a database record in a test, you MUST delete it before the test completes
+- For multiple tests with similar cleanup needs, use `afterEach` to centralize cleanup logic
+- Track created resources (IDs, files, etc.) in a shared array within the `describe` block
+
+**Example pattern:**
+
+```typescript
+describe('My Feature', () => {
+  const createdIDs: number[] = []
+
+  afterEach(async () => {
+    for (const id of createdIDs) {
+      await payload.delete({ collection: 'my-collection', id })
+    }
+    createdIDs.length = 0
+  })
+
+  it('should create a record', async () => {
+    const id = 123
+    createdIDs.push(id)
+
+    await payload.create({ collection: 'my-collection', data: { id, title: 'Test' } })
+    // assertions...
+  })
+})
+```
+
+**Additional test guidelines:**
+
+- Use descriptive test names starting with "should" (e.g., "should create document with custom ID")
+- Add blank lines after variable declarations to improve readability
+- Collection and global slugs should be kept in a shared file and re-used i.e. on relationship fields `relationTo: collectionSlug`
+- One test should verify one behavior - keep tests focused
+- When adding a new collection for testing, add it to both `collections/` directory and the config file import statements
+
+### How to run tests
+
 - `pnpm run test` - Run all tests (integration + components + e2e)
 - `pnpm run test:int` - Integration tests (MongoDB, recommended)
 - `pnpm run test:int <dir>` - Specific test suite (e.g. `fields`)
diff --git a/packages/db-mongodb/src/models/buildCollectionSchema.ts b/packages/db-mongodb/src/models/buildCollectionSchema.ts
index 01eb24acd1d..8c7a3d2da05 100644
--- a/packages/db-mongodb/src/models/buildCollectionSchema.ts
+++ b/packages/db-mongodb/src/models/buildCollectionSchema.ts
@@ -25,6 +25,7 @@ export const buildCollectionSchema = (
     },
     compoundIndexes: collection.sanitizedIndexes,
     configFields: collection.fields,
+    flattenedFields: collection.flattenedFields,
     payload,
   })

diff --git a/packages/db-mongodb/src/models/buildSchema.ts b/packages/db-mongodb/src/models/buildSchema.ts
index 4e1a7992718..70648be1fba 100644
--- a/packages/db-mongodb/src/models/buildSchema.ts
+++ b/packages/db-mongodb/src/models/buildSchema.ts
@@ -11,6 +11,7 @@ import {
   type EmailField,
   type Field,
   type FieldAffectingData,
+  type FlattenedField,
   type GroupField,
   type JSONField,
   type NonPresentationalField,
@@ -130,17 +131,26 @@ export const buildSchema = (args: {
   buildSchemaOptions: BuildSchemaOptions
   compoundIndexes?: SanitizedCompoundIndex[]
   configFields: Field[]
+  flattenedFields?: FlattenedField[]
   parentIsLocalized?: boolean
   payload: Payload
 }): Schema => {
-  const { buildSchemaOptions = {}, configFields, parentIsLocalized, payload } = args
+  const {
+    buildSchemaOptions = {},
+    configFields,
+    flattenedFields,
+    parentIsLocalized,
+    payload,
+  } = args
   const { allowIDField, options } = buildSchemaOptions
   let fields = {}

   let schemaFields = configFields

   if (!allowIDField) {
-    const idField = schemaFields.find((field) => fieldAffectsData(field) && field.name === 'id')
+    // Use flattenedFields if available to find custom id field regardless of nesting
+    const fieldsToSearch = flattenedFields || schemaFields
+    const idField = fieldsToSearch.find((field) => fieldAffectsData(field) && field.name === 'id')
     if (idField) {
       fields = {
         _id:
diff --git a/packages/payload/src/fields/hooks/afterRead/index.ts b/packages/payload/src/fields/hooks/afterRead/index.ts
index c0ba648d0d2..4fd020306a8 100644
--- a/packages/payload/src/fields/hooks/afterRead/index.ts
+++ b/packages/payload/src/fields/hooks/afterRead/index.ts
@@ -82,6 +82,7 @@ export async function afterRead<T extends JsonObject>(args: AfterReadArgs<T>): P
     doc: incomingDoc,
     draft,
     fallbackLocale,
+    fieldDepth: 0,
     fieldPromises,
     fields: (collection?.fields || global?.fields)!,
     findMany: findMany!,
diff --git a/packages/payload/src/fields/hooks/afterRead/promise.ts b/packages/payload/src/fields/hooks/afterRead/promise.ts
index 686f3ac4144..54d789b700e 100644
--- a/packages/payload/src/fields/hooks/afterRead/promise.ts
+++ b/packages/payload/src/fields/hooks/afterRead/promise.ts
@@ -35,6 +35,14 @@ type Args = {
   draft: boolean
   fallbackLocale: TypedFallbackLocale
   field: Field | TabAsField
+  /**
+   * The depth of the current field being processed.
+   * Fields without names (i.e. rows, collapsibles, unnamed groups)
+   * simply pass this value through
+   *
+   * @default 0
+   */
+  fieldDepth: number
   fieldIndex: number
   /**
    * fieldPromises are used for things like field hooks. They should be awaited before awaiting populationPromises
@@ -81,6 +89,7 @@ export const promise = async ({
   draft,
   fallbackLocale,
   field,
+  fieldDepth,
   fieldIndex,
   fieldPromises,
   findMany,
@@ -117,11 +126,14 @@ export const promise = async ({
   const indexPathSegments = indexPath ? indexPath.split('-').filter(Boolean)?.map(Number) : []
   let removedFieldValue = false

+  const isTopLevelIDField = fieldAffectsDataResult && field.name === 'id' && fieldDepth === 0
+
   if (
     fieldAffectsDataResult &&
     field.hidden &&
     typeof siblingDoc[field.name!] !== 'undefined' &&
-    !showHiddenFields
+    !showHiddenFields &&
+    !isTopLevelIDField
   ) {
     removedFieldValue = true
     delete siblingDoc[field.name!]
@@ -438,6 +450,7 @@ export const promise = async ({
             doc,
             draft,
             fallbackLocale,
+            fieldDepth: fieldDepth + 1,
             fieldPromises,
             fields: field.fields,
             findMany,
@@ -473,6 +486,7 @@ export const promise = async ({
                 doc,
                 draft,
                 fallbackLocale,
+                fieldDepth: fieldDepth + 1,
                 fieldPromises,
                 fields: field.fields,
                 findMany,
@@ -534,6 +548,7 @@ export const promise = async ({
               doc,
               draft,
               fallbackLocale,
+            fieldDepth: fieldDepth + 1,
               fieldPromises,
               fields: block.fields,
               findMany,
@@ -579,6 +594,7 @@ export const promise = async ({
                   doc,
                   draft,
                   fallbackLocale,
+                  fieldDepth: fieldDepth + 1,
                   fieldPromises,
                   fields: block.fields,
                   findMany,
@@ -622,6 +638,7 @@ export const promise = async ({
         doc,
         draft,
         fallbackLocale,
+        fieldDepth,
         fieldPromises,
         fields: field.fields,
         findMany,
@@ -665,6 +682,7 @@ export const promise = async ({
               doc,
               draft,
               fallbackLocale,
+              fieldDepth: fieldDepth + 1,
               fieldPromises,
               fields: field.fields,
               findMany,
@@ -697,6 +715,7 @@ export const promise = async ({
             doc,
             draft,
             fallbackLocale,
+            fieldDepth: fieldDepth + 1,
             fieldPromises,
             fields: field.fields,
             findMany,
@@ -729,6 +748,7 @@ export const promise = async ({
           doc,
           draft,
           fallbackLocale,
+          fieldDepth,
           fieldPromises,
           fields: field.fields,
           findMany,
@@ -871,6 +891,7 @@ export const promise = async ({
               doc,
               draft,
               fallbackLocale,
+              fieldDepth: fieldDepth + 1,
               fieldPromises,
               fields: field.fields,
               findMany,
@@ -903,6 +924,7 @@ export const promise = async ({
             doc,
             draft,
             fallbackLocale,
+            fieldDepth: fieldDepth + 1,
             fieldPromises,
             fields: field.fields,
             findMany,
@@ -935,6 +957,7 @@ export const promise = async ({
           doc,
           draft,
           fallbackLocale,
+          fieldDepth,
           fieldPromises,
           fields: field.fields,
           findMany,
@@ -971,6 +994,7 @@ export const promise = async ({
         doc,
         draft,
         fallbackLocale,
+        fieldDepth,
         fieldPromises,
         fields: field.tabs.map((tab) => ({ ...tab, type: 'tab' })),
         findMany,
diff --git a/packages/payload/src/fields/hooks/afterRead/traverseFields.ts b/packages/payload/src/fields/hooks/afterRead/traverseFields.ts
index 8df4179ec77..e6888828309 100644
--- a/packages/payload/src/fields/hooks/afterRead/traverseFields.ts
+++ b/packages/payload/src/fields/hooks/afterRead/traverseFields.ts
@@ -24,6 +24,14 @@ type Args = {
   doc: JsonObject
   draft: boolean
   fallbackLocale: TypedFallbackLocale
+  /**
+   * The depth of the current field being processed.
+   * Fields without names (i.e. rows, collapsibles, unnamed groups)
+   * simply pass this value through
+   *
+   * @default 0
+   */
+  fieldDepth?: number
   /**
    * fieldPromises are used for things like field hooks. They should be awaited before awaiting populationPromises
    */
@@ -61,6 +69,7 @@ export const traverseFields = ({
   doc,
   draft,
   fallbackLocale,
+  fieldDepth = 0,
   fieldPromises,
   fields,
   findMany,
@@ -94,6 +103,7 @@ export const traverseFields = ({
         draft,
         fallbackLocale,
         field,
+        fieldDepth,
         fieldIndex,
         fieldPromises,
         findMany,
PATCH

echo "Patch applied successfully."
