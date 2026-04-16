#!/bin/bash
set -e
cd /workspace/payload_repo

# Apply the core fix to update.ts
cat << 'PATCH' | git apply -
diff --git a/packages/payload/src/collections/operations/update.ts b/packages/payload/src/collections/operations/update.ts
index 973df84806e..252b240d715 100644
--- a/packages/payload/src/collections/operations/update.ts
+++ b/packages/payload/src/collections/operations/update.ts
@@ -179,7 +179,7 @@ export const updateOperation = async <

     let docs

-    if (hasDraftsEnabled(collectionConfig) && shouldSaveDraft) {
+    if (hasDraftsEnabled(collectionConfig) && (shouldSaveDraft || isTrashAttempt)) {
       const versionsWhere = appendVersionToQueryKey(fullWhere)

       await validateQueryPaths({
PATCH

# Add localized field to Posts collection for testing
cat << 'PATCH' | git apply -
diff --git a/test/trash/collections/Posts/index.ts b/test/trash/collections/Posts/index.ts
index d37cdb6be56..72b21f7398d 100644
--- a/test/trash/collections/Posts/index.ts
+++ b/test/trash/collections/Posts/index.ts
@@ -14,6 +14,11 @@ export const Posts: CollectionConfig = {
       type: 'text',
       required: true,
     },
+    {
+      name: 'localizedField',
+      type: 'text',
+      localized: true,
+    },
   ],
   versions: {
     drafts: true,
PATCH

# Add localization config
cat << 'PATCH' | git apply -
diff --git a/test/trash/config.ts b/test/trash/config.ts
index fa29370f189..a63b2394716 100644
--- a/test/trash/config.ts
+++ b/test/trash/config.ts
@@ -20,6 +20,10 @@ export default buildConfigWithDefaults({
       baseDir: path.resolve(dirname),
     },
   },
+  localization: {
+    locales: ['en', 'es'],
+    defaultLocale: 'en',
+  },
   editor: lexicalEditor({}),

   onInit: async (payload) => {
PATCH

# Add integration test
cat << 'PATCH' | git apply -
diff --git a/test/trash/int.spec.ts b/test/trash/int.spec.ts
index c421d0a675e..3885632b8ca 100644
--- a/test/trash/int.spec.ts
+++ b/test/trash/int.spec.ts
@@ -1147,6 +1147,82 @@ describe('trash', () => {
         expect(result.totalDocs).toEqual(1) // Only postsDocTwo
       })
     })
+
+    it('should preserve localized field data when bulk trashing draft documents', async () => {
+      const localizedFieldValueEN = 'Localized Draft Content EN'
+      const localizedFieldValueES = 'Localized Draft Content ES'
+
+      const post = await payload.create({
+        collection: postsSlug,
+        data: {
+          title: 'Draft with Localized Field',
+          _status: 'draft',
+        },
+      })
+
+      // Update en locale as draft - isSavingDraft = true skips updateOne on the main table,
+      // storing localized data only in the versions table
+      await payload.update({
+        collection: postsSlug,
+        id: post.id,
+        locale: 'en',
+        data: {
+          localizedField: localizedFieldValueEN,
+          _status: 'draft',
+        },
+        draft: true,
+      })
+
+      await payload.update({
+        collection: postsSlug,
+        id: post.id,
+        locale: 'es',
+        data: {
+          localizedField: localizedFieldValueES,
+          _status: 'draft',
+        },
+        draft: true,
+      })
+
+      // Bulk trash the document (simulates list view "Move to Trash")
+      // This reads from the main table which has stale/empty localizedField
+      const trashResult = await payload.update({
+        collection: postsSlug,
+        data: {
+          deletedAt: new Date().toISOString(),
+        },
+        where: {
+          id: {
+            equals: post.id,
+          },
+        },
+      })
+
+      expect(trashResult.docs).toHaveLength(1)
+      expect(trashResult.docs[0]?.deletedAt).toBeTruthy()
+
+      // Fetch the latest draft version of the trashed document for each locale
+      const trashedDocEN = await payload.findByID({
+        collection: postsSlug,
+        id: post.id,
+        locale: 'en',
+        draft: true,
+        trash: true,
+      })
+
+      const trashedDocES = await payload.findByID({
+        collection: postsSlug,
+        id: post.id,
+        locale: 'es',
+        draft: true,
+        trash: true,
+      })
+
+      // localizedField should be preserved from the latest draft version for both locales,
+      // not lost due to stale main table data being used during bulk trash
+      expect(trashedDocEN.localizedField).toBe(localizedFieldValueEN)
+      expect(trashedDocES.localizedField).toBe(localizedFieldValueES)
+    })
   })

   describe('REST API', () => {
PATCH

# Update payload-types.ts
cat << 'PATCH' | git apply -
diff --git a/test/trash/payload-types.ts b/test/trash/payload-types.ts
index 48d331e2e09..957f863d93c 100644
--- a/test/trash/payload-types.ts
+++ b/test/trash/payload-types.ts
@@ -92,10 +92,13 @@ export interface Config {
   db: {
     defaultIDType: string;
   };
-  fallbackLocale: null;
+  fallbackLocale: ('false' | 'none' | 'null') | false | null | ('en' | 'es') | ('en' | 'es')[];
   globals: {};
   globalsSelect: {};
-  locale: null;
+  locale: 'en' | 'es';
+  widgets: {
+    collections: CollectionsWidget;
+  };
   user: User;
   jobs: {
     tasks: unknown;
@@ -138,6 +141,7 @@ export interface Page {
 export interface Post {
   id: string;
   title: string;
+  localizedField?: string | null;
   updatedAt: string;
   createdAt: string;
   deletedAt?: string | null;
@@ -297,6 +301,7 @@ export interface PagesSelect<T extends boolean = true> {
  */
 export interface PostsSelect<T extends boolean = true> {
   title?: T;
+  localizedField?: T;
   updatedAt?: T;
   createdAt?: T;
   deletedAt?: T;
@@ -389,6 +394,16 @@ export interface PayloadMigrationsSelect<T extends boolean = true> {
   updatedAt?: T;
   createdAt?: T;
 }
+/**
+ * This interface was referenced by `Config`'s JSON-Schema
+ * via the `definition` "collections_widget".
+ */
+export interface CollectionsWidget {
+  data?: {
+    [k: string]: unknown;
+  };
+  width: 'full';
+}
 /**
  * This interface was referenced by `Config`'s JSON-Schema
  * via the `definition` "auth".
PATCH

echo "Fix applied successfully"
