#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied (distinctive line from the new helper function)
if grep -q 'def _handle_finished_req(' python/sglang/srt/managers/scheduler_output_processor_mixin.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/python/sglang/srt/configs/model_config.py b/python/sglang/srt/configs/model_config.py
index 0fb0703d4972..89e90516ef12 100644
--- a/python/sglang/srt/configs/model_config.py
+++ b/python/sglang/srt/configs/model_config.py
@@ -232,6 +232,8 @@ def __init__(

         # Cache attributes
         self.hf_eos_token_id = self._get_hf_eos_token_id()
+        # Set by scheduler when reasoning_parser is enabled
+        self.think_end_id: Optional[int] = None

         # multimodal
         self.image_token_id = getattr(
diff --git a/python/sglang/srt/managers/scheduler.py b/python/sglang/srt/managers/scheduler.py
index 67af2d0de943..ceb79f4a1adb 100644
--- a/python/sglang/srt/managers/scheduler.py
+++ b/python/sglang/srt/managers/scheduler.py
@@ -553,6 +553,7 @@ def init_tokenizer(self):
                 reasoning_parser.detector.think_end_token, add_special_tokens=False
             )[0]
             self._think_end_id = self.tokenizer.think_end_id
+            self.model_config.think_end_id = self._think_end_id
         else:
             self._think_end_id = None

diff --git a/python/sglang/srt/managers/scheduler_output_processor_mixin.py b/python/sglang/srt/managers/scheduler_output_processor_mixin.py
index 496cd96656e5..8e7639df1335 100644
--- a/python/sglang/srt/managers/scheduler_output_processor_mixin.py
+++ b/python/sglang/srt/managers/scheduler_output_processor_mixin.py
@@ -406,20 +406,8 @@ def process_batch_result_decode(
                         v.tolist()
                         for v in logits_output.next_token_token_ids_logprobs_val
                     ]
-        else:
-            # for normal spec decoding: unify next_token_ids format
-            next_token_ids = []
-            cum_num_tokens = 0
-            next_token_ids_list = result.next_token_ids.tolist()
-
-            for i, req in enumerate(batch.reqs):
-                accept_length = result.accept_length_per_req_cpu[i]
-                next_token_ids.append(
-                    next_token_ids_list[
-                        cum_num_tokens : cum_num_tokens + accept_length + 1
-                    ]
-                )
-                cum_num_tokens += accept_length + 1
+        # else: Spec V1 — output_ids, check_finished, grammar, and reasoning tokens
+        # are already handled in the verify phase (eagle_info.py / ngram_info.py).

         self.num_generated_tokens += len(batch.reqs)
         if not batch.spec_algorithm.is_none():
@@ -431,24 +419,36 @@ def process_batch_result_decode(

         self.token_to_kv_pool_allocator.free_group_begin()

-        # NOTE: in any case, we should check finish here
-        # if finished, also clean up committed kv cache and over-allocated kv cache here
+        # Spec V1 handles output_ids, check_finished, grammar, and reasoning tokens
+        # in the verify phase. Non-spec and V2 handle them here in post-processing.
+        is_spec_v1 = not batch.spec_algorithm.is_none() and not batch.is_spec_v2

-        # Check finish condition
-        for i, (req, next_token_id) in enumerate(zip(batch.reqs, next_token_ids)):
+        for i, req in enumerate(batch.reqs):
             req: Req

             if self.enable_overlap and (req.finished() or req.is_retracted):
                 # NOTE: This (req.finished() or req.is_retracted) should only happen when overlap scheduling is enabled.
-                # (currently not, e.g. Eagle V1 still check finish during forward)
                 # And all the over-allocated tokens will be freed in `release_kv_cache`.
                 continue

+            if is_spec_v1:
+                self._mamba_prefix_cache_update(req, batch, result, i)
+                req.time_stats.set_last_decode_finish_time()
+                self._handle_finished_req(req, i, logits_output)
+                if req.return_hidden_states and logits_output.hidden_states is not None:
+                    req.hidden_states.append(
+                        logits_output.hidden_states[i].cpu().clone().tolist()
+                    )
+                if req.grammar is not None:
+                    req.grammar.finished = req.finished()
+                continue
+
+            # Non-spec and V2: full post-processing
+            next_token_id = next_token_ids[i]
             new_accepted_len = 1
             if batch.spec_algorithm.is_none():
                 req.output_ids.append(next_token_id)
-            elif batch.is_spec_v2:
-                # Only spec v2's output_ids are updated here.
+            else:
                 req.output_ids.extend(next_token_id)
                 new_accepted_len = len(next_token_id)

@@ -456,39 +456,12 @@ def process_batch_result_decode(

             # Update Mamba last track seqlen
             self._mamba_prefix_cache_update(req, batch, result, i)
-
             req.time_stats.set_last_decode_finish_time()
-
             req.check_finished(new_accepted_len)

-            if (
-                self.server_args.disaggregation_decode_enable_offload_kvcache
-                and not req.finished()
-            ):
-                self.decode_offload_manager.offload_kv_cache(req)
-
-            if req.finished():
-                # delete feature to save memory
-                if req.multimodal_inputs is not None and req.session is None:
-                    req.multimodal_inputs.release_features()
-                self.maybe_collect_routed_experts(req)
-
-                if self.server_args.disaggregation_decode_enable_offload_kvcache:
-                    # Asynchronously offload KV cache; release_kv_cache will be called after Device->Host transfer completes
-                    if not self.decode_offload_manager.offload_kv_cache(req):
-                        self.decode_offload_manager.finalize_release_on_finish(req)
-                else:
-                    if self.enable_hisparse:
-                        self.hisparse_coordinator.request_finished(req)
-                    release_kv_cache(req, self.tree_cache)
-
-                req.time_stats.set_completion_time()
-
-            self.maybe_collect_customized_info(i, req, logits_output)
-
-            if req.return_logprob and (
-                batch.spec_algorithm.is_none() or batch.is_spec_v2
-            ):
+            self._handle_finished_req(req, i, logits_output)
+
+            if req.return_logprob:
                 # Spec v1 handles logprobs inside its own worker.
                 # Normalize: non-spec has 1 token, spec v2 has multiple.
                 if batch.is_spec_v2:
@@ -554,6 +527,34 @@ def process_batch_result_decode(
             num_accepted_tokens=result.num_accepted_tokens,
         )

+    def _handle_finished_req(
+        self: Scheduler, req: Req, i: int, logits_output: LogitsProcessorOutput
+    ):
+        if (
+            self.server_args.disaggregation_decode_enable_offload_kvcache
+            and not req.finished()
+        ):
+            self.decode_offload_manager.offload_kv_cache(req)
+
+        if req.finished():
+            # delete feature to save memory
+            if req.multimodal_inputs is not None and req.session is None:
+                req.multimodal_inputs.release_features()
+            self.maybe_collect_routed_experts(req)
+
+            if self.server_args.disaggregation_decode_enable_offload_kvcache:
+                # Asynchronously offload KV cache; release_kv_cache will be called after Device->Host transfer completes
+                if not self.decode_offload_manager.offload_kv_cache(req):
+                    self.decode_offload_manager.finalize_release_on_finish(req)
+            else:
+                if self.enable_hisparse:
+                    self.hisparse_coordinator.request_finished(req)
+                release_kv_cache(req, self.tree_cache)
+
+            req.time_stats.set_completion_time()
+
+        self.maybe_collect_customized_info(i, req, logits_output)
+
     def _maybe_update_reasoning_tokens(
         self: Scheduler, req: Req, next_token_id: Union[int, List[int]]
     ):
diff --git a/python/sglang/srt/speculative/eagle_info.py b/python/sglang/srt/speculative/eagle_info.py
index dbb91f555ecf..ddb4752994ac 100644
--- a/python/sglang/srt/speculative/eagle_info.py
+++ b/python/sglang/srt/speculative/eagle_info.py
@@ -392,6 +392,7 @@ def verify(
         accept_index_cpu = accept_index.tolist()
         predict_cpu = predict.tolist()
         has_finished = False
+        think_end_id = batch.model_config.think_end_id

         # Iterate every accepted token and check if req has finished after append the token
         # should be checked BEFORE free kv cache slots
@@ -403,6 +404,8 @@ def verify(
                 num_accepted += 1
                 id = predict_cpu[idx]
                 req.output_ids.append(id)
+                if req.require_reasoning and think_end_id is not None:
+                    req.update_reasoning_tokens(id, think_end_id)
                 req.check_finished()
                 if req.finished():
                     has_finished = True
diff --git a/python/sglang/srt/speculative/ngram_info.py b/python/sglang/srt/speculative/ngram_info.py
index 7aafe9870769..bcfad4bae663 100644
--- a/python/sglang/srt/speculative/ngram_info.py
+++ b/python/sglang/srt/speculative/ngram_info.py
@@ -161,6 +161,7 @@ def _fill_requests(
         accept_index_cpu = self.accepted_indices.tolist()
         predict_cpu = self.predict.tolist()
         has_finished = False
+        think_end_id = batch.model_config.think_end_id

         # Iterate every accepted token and check if req has finished after append the token
         # should be checked BEFORE free kv cache slots
@@ -170,6 +171,8 @@ def _fill_requests(
                 break
                 id = predict_cpu[idx]
                 req.output_ids.append(id)
+                if req.require_reasoning and think_end_id is not None:
+                    req.update_reasoning_tokens(id, think_end_id)
                 req.check_finished()
                 if req.finished():
                     has_finished = True

PATCH

echo "Patch applied successfully."
