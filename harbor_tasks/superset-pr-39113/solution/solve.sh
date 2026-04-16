#!/bin/bash
set -e

cd /workspace/superset

# Idempotency check - skip if already patched
if grep -q 'datetime.now(timezone.utc)' superset/mcp_service/database/schemas.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the PR fix using a heredoc patch
# PR #39113: Fix timezone-aware datetime handling
patch -p1 << 'EOF'
diff --git a/superset/mcp_service/database/schemas.py b/superset/mcp_service/database/schemas.py
index 3eb9cffe4f..ff2821288b 100644
--- a/superset/mcp_service/database/schemas.py
+++ b/superset/mcp_service/database/schemas.py
@@ -274,9 +274,11 @@ class DatabaseError(BaseModel):
     @classmethod
     def create(cls, error: str, error_type: str) -> "DatabaseError":
         """Create a standardized DatabaseError with timestamp."""
-        from datetime import datetime
+        from datetime import datetime, timezone

-        return cls(error=error, error_type=error_type, timestamp=datetime.now())
+        return cls(
+            error=error, error_type=error_type, timestamp=datetime.now(timezone.utc)
+        )


 class GetDatabaseInfoRequest(MetadataCacheControl):
@@ -306,7 +308,8 @@ def _humanize_timestamp(dt: datetime | None) -> str | None:
     """Convert a datetime to a humanized string like '2 hours ago'."""
     if dt is None:
         return None
-    return humanize.naturaltime(datetime.now() - dt)
+    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
+    return humanize.naturaltime(now - dt)


 def serialize_database_object(database: Any) -> DatabaseInfo | None:
EOF

echo "Patch applied successfully."
