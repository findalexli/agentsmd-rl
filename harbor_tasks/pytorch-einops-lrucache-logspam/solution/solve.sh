#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pytorch

# Check if already applied (the fix comments out the version check)
if grep -q '# if einops.__version__ >= "0.8.2":' torch/_dynamo/decorators.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/test/dynamo/test_einops.py b/test/dynamo/test_einops.py
index fcd86e50b944c..2c445be38ee8e 100644
--- a/test/dynamo/test_einops.py
+++ b/test/dynamo/test_einops.py
@@ -11,6 +11,7 @@
 from torch.testing._internal.common_utils import (
     instantiate_parametrized_tests,
     parametrize,
+    xfailIf,
 )


@@ -190,6 +191,7 @@ def f(x):
             else:
                 self.assertIn(einops_method, output)

+    @xfailIf(einops_version == "0.8.2")
     @parametrize(
         "method",
         ["reduce", "repeat", "pack", "unpack", "einsum", "rearrange"],
@@ -222,6 +224,15 @@ def test_einops_method(self, method):
             self.fail(method)
         self._run_in_subprocess(flag, method, einops_method, snippet)

+    def test_no_warning(self):
+        # checks that this doesn't produce any warnings
+        @torch.compile(backend="eager", fullgraph=True)
+        def fn(x):
+            return einops.rearrange(x, "... -> (...)")
+
+        x = torch.randn(5)
+        self.assertNotWarn(lambda: fn(x))
+

 instantiate_parametrized_tests(
     TestEinops,
diff --git a/torch/_dynamo/decorators.py b/torch/_dynamo/decorators.py
index ed1354555a7d7..b444eaea9fb70 100644
--- a/torch/_dynamo/decorators.py
+++ b/torch/_dynamo/decorators.py
@@ -1156,14 +1156,15 @@ def mark_static_address(t: Any, guard: bool = False) -> None:
 def _allow_in_graph_einops() -> None:
     import einops

-    if einops.__version__ >= "0.8.2":
-        if hasattr(einops, "einops") and hasattr(einops.einops, "get_backend"):
-            # trigger backend registration up front to avoid a later guard failure
-            # that would otherwise cause a recompilation
-            einops.rearrange(torch.randn(1), "i -> i")
-
-        # einops 0.8.2+ don't need explicit allow_in_graph calls
-        return
+    # There is a lru_cache logspam issue with einops when allow_in_graph is not
+    # used. Disabling this for now until the lru_cache issue is resolved.
+    # if einops.__version__ >= "0.8.2":
+    #     if hasattr(einops, "einops") and hasattr(einops.einops, "get_backend"):
+    #         # trigger backend registration up front to avoid a later guard failure
+    #         # that would otherwise cause a recompilation
+    #         einops.rearrange(torch.randn(1), "i -> i")
+    #     # einops 0.8.2+ don't need explicit allow_in_graph calls
+    #     return

     try:
         allow_in_graph(einops.rearrange)

PATCH

echo "Patch applied successfully."
