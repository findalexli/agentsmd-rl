#!/bin/bash
set -e

cd /workspace/dagster

# Check if already patched (idempotency)
if grep -q "sections/api/apidocs/" docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py; then
    echo "Already patched, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py b/docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py
index 258c135c5ec7c..53c913ed9c141 100644
--- a/docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py
+++ b/docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py
@@ -174,17 +174,14 @@ def get_child_as(node: nodes.Node, index: int, node_type: type[T_Node]) -> T_Nod
 def transform_inventory_uri(uri: str) -> str:
     """Transform Sphinx source paths to final documentation URLs.

-    The Sphinx source files live under a ``sections/`` directory, but the
-    built documentation is served without that prefix.  For example::
-
-        sections/api/dagster/pipes        -> api/dagster/pipes
-        sections/integrations/libraries/… -> integrations/libraries/…
-
-    Stripping the ``sections/`` prefix aligns the inventory URIs with the
-    actual URL structure produced by the build-api-docs script.
+    Transforms paths like:
+        sections/api/apidocs/dagster/internals/
+    to:
+        api/dagster/internals
     """
-    if uri.startswith("sections/"):
-        transformed = uri[len("sections/") :]
+    # Remove the 'sections/api/apidocs/' prefix
+    if uri.startswith("sections/api/apidocs/"):
+        transformed = uri.replace("sections/api/apidocs/", "api/", 1)
         # Remove trailing slash if present
         if transformed.endswith("/"):
             transformed = transformed[:-1]
PATCH

echo "Patch applied successfully"
