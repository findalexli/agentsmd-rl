#!/usr/bin/env bash
set -euo pipefail

cd /workspace/anomalib

# Idempotency guard
if grep -qF "You are an expert Python developer who writes high-quality, Google-style docstri" ".cursor/rules/python_docstrings.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/python_docstrings.mdc b/.cursor/rules/python_docstrings.mdc
@@ -0,0 +1,60 @@
+---
+description: Standards for Python docstrings using Google style
+globs: **/*.py
+---
+
+# Python Docstring Rules
+
+You are an expert Python developer who writes high-quality, Google-style docstrings.
+
+## General Guidelines
+
+-   **Style:** Use Google-style docstrings.
+-   **Line Length:** Limit docstrings to 120 characters per line.
+-   **Structure:**
+    1.  **Short Description:** A concise summary of the function, class, or module.
+    2.  **Longer Explanation:** (Optional) detailed description of the behavior.
+    3.  **Args:** Description of arguments.
+    4.  **Returns:** Description of return values.
+    5.  **Raises:** (Optional) Description of raised exceptions.
+    6.  **Example:** Usage examples using doctest style.
+
+## Formatting Details
+
+### Args Section
+
+-   List each argument with its type and a description.
+-   Format: `param_name (type): Description. Defaults to value.`
+-   If types are long, they can be included in the description or wrapped.
+
+### Returns Section
+
+-   Describe the return value and its type.
+-   Format: `type: Description.`
+
+### Example Section
+
+-   Use `>>>` for code examples (doctest style).
+-   Show the expected output on the following lines.
+
+## Example
+
+```python
+def my_function(param1: int, param2: str = "default") -> bool:
+    """Short description.
+
+    A longer explanation.
+
+    Args:
+        param1 (int): Explanation of param1.
+        param2 (str): Explanation of param2. Defaults to "default".
+
+    Returns:
+        bool: Explanation of the return value.
+
+    Example:
+        >>> my_function(1, "test")
+        True
+    """
+    return True
+```
PATCH

echo "Gold patch applied."
