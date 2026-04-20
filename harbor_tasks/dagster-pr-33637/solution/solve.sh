#!/bin/bash
set -e

cd /workspace/dagster-io_dagster

# Apply the gold patch to fix the inventory URI transformation
git apply <<'PATCH'
diff --git a/docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py b/docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py
index 53c913ed9c141..258c135c5ec7c 100644
--- a/docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py
+++ b/docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py
@@ -174,14 +174,17 @@ def get_child_as(node: nodes.Node, index: int, node_type: type[T_Node]) -> T_Nod
 def transform_inventory_uri(uri: str) -> str:
     """Transform Sphinx source paths to final documentation URLs.

-    Transforms paths like:
-        sections/api/apidocs/dagster/internals/
-    to:
-        api/dagster/internals
+    The Sphinx source files live under a ``sections/`` directory, but the
+    built documentation is served without that prefix.  For example::
+
+        sections/api/dagster/pipes        -> api/dagster/pipes
+        sections/integrations/libraries/… -> integrations/libraries/…
+
+    Stripping the ``sections/`` prefix aligns the inventory URIs with the
+    actual URL structure produced by the build-api-docs script.
     """
-    # Remove the 'sections/api/apidocs/' prefix
-    if uri.startswith("sections/api/apidocs/"):
-        transformed = uri.replace("sections/api/apidocs/", "api/", 1)
+    if uri.startswith("sections/"):
+        transformed = uri[len("sections/") :]
         # Remove trailing slash if present
         if transformed.endswith("/"):
             transformed = transformed[:-1]
PATCH

# Idempotency check - look for a distinctive line from the patched file
grep -q "sections/" docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py && echo "Patch applied successfully"