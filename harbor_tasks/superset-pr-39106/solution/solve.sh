#!/bin/bash
# Gold solution for superset-mcp-auth-valueerror-fallback
# Applies the fix from PR apache/superset#39106

set -e

cd /workspace/superset

# Check if patch is already applied (idempotency)
if grep -q "MCP user resolution failed, denying request" superset/mcp_service/auth.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/superset/mcp_service/auth.py b/superset/mcp_service/auth.py
index 00b8d70e3489..d72a30b5587a 100644
--- a/superset/mcp_service/auth.py
+++ b/superset/mcp_service/auth.py
@@ -487,26 +487,17 @@ def _setup_user_context() -> User | None:
                 _cleanup_session_on_error()
                 continue
             logger.error("DB connection failed on retry during user setup: %s", e)
+            _cleanup_session_on_error()
             raise
         except ValueError as e:
-            # JWT user resolution failed (e.g. SAML subject not in DB).
-            # Log a security warning but fall back to middleware-provided
-            # g.user if available. This handles cases where the JWT
-            # resolver username format doesn't match the DB username
-            # (e.g., SAML subject vs email). A separate story should
-            # investigate whether any deployments hit this path and
-            # migrate them before removing the fallback entirely.
-            if has_request_context() and hasattr(g, "user") and g.user:
-                logger.warning(
-                    "SECURITY: JWT user resolution failed (%s), falling "
-                    "back to middleware-provided g.user=%s. This fallback "
-                    "should be investigated and removed once all "
-                    "deployments use consistent username resolution.",
-                    e,
-                    g.user.username,
-                )
-                user = g.user
-                break
+            # User resolution failed — fail closed. Do not fall back to
+            # g.user from middleware, as that could allow a request to
+            # proceed as a different user in multi-tenant deployments.
+            # Clear g.user so error/audit logging doesn't attribute
+            # the denied request to the middleware-provided identity.
+            logger.error("MCP user resolution failed, denying request: %s", e)
+            if has_request_context():
+                g.pop("user", None)
             raise

     g.user = user
PATCH

echo "Gold patch applied successfully."
