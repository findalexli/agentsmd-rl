#!/bin/bash
set -e

cd /workspace/superset

# Idempotency check - skip if patch already applied
if grep -q "register_superset_auth_view = True" superset/security/manager.py; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/superset/security/manager.py b/superset/security/manager.py
index 32bc75e079e0..2c10cd8ce02f 100644
--- a/superset/security/manager.py
+++ b/superset/security/manager.py
@@ -259,6 +259,10 @@ class SupersetSecurityManager(  # pylint: disable=too-many-public-methods
     SecurityManager
 ):
     userstatschartview = None
+    register_superset_auth_view = True
+    """Set to False in subclasses that provide their own auth view."""
+    register_superset_registeruser_view = True
+    """Set to False in subclasses that provide their own register user view."""
     READ_ONLY_MODEL_VIEWS = {"Database", "DynamicPlugin"}

     role_api = SupersetRoleApi
@@ -3167,10 +3171,12 @@ def is_admin(self) -> bool:
     def register_views(self) -> None:
         from superset.views.auth import SupersetAuthView, SupersetRegisterUserView

-        self.auth_view = self.appbuilder.add_view_no_menu(SupersetAuthView)
-        self.registeruser_view = self.appbuilder.add_view_no_menu(
-            SupersetRegisterUserView
-        )
+        if self.register_superset_auth_view:
+            self.auth_view = self.appbuilder.add_view_no_menu(SupersetAuthView)
+        if self.register_superset_registeruser_view:
+            self.registeruser_view = self.appbuilder.add_view_no_menu(
+                SupersetRegisterUserView
+            )

         # Apply rate limiting to auth view if enabled
         # This needs to be done after the view is added, otherwise the blueprint
PATCH

echo "Patch applied successfully."
