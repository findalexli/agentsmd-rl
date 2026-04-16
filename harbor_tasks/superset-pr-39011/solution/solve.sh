#!/bin/bash
# Solution script for superset-mcp-dashboard-draft task
# Applies the gold patch to fix the MCP dashboard default published state

set -e

cd /workspace/superset

# Check for idempotency - skip if already patched
if grep -q 'default=False, description="Whether to publish the dashboard"' superset/mcp_service/dashboard/schemas.py; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/superset/mcp_service/dashboard/schemas.py b/superset/mcp_service/dashboard/schemas.py
index be2860e07cbe..cc01255eea4b 100644
--- a/superset/mcp_service/dashboard/schemas.py
+++ b/superset/mcp_service/dashboard/schemas.py
@@ -445,7 +445,7 @@ class GenerateDashboardRequest(BaseModel):
     )
     description: str | None = Field(None, description="Description for the dashboard")
     published: bool = Field(
-        default=True, description="Whether to publish the dashboard"
+        default=False, description="Whether to publish the dashboard"
     )


PATCH

echo "Patch applied successfully."
