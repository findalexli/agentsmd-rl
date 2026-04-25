#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

# Check if patch is already applied
if grep -q 'float8_' src/transformers/modeling_utils.py && grep -q 'float4_' src/transformers/modeling_utils.py; then
    # Check if it's in the get_state_dict_dtype function context (not just anywhere)
    if python3 -c "
import ast
with open('src/transformers/modeling_utils.py') as f:
    source = f.read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'get_state_dict_dtype':
        func_src = source.splitlines()[node.lineno-1:node.end_lineno]
        func_text = '\n'.join(func_src)
        if 'float8_' in func_text and 'float4_' in func_text:
            exit(0)
exit(1)
"; then
        echo "Patch already applied."
        exit 0
    fi
fi

git apply - <<'PATCH'
diff --git a/src/transformers/modeling_utils.py b/src/transformers/modeling_utils.py
index 1930774ae3e0..ff56e2db03ac 100644
--- a/src/transformers/modeling_utils.py
+++ b/src/transformers/modeling_utils.py
@@ -259,7 +259,8 @@ def get_state_dict_dtype(state_dict):
     Returns the first found floating dtype in `state_dict` if there is one, otherwise returns the first dtype.
     """
     for t in state_dict.values():
-        if t.is_floating_point():
+        # We cannot instantiate a whole model under float4/8_xxx dtypes (torch does not allow setting them as default dtype)
+        if t.is_floating_point() and "float8_" not in str(t.dtype) and "float4_" not in str(t.dtype):
             return t.dtype

     # if no floating dtype was found return whatever the first dtype is

PATCH
