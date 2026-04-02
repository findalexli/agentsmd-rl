#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pytorch

# Idempotency check: if safe_mod already exists in utils.h, patch is applied
if grep -q 'safe_mod' c10/metal/utils.h 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/c10/metal/utils.h b/c10/metal/utils.h
index 8d58d0dfdd1f2..cc946e4fc4aa4 100644
--- a/c10/metal/utils.h
+++ b/c10/metal/utils.h
@@ -189,6 +189,18 @@ inline common_dtype<T, U> floor_divide(T x, U y) {
   return ::metal::floor(x / y);
 }

+// Workaround for Metal compiler bug: the compiler produces wrong results
+// when optimizing fused (x / A) % B expressions for integral types.
+template <
+    typename T,
+    typename U,
+    ::metal::enable_if_t<
+        is_scalar_integral_v<T> && is_scalar_integral_v<U>,
+        bool> = true>
+inline common_dtype<T, U> safe_mod(volatile T x, U y) {
+  return x % y;
+}
+
 // fmod
 template <
     typename T,
diff --git a/torch/_inductor/codegen/mps.py b/torch/_inductor/codegen/mps.py
index 4e409238d0b72..b413a6f43f636 100644
--- a/torch/_inductor/codegen/mps.py
+++ b/torch/_inductor/codegen/mps.py
@@ -80,6 +80,9 @@ def _print_FloorDiv(self, expr: sympy.Expr) -> str:

     def _print_ModularIndexing(self, expr: sympy.Expr) -> str:
         x, div, mod = expr.args
+        # Workaround for Metal compiler bug with fused (x / A) % B, see PR 175481
+        use_safe_mod = div == 65536 and (mod & (mod - 1)) != 0
+
         x = self.doprint(x)
         if div != 1:
             div = self.doprint(div)
@@ -88,6 +91,8 @@ def _print_ModularIndexing(self, expr: sympy.Expr) -> str:
             else:
                 x = f"metal::floor({x}) / ({div})"
         mod = self.doprint(mod)
+        if use_safe_mod:
+            return f"c10::metal::safe_mod({x}, {mod})"
         return f"({x}) % ({mod})"

     def _print_Min(self, expr: sympy.Expr) -> str:

PATCH

echo "Patch applied successfully."
