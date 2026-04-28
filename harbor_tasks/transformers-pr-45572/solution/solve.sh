#!/bin/bash
set -e
cd /workspace/transformers

# Verify base state
grep -q 'masked_fill(~score_mask.bool(), 0.0)' src/transformers/models/dots1/modular_dots1.py || {
    echo "IDEMPOTENT: fix already applied or unexpected state"
    exit 0
}

git apply <<'PATCH'
diff --git a/src/transformers/models/dots1/modeling_dots1.py b/src/transformers/models/dots1/modeling_dots1.py
index 399194648663..95b21258ffd5 100644
--- a/src/transformers/models/dots1/modeling_dots1.py
+++ b/src/transformers/models/dots1/modeling_dots1.py
@@ -368,7 +368,7 @@ def __init__(self, config):
         self.top_k = config.num_experts_per_tok

     def route_tokens_to_experts(self, router_logits):
-        router_logits = router_logits.sigmoid()  # main diff with deepseekv3
+        router_logits = router_logits.sigmoid()
         router_logits_for_choice = router_logits + self.gate.e_score_correction_bias
         group_scores = (
             router_logits_for_choice.view(-1, self.n_group, self.n_routed_experts // self.n_group)
@@ -383,7 +383,7 @@ def route_tokens_to_experts(self, router_logits):
             .expand(-1, self.n_group, self.n_routed_experts // self.n_group)
             .reshape(-1, self.n_routed_experts)
         )
-        scores_for_choice = router_logits_for_choice.masked_fill(~score_mask.bool(), 0.0)
+        scores_for_choice = router_logits_for_choice.masked_fill(~score_mask.bool(), float("-inf"))
         topk_indices = torch.topk(scores_for_choice, k=self.top_k, dim=-1, sorted=False)[1]
         topk_weights = router_logits.gather(1, topk_indices)
         if self.norm_topk_prob:
diff --git a/src/transformers/models/dots1/modular_dots1.py b/src/transformers/models/dots1/modular_dots1.py
index d390037d0820..06402d63e28c 100644
--- a/src/transformers/models/dots1/modular_dots1.py
+++ b/src/transformers/models/dots1/modular_dots1.py
@@ -11,7 +11,6 @@
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
-import torch
 from huggingface_hub.dataclasses import strict

 from ...configuration_utils import PreTrainedConfig
@@ -156,30 +155,7 @@ class Dots1TopkRouter(DeepseekV3TopkRouter):


 class Dots1MoE(DeepseekV3MoE):
-    def route_tokens_to_experts(self, router_logits):
-        router_logits = router_logits.sigmoid()  # main diff with deepseekv3
-        router_logits_for_choice = router_logits + self.gate.e_score_correction_bias
-        group_scores = (
-            router_logits_for_choice.view(-1, self.n_group, self.n_routed_experts // self.n_group)
-            .topk(2, dim=-1)[0]
-            .sum(dim=-1)
-        )
-        group_idx = torch.topk(group_scores, k=self.topk_group, dim=-1, sorted=False)[1]
-        group_mask = torch.zeros_like(group_scores)
-        group_mask.scatter_(1, group_idx, 1)
-        score_mask = (
-            group_mask.unsqueeze(-1)
-            .expand(-1, self.n_group, self.n_routed_experts // self.n_group)
-            .reshape(-1, self.n_routed_experts)
-        )
-        scores_for_choice = router_logits_for_choice.masked_fill(~score_mask.bool(), 0.0)
-        topk_indices = torch.topk(scores_for_choice, k=self.top_k, dim=-1, sorted=False)[1]
-        topk_weights = router_logits.gather(1, topk_indices)
-        if self.norm_topk_prob:
-            denominator = topk_weights.sum(dim=-1, keepdim=True) + 1e-20
-            topk_weights /= denominator
-        topk_weights = topk_weights * self.routed_scaling_factor
-        return topk_indices, topk_weights
+    pass


 class Dots1DecoderLayer(DeepseekV3DecoderLayer):

PATCH

# Verify the fix is applied
grep -q 'float("-inf")' src/transformers/models/dots1/modeling_dots1.py
grep -q 'class Dots1MoE(DeepseekV3MoE):' src/transformers/models/dots1/modular_dots1.py
