#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotency check: if get_prompt_token_ids_cpu method already exists, patch is applied
if grep -q 'def get_prompt_token_ids_cpu' vllm/v1/pool/metadata.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/model_executor/layers/pooler/common.py b/vllm/model_executor/layers/pooler/common.py
index d8aa78e70cc6..55fc4b457689 100644
--- a/vllm/model_executor/layers/pooler/common.py
+++ b/vllm/model_executor/layers/pooler/common.py
@@ -18,7 +18,7 @@
 @dataclass(frozen=True)
 class PoolingParamsUpdate:
     requires_token_ids: bool = False
-    """Set this flag to enable `get_prompt_token_ids` for your pooler."""
+    """Set this flag to enable prompt token IDs for your pooler."""

     def __or__(self, other: "PoolingParamsUpdate") -> "PoolingParamsUpdate":
         return PoolingParamsUpdate(
diff --git a/vllm/model_executor/layers/pooler/special.py b/vllm/model_executor/layers/pooler/special.py
index 686072632685..d06663b5b947 100644
--- a/vllm/model_executor/layers/pooler/special.py
+++ b/vllm/model_executor/layers/pooler/special.py
@@ -146,17 +146,19 @@ def forward(
     ) -> PoolerOutput:
         pooled_outputs = self.pooler(hidden_states, pooling_metadata)
         assert isinstance(pooled_outputs, list)
+        prompt_token_ids = pooling_metadata.get_prompt_token_ids_cpu()

-        for i, prompt_len in enumerate(pooling_metadata.prompt_lens):
+        for i, (prompt_len, token_ids) in enumerate(
+            zip(pooling_metadata.prompt_lens, prompt_token_ids)
+        ):
             pooled_data = pooled_outputs[i]
             assert (
                 isinstance(pooled_data, torch.Tensor)
                 and pooled_data.shape[0] == prompt_len
             )
-            token_ids = pooling_metadata.prompt_token_ids[i, :prompt_len]
-            if token_ids[0] == self.bos_token_id:
+            if int(token_ids[0]) == self.bos_token_id:
                 pooled_data = pooled_data[1:]
-            if token_ids[-1] == self.eos_token_id:
+            if int(token_ids[-1]) == self.eos_token_id:
                 pooled_data = pooled_data[:-1]
             pooled_outputs[i] = pooled_data.squeeze(-1)

diff --git a/vllm/model_executor/models/bert.py b/vllm/model_executor/models/bert.py
index 0cdf4f70e5bd..01854b96d56f 100644
--- a/vllm/model_executor/models/bert.py
+++ b/vllm/model_executor/models/bert.py
@@ -638,25 +638,26 @@ def forward(
         lens: list[int] = lens_tensor.tolist()
         B: int = len(lens)

-        token_ids = pooling_metadata.prompt_token_ids
+        prompt_token_ids = pooling_metadata.get_prompt_token_ids_cpu()
         offset = 0
         pooled_list: list[torch.Tensor] = []

         for i in range(B):
             L = int(lens[i])
             hs = hidden_states[offset : offset + L]
+            token_ids = prompt_token_ids[i]

             start_idx = 0
             end_idx = L
-            if self.remove_cls_sep and token_ids is not None:
+            if self.remove_cls_sep:
                 if (
                     self.cls_token_id is not None
-                    and token_ids[i, 0].item() == self.cls_token_id
+                    and int(token_ids[0]) == self.cls_token_id
                 ):
                     start_idx = 1
                 if (
                     self.sep_token_id is not None
-                    and token_ids[i, L - 1].item() == self.sep_token_id
+                    and int(token_ids[L - 1]) == self.sep_token_id
                 ):
                     end_idx = max(start_idx, L - 1)

diff --git a/vllm/model_executor/models/gritlm.py b/vllm/model_executor/models/gritlm.py
index b5c6946b6701..4fb9bc7b0928 100644
--- a/vllm/model_executor/models/gritlm.py
+++ b/vllm/model_executor/models/gritlm.py
@@ -156,10 +156,11 @@ def forward(
         pooling_metadata: PoolingMetadata,
     ) -> SequencePoolingMethodOutput:
         prompt_lens = pooling_metadata.prompt_lens
+        prompt_token_ids = pooling_metadata.get_prompt_token_ids_cpu()
         instr_lens = torch.tensor(
             [
-                self._get_instruction_len(token_ids.cpu().numpy())
-                for token_ids in pooling_metadata.get_prompt_token_ids()
+                self._get_instruction_len(token_ids.numpy())
+                for token_ids in prompt_token_ids
             ],
             device="cpu",
         )
diff --git a/vllm/v1/pool/metadata.py b/vllm/v1/pool/metadata.py
index c9fafe142417..076c87526f0a 100644
--- a/vllm/v1/pool/metadata.py
+++ b/vllm/v1/pool/metadata.py
@@ -50,7 +50,8 @@ class PoolingMetadata:
     """Tensors for pooling."""

     prompt_lens: torch.Tensor  # CPU Tensor
-    prompt_token_ids: torch.Tensor | None
+    prompt_token_ids: torch.Tensor | None  # Model-device tensor
+    prompt_token_ids_cpu: torch.Tensor | None  # CPU tensor
     pooling_params: list[PoolingParams]
     pooling_states: list[PoolingStates]
     pooling_cursor: PoolingCursor | None = None
@@ -73,6 +74,9 @@ def __getitem__(self, indices: slice):
             prompt_token_ids=None
             if self.prompt_token_ids is None
             else self.prompt_token_ids[indices],
+            prompt_token_ids_cpu=None
+            if self.prompt_token_ids_cpu is None
+            else self.prompt_token_ids_cpu[indices],
             pooling_params=self.pooling_params[indices],
             pooling_states=self.pooling_states[indices],
             pooling_cursor=None
@@ -85,7 +89,13 @@ def get_prompt_token_ids(self) -> list[torch.Tensor]:
         assert prompt_token_ids is not None, (
             "Please set `requires_token_ids=True` in `get_pooling_updates`"
         )
+        return [prompt_token_ids[i, :num] for i, num in enumerate(self.prompt_lens)]

+    def get_prompt_token_ids_cpu(self) -> list[torch.Tensor]:
+        prompt_token_ids = self.prompt_token_ids_cpu
+        assert prompt_token_ids is not None, (
+            "Please set `requires_token_ids=True` in `get_pooling_updates`"
+        )
         return [prompt_token_ids[i, :num] for i, num in enumerate(self.prompt_lens)]

     def get_pooling_cursor(self) -> PoolingCursor:
diff --git a/vllm/v1/worker/gpu_input_batch.py b/vllm/v1/worker/gpu_input_batch.py
index 11d57f1d7738..b9cd10544826 100644
--- a/vllm/v1/worker/gpu_input_batch.py
+++ b/vllm/v1/worker/gpu_input_batch.py
@@ -833,8 +833,13 @@ def _make_sampling_metadata(self) -> SamplingMetadata:
         # step pooling during the sampling/pooling process.
         # Hence copy these tensors only when there are requests which
         # need penalties/step_pooler to be applied.
+        prompt_token_ids_cpu = (
+            self._make_prompt_token_ids_cpu_tensor() if needs_prompt_token_ids else None
+        )
         prompt_token_ids = (
-            self._make_prompt_token_ids_tensor() if needs_prompt_token_ids else None
+            prompt_token_ids_cpu.to(device=self.device, non_blocking=True)
+            if prompt_token_ids_cpu is not None
+            else None
         )

         # Only set output_token_ids if required by the current requests'
@@ -891,15 +896,19 @@ def get_pooling_states(self) -> list[PoolingStates]:
     def get_pooling_metadata(self) -> PoolingMetadata:
         pooling_params = self.get_pooling_params()
         pooling_states = self.get_pooling_states()
+        prompt_token_ids_cpu = None
+        if any(p.requires_token_ids for p in pooling_params):
+            prompt_token_ids_cpu = self._make_prompt_token_ids_cpu_tensor()

         return PoolingMetadata(
             prompt_lens=self.num_prompt_tokens_cpu_tensor[: self.num_reqs].clone(),
             prompt_token_ids=self.sampling_metadata.prompt_token_ids,
+            prompt_token_ids_cpu=prompt_token_ids_cpu,
             pooling_params=pooling_params,
             pooling_states=pooling_states,
         )

-    def _make_prompt_token_ids_tensor(self) -> torch.Tensor:
+    def _make_prompt_token_ids_cpu_tensor(self) -> torch.Tensor:
         num_reqs = self.num_reqs
         max_prompt_len = self.num_prompt_tokens[:num_reqs].max()
         prompt_token_ids_cpu_tensor = torch.empty(
@@ -914,7 +923,7 @@ def _make_prompt_token_ids_tensor(self) -> torch.Tensor:
         # token_id of this value.
         for i in range(num_reqs):
             prompt_token_ids[i, self.num_prompt_tokens[i] :] = self.vocab_size
-        return prompt_token_ids_cpu_tensor.to(device=self.device, non_blocking=True)
+        return prompt_token_ids_cpu_tensor

     def make_lora_inputs(
         self, num_scheduled_tokens: np.ndarray, num_sampled_tokens: np.ndarray
diff --git a/vllm/v1/worker/gpu_model_runner.py b/vllm/v1/worker/gpu_model_runner.py
index d44bf74c3a4f..42d784a473ba 100644
--- a/vllm/v1/worker/gpu_model_runner.py
+++ b/vllm/v1/worker/gpu_model_runner.py
@@ -5653,6 +5653,7 @@ def _dummy_pooler_run_task(
         dummy_metadata = PoolingMetadata(
             prompt_lens=dummy_prompt_lens,
             prompt_token_ids=dummy_token_ids,
+            prompt_token_ids_cpu=dummy_token_ids.cpu(),
             pooling_params=[dummy_pooling_params] * num_reqs,
             pooling_states=[PoolingStates() for i in range(num_reqs)],
         )

PATCH

echo "Patch applied successfully."
