#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if the fix is already applied, exit
if grep -q 'static_cast<decltype({b})>({value_to_metal(c)})' torch/_inductor/codegen/mps.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/torch/_inductor/codegen/mps.py b/torch/_inductor/codegen/mps.py
index 05d0e84c681ad..4e409238d0b72 100644
--- a/torch/_inductor/codegen/mps.py
+++ b/torch/_inductor/codegen/mps.py
@@ -240,13 +240,17 @@ def masked(mask: CSEVariable, body: sympy.Expr, other: CSEVariable) -> str:
             )
             with V.kernel.compute.indent():
                 V.kernel.compute.splice(scoped_body)
-                V.kernel.compute.writeline(f"{var} = {rc};")
-            V.kernel.compute.writeline(f"}} else {var} = {other_str};")
+                V.kernel.compute.writeline(
+                    f"{var} = static_cast<decltype({var})>({rc});"
+                )
+            V.kernel.compute.writeline(
+                f"}} else {var} = static_cast<decltype({var})>({other_str});"
+            )
         return var

     @staticmethod
     def where(a: OpVarT, b: OpVarT, c: OpVarT) -> str:
-        return f"{a} ? {b} : {value_to_metal(c)}"
+        return f"{a} ? {b} : static_cast<decltype({b})>({value_to_metal(c)})"

     @staticmethod
     def remainder(a: OpVarT, b: OpVarT) -> str:

PATCH

echo "Patch applied successfully."
