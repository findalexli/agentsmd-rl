#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

# Idempotency: skip if the gold patch is already applied. The distinctive
# string is the new helper function added in superset/mcp_service/system/schemas.py.
if grep -q 'def serialize_user_object(user: Any) -> UserInfo | None' \
        superset/mcp_service/system/schemas.py 2>/dev/null \
   && grep -q 'role.name for role in raw_roles' \
        superset/mcp_service/system/schemas.py 2>/dev/null; then
    echo "Gold patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset/mcp_service/chart/schemas.py b/superset/mcp_service/chart/schemas.py
index 28fdf1b0d88b..c5a2098442f9 100644
--- a/superset/mcp_service/chart/schemas.py
+++ b/superset/mcp_service/chart/schemas.py
@@ -45,6 +45,7 @@
 from superset.mcp_service.common.error_schemas import ChartGenerationError
 from superset.mcp_service.system.schemas import (
     PaginationInfo,
+    serialize_user_object,
     TagInfo,
     UserInfo,
 )
@@ -278,8 +279,9 @@ def serialize_chart_object(chart: ChartLike | None) -> ChartInfo | None:
         if getattr(chart, "tags", None)
         else [],
         owners=[
-            UserInfo.model_validate(owner, from_attributes=True)
+            info
             for owner in getattr(chart, "owners", [])
+            if (info := serialize_user_object(owner)) is not None
         ]
         if getattr(chart, "owners", None)
         else [],
diff --git a/superset/mcp_service/dashboard/schemas.py b/superset/mcp_service/dashboard/schemas.py
index 7b002677c698..e09b3871ce6c 100644
--- a/superset/mcp_service/dashboard/schemas.py
+++ b/superset/mcp_service/dashboard/schemas.py
@@ -87,6 +87,7 @@
 from superset.mcp_service.system.schemas import (
     PaginationInfo,
     RoleInfo,
+    serialize_user_object,
     TagInfo,
     UserInfo,
 )
@@ -109,19 +110,8 @@ def create(cls, error: str, error_type: str) -> "DashboardError":
         return cls(error=error, error_type=error_type, timestamp=datetime.now())


-def serialize_user_object(user: Any) -> UserInfo | None:
-    """Serialize a user object to UserInfo"""
-    if not user:
-        return None
-
-    return UserInfo(
-        id=getattr(user, "id", None),
-        username=getattr(user, "username", None),
-        first_name=getattr(user, "first_name", None),
-        last_name=getattr(user, "last_name", None),
-        email=getattr(user, "email", None),
-        active=getattr(user, "active", None),
-    )
+# serialize_user_object is imported from system.schemas and re-exported here
+# for backward compatibility with dashboard tool modules.


 def serialize_tag_object(tag: Any) -> TagInfo | None:
@@ -502,8 +492,9 @@ def dashboard_serializer(dashboard: "Dashboard") -> DashboardInfo:
         changed_on_humanized=dashboard.changed_on_humanized,
         chart_count=len(dashboard.slices) if dashboard.slices else 0,
         owners=[
-            UserInfo.model_validate(owner, from_attributes=True)
+            info
             for owner in dashboard.owners
+            if (info := serialize_user_object(owner)) is not None
         ]
         if dashboard.owners
         else [],
diff --git a/superset/mcp_service/dataset/schemas.py b/superset/mcp_service/dataset/schemas.py
index b0dad96b5926..14dd329e8f7d 100644
--- a/superset/mcp_service/dataset/schemas.py
+++ b/superset/mcp_service/dataset/schemas.py
@@ -37,6 +37,7 @@
 from superset.mcp_service.common.cache_schemas import MetadataCacheControl
 from superset.mcp_service.system.schemas import (
     PaginationInfo,
+    serialize_user_object,
     TagInfo,
     UserInfo,
 )
@@ -338,8 +339,9 @@ def serialize_dataset_object(dataset: Any) -> DatasetInfo | None:
         if getattr(dataset, "tags", None)
         else [],
         owners=[
-            UserInfo.model_validate(owner, from_attributes=True)
+            info
             for owner in getattr(dataset, "owners", [])
+            if (info := serialize_user_object(owner)) is not None
         ]
         if getattr(dataset, "owners", None)
         else [],
diff --git a/superset/mcp_service/system/schemas.py b/superset/mcp_service/system/schemas.py
index f1667471693f..9810cc4d3b3e 100644
--- a/superset/mcp_service/system/schemas.py
+++ b/superset/mcp_service/system/schemas.py
@@ -25,7 +25,7 @@
 from __future__ import annotations

 from datetime import datetime
-from typing import Dict, List
+from typing import Any, Dict, List

 from pydantic import BaseModel, ConfigDict, Field

@@ -170,6 +170,29 @@ class UserInfo(BaseModel):
     )


+def serialize_user_object(user: Any) -> UserInfo | None:
+    """Serialize a user ORM object to UserInfo, extracting role names as strings."""
+    if not user:
+        return None
+
+    user_roles: list[str] = []
+    if (raw_roles := getattr(user, "roles", None)) is not None:
+        try:
+            user_roles = [role.name for role in raw_roles if hasattr(role, "name")]
+        except TypeError:
+            user_roles = []
+
+    return UserInfo(
+        id=getattr(user, "id", None),
+        username=getattr(user, "username", None),
+        first_name=getattr(user, "first_name", None),
+        last_name=getattr(user, "last_name", None),
+        email=getattr(user, "email", None),
+        active=getattr(user, "active", None),
+        roles=user_roles,
+    )
+
+
 class TagInfo(BaseModel):
     id: int | None = None
     name: str | None = None
PATCH

echo "Gold patch applied."
