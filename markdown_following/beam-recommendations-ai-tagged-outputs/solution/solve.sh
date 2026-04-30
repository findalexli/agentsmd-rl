#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if grep -q 'pardo.with_outputs' sdks/python/apache_beam/ml/gcp/recommendations_ai.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/sdks/python/apache_beam/ml/gcp/recommendations_ai.py b/sdks/python/apache_beam/ml/gcp/recommendations_ai.py
index 077fc83bbd07..9730a6b2b1d9 100644
--- a/sdks/python/apache_beam/ml/gcp/recommendations_ai.py
+++ b/sdks/python/apache_beam/ml/gcp/recommendations_ai.py
@@ -79,15 +79,19 @@ def get_recommendation_user_event_client():


 class CreateCatalogItem(PTransform):
-  """Creates catalogitem information.
-    The ``PTransform`` returns a PCollectionTuple with a PCollections of
-    successfully and failed created CatalogItems.
+  """Creates catalog item records.
+
+    The ``PTransform`` returns a ``PCollectionTuple`` of successfully created
+    catalog items (``created_catalog_items``) and failures
+    (``failed_catalog_items``).

     Example usage::

-      pipeline | CreateCatalogItem(
-        project='example-gcp-project',
-        catalog_name='my-catalog')
+      result = (
+          pipeline
+          | CreateCatalogItem(
+              project='example-gcp-project', catalog_name='my-catalog'))
+      created = result.created_catalog_items
     """
   def __init__(
       self,
@@ -123,13 +127,15 @@ class CreateCatalogItem(PTransform):
       raise ValueError(
           """GCP project name needs to be specified in "project" pipeline
             option""")
-    return pcoll | ParDo(
+    pardo = ParDo(
         _CreateCatalogItemFn(
             self.project,
             self.retry,
             self.timeout,
             self.metadata,
             self.catalog_name))
+    return pcoll | pardo.with_outputs(
+        FAILED_CATALOG_ITEMS, main='created_catalog_items')


 class _CreateCatalogItemFn(DoFn):

PATCH

echo "Patch applied successfully."
