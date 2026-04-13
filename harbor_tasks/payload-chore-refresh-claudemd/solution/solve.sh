#!/bin/bash
# Gold patch for adding proper documentation to default_user_agent function

cat > /tmp/patch.diff << 'EOF'
diff --git a/src/requests/utils.py b/src/requests/utils.py
--- a/src/requests/utils.py
+++ b/src/requests/utils.py
@@ -878,6 +878,9 @@ def prepend_scheme_if_needed(url, scheme):
 def default_user_agent(name="python-requests"):
     """
     Return a string representing the default user agent.
-
+    Includes the library name and version number.
+    Example: 'python-requests/2.31.0'
+
+    :param name: The name to use in the user agent string. Defaults to 'python-requests'.
     :rtype: str
     """
     return f"{name}/{__version__}"
EOF

# Apply the patch
cd /workspace/requests && git apply /tmp/patch.diff
