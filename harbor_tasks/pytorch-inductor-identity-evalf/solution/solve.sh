#!/usr/bin/env bash
set -euo pipefail
cd /workspace/pytorch

# Idempotent: skip if already applied
grep -q '_identity_atom_compare' torch/utils/_sympy/functions.py && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/torch/utils/_sympy/functions.py b/torch/utils/_sympy/functions.py
index ee04c2461f3c6..5102afd9b530e 100644
--- a/torch/utils/_sympy/functions.py
+++ b/torch/utils/_sympy/functions.py
@@ -1366,6 +1366,38 @@ class Identity(sympy.Function):
     def __int__(self) -> int:
         # pyrefly: ignore [missing-attribute]
         return int(self.args[0])

+    def _identity_atom_compare(self, other, op):
+        """
+        Fast path for comparing wrapped numeric atomics against other numeric atomics.
+        Keep compound expressions on SymPy's default symbolic path.
+        """
+        arg = self.args[0]
+        if isinstance(other, int):
+            other = sympy.Integer(other)
+        if not isinstance(other, sympy.Expr):
+            return None
+        if not (arg.is_Atom and arg.is_number and arg.is_comparable):
+            return None
+        if not (other.is_Atom and other.is_number and other.is_comparable):
+            return None
+        return sympy.S.true if op(arg, other) else sympy.S.false
+
+    def __ge__(self, other):
+        out = self._identity_atom_compare(other, lambda a, b: a >= b)
+        return out if out is not None else super().__ge__(other)
+
+    def __gt__(self, other):
+        out = self._identity_atom_compare(other, lambda a, b: a > b)
+        return out if out is not None else super().__gt__(other)
+
+    def __le__(self, other):
+        out = self._identity_atom_compare(other, lambda a, b: a <= b)
+        return out if out is not None else super().__le__(other)
+
+    def __lt__(self, other):
+        out = self._identity_atom_compare(other, lambda a, b: a < b)
+        return out if out is not None else super().__lt__(other)
+
     def __float__(self) -> float:
         # pyrefly: ignore [missing-attribute]
         return float(self.args[0])

PATCH
