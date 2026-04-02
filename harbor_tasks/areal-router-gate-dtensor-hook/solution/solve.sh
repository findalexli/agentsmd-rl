#!/usr/bin/env bash
set -euo pipefail
cd /workspace/AReaL

# Idempotent: check if already applied
if grep -q "class RouterGateLinear" areal/experimental/models/archon/moe/router.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/experimental/models/archon/moe/router.py b/areal/experimental/models/archon/moe/router.py
index 4f71356f5..56433df84 100644
--- a/areal/experimental/models/archon/moe/router.py
+++ b/areal/experimental/models/archon/moe/router.py
@@ -71,6 +71,39 @@ def router_gating_linear(
     return F.linear(input, weight)


+class RouterGateLinear(nn.Linear):
+    """Router gate linear that performs GEMM in higher precision.
+
+    Wraps :func:`router_gating_linear` inside an :class:`~torch.nn.Linear`
+    subclass so that DTensor hooks registered by :class:`ReplicateParallel`
+    fire correctly when the module is called via ``self.gate(x)``.
+
+    When ``router_dtype`` is set, both the forward and backward passes run
+    the GEMM in ``router_dtype`` while saving activations in the original
+    dtype for memory efficiency (via :class:`RouterGatingLinearFunction`).
+    When ``router_dtype`` is ``None``, falls back to standard
+    :func:`~torch.nn.functional.linear`.
+
+    Args:
+        in_features: Size of each input sample.
+        out_features: Size of each output sample.
+        router_dtype: Dtype to use for the gate GEMM. ``None`` means use the
+            model dtype unchanged.
+    """
+
+    def __init__(
+        self,
+        in_features: int,
+        out_features: int,
+        router_dtype: torch.dtype | None = None,
+    ):
+        super().__init__(in_features, out_features, bias=False)
+        self.router_dtype = router_dtype
+
+    def forward(self, input: torch.Tensor) -> torch.Tensor:
+        return router_gating_linear(input, self.weight, self.router_dtype)
+
+
 class TokenChoiceTopKRouter(nn.Module):
     """Token-choice routing with top-k expert selection.

@@ -110,7 +143,7 @@ class TokenChoiceTopKRouter(nn.Module):
         _debug_force_load_balance: bool = False,
     ):
         super().__init__()
-        self.gate = nn.Linear(dim, num_experts, bias=False)
+        self.gate = RouterGateLinear(dim, num_experts, router_dtype=router_dtype)
         self.num_experts = num_experts
         self.top_k = top_k
         self.score_func = score_func
@@ -212,7 +245,7 @@ class TokenChoiceTopKRouter(nn.Module):
                 - num_tokens_per_expert: Token count per expert, shape (num_experts,).
         """
         # Compute gate scores: (num_tokens, num_experts)
-        scores = router_gating_linear(x, self.gate.weight, self.router_dtype)
+        scores = self.gate(x)

         # Apply scoring function in float32 to avoid loss explosion
         if self.score_func == "sigmoid":

PATCH
