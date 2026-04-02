#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if return_logprobs already exists in configuration_utils.py
if grep -q 'return_logprobs' src/transformers/generation/configuration_utils.py; then
    echo "Patch already applied."
    exit 0
fi

git apply --ignore-whitespace --whitespace=nowarn - <<'PATCH'
diff --git a/examples/pytorch/continuous_batching.py b/examples/pytorch/continuous_batching.py
index 5df4135adcd5..8731b2a490f4 100644
--- a/examples/pytorch/continuous_batching.py
+++ b/examples/pytorch/continuous_batching.py
@@ -215,15 +215,7 @@ def batch_generate(
 
     # Choose attention implementation
     if args.attn is None:
-        if args.compile:
-            args.attn = "kernels-community/flash-attn3@fake-ops-return-probs"
-            logger.warning(
-                "No attention implementation was provided and compile is enabled. Using experimental kernel: "
-                "kernels-community/flash-attn3@fake-ops-return-probs because compile is not supported on main. Change "
-                "this when main supports it."  # TODO: cf comment
-            )
-        else:
-            args.attn = "kernels-community/flash-attn3"
+        args.attn = "kernels-community/flash-attn3"
 
     # Set seed
     if args.seed is not None:
diff --git a/src/transformers/generation/configuration_utils.py b/src/transformers/generation/configuration_utils.py
index c72c81a4da56..cffbab00c365 100644
--- a/src/transformers/generation/configuration_utils.py
+++ b/src/transformers/generation/configuration_utils.py
@@ -1587,6 +1587,8 @@ class ContinuousBatchingConfig:
             If True, a default compile config will be used for paths that are not explicitly set.
         scheduler (`str`, *optional*, defaults to `"fifo"`):
             Scheduler type to use.
+        return_logprobs (`bool`, *optional*, defaults to `False`):
+            Whether to return log probabilities along with the generated tokens.
         max_queue_size (`int`, *optional*, defaults to 0):
             Maximum request queue size for serving. 0 means unlimited.
     """
@@ -1633,6 +1635,10 @@ class ContinuousBatchingConfig:
     # Scheduler type used
     scheduler: str = "fifo"
 
+    # Whether to generate log probabilities, which is the log of the softmax of the processed logits. If True, the log
+    # probabilities will be returned along with the generated tokens in the generation output.
+    return_logprobs: bool = False
+
     # The parameters below are mostly useful in the context of serving
     max_queue_size: int = 0
 
diff --git a/src/transformers/generation/continuous_batching/continuous_api.py b/src/transformers/generation/continuous_batching/continuous_api.py
index 08be21022d73..cc1a3fff2dd9 100644
--- a/src/transformers/generation/continuous_batching/continuous_api.py
+++ b/src/transformers/generation/continuous_batching/continuous_api.py
@@ -110,7 +110,6 @@ def __init__(
         """
         self.cache = cache
         self.config = config
-        self.generation_config = generation_config
         self.cb_config = continuous_batching_config
         self.input_queue = input_queue
         self.output_queue = output_queue
@@ -119,6 +118,10 @@ def __init__(
         self.model_dtype = model_dtype
         self.scheduler = scheduler
 
+        # Generation-related attributes
+        self.do_sample = getattr(generation_config, "do_sample", True)
+        self.return_logprobs = continuous_batching_config.return_logprobs
+
         # Retrieve the size of the sliding window if there is one
         self.sliding_window = 1 if getattr(config, "sliding_window", None) is None else config.sliding_window
         # Cuda graphs for the generation step
@@ -140,20 +143,17 @@ def __init__(
             is_flash_attn=is_flash_attention_requested(config=config),
             decode_fast_path_available=self.cache.max_blocks_per_request > 0,
         )
+        varlen_config, decode_config = self.cb_config.varlen_compile_config, self.cb_config.decode_compile_config
 
         # Compile the varlen path if config provided
-        varlen_config = self.cb_config.varlen_compile_config
+        self._compiled_varlen = None
         if varlen_config is not None:
             self._compiled_varlen = torch.compile(self._forward_process_and_sample, **varlen_config.to_dict())
-        else:
-            self._compiled_varlen = None
 
         # Compile the decode path if config provided
-        decode_config = self.cb_config.decode_compile_config
+        self._compiled_decode = None
         if decode_config is not None:
             self._compiled_decode = torch.compile(self._forward_process_and_sample, **decode_config.to_dict())
-        else:
-            self._compiled_decode = None
 
         # Padding is turned on when either cuda graphs or compile is used
         self._pad_inputs = self.use_cuda_graph or (varlen_config is not None or decode_config is not None)
@@ -164,11 +164,11 @@ def __init__(
             # Since in async there are 2 IO pairs, there are also 2 graph buffers: we divide the max_cached_graphs by 2
             max_cached_graphs = ceil(self.max_cached_graphs / 2)
             self.inputs_and_outputs = ContinuousBatchingAsyncIOs(
-                cache, config, model_device, model_dtype, max_cached_graphs
+                cache, config, model_device, model_dtype, max_cached_graphs, self.return_logprobs
             )
         else:
             self.inputs_and_outputs = ContinuousBatchingIOs(
-                cache, config, model_device, model_dtype, self.max_cached_graphs
+                cache, config, model_device, model_dtype, self.max_cached_graphs, self.return_logprobs
             )
         # Set up the graph pool. This allows all graphs to share the same memory pool, which is fine because they never
         # run concurrently. This greatly saves memory.
@@ -328,7 +328,7 @@ def _maybe_send_output(self, state: RequestState) -> None:
     @traced
     def update_batch(self) -> None:
         """Update request states based on generated tokens."""
-        requests_in_batch, new_tokens = self.inputs_and_outputs.prepare_batch_update()
+        requests_in_batch, new_tokens, logprobs = self.inputs_and_outputs.prepare_batch_update()
         current_logits_index = 0
         for future_state in requests_in_batch:
             state = future_state.state
@@ -348,10 +348,11 @@ def update_batch(self) -> None:
                     state.status = RequestStatus.DECODING
 
                 token = new_tokens[current_logits_index]
+                logprob = logprobs[current_logits_index] if logprobs is not None else None
                 current_logits_index += 1
 
                 # Update the request and stop if it is complete
-                is_finished = state.update_and_check_completion(token)
+                is_finished = state.update_and_check_completion(token, logprob)
                 # We mark the completed blocks as such
                 self.cache.mark_shareable_blocks_as_complete(state, future_state.complete_blocks)
                 if is_finished:
@@ -425,7 +426,7 @@ def fail_all_requests(self, error: Exception) -> None:
 
     @traced
     @torch.no_grad()
-    def _generation_step(self, model: nn.Module, logit_processor: LogitsProcessorList, do_sample: bool) -> None:
+    def _generation_step(self, model: nn.Module, logit_processor: LogitsProcessorList) -> None:
         """Perform a single generation step."""
 
         # Retrieve the model kwargs with or without padding
@@ -443,7 +444,7 @@ def _generation_step(self, model: nn.Module, logit_processor: LogitsProcessorLis
         if not self.use_cuda_graph:
             maybe_stream = torch.cuda.stream(compute_stream) if compute_stream is not None else nullcontext()
             with maybe_stream:
-                forward_fn(model, batch_data, logit_processor, do_sample, carry_over_ids, prev_output_ids, output_ids)
+                forward_fn(model, batch_data, logit_processor, carry_over_ids, prev_output_ids, output_ids)
 
         # Otherwise, we use create or replay the graph (cuda is available in this path)
         else:
@@ -458,24 +459,17 @@ def _generation_step(self, model: nn.Module, logit_processor: LogitsProcessorLis
                 # compute_stream.wait_stream(torch.cuda.current_stream())
                 # Warmup
                 with torch.cuda.stream(compute_stream):
-                    forward_fn(
-                        model, batch_data, logit_processor, do_sample, carry_over_ids, prev_output_ids, output_ids
-                    )
+                    forward_fn(model, batch_data, logit_processor, carry_over_ids, prev_output_ids, output_ids)
                 # torch.cuda.current_stream().wait_stream(compute_stream)
                 # Capture
                 graph = torch.cuda.CUDAGraph()
-                # Continuous batching can run multiple manager threads concurrently in one process.
-                # PyTorch's default capture mode ("global") errors on CUDA actions from other threads,
-                # which invalidates unrelated captures even when each manager uses a different device.
+                # Continuous batching can run multiple manager threads concurrently in one process, but PyTorch's
+                # default capture mode ("global") errors on CUDA actions from other threads. This means capture can be
+                # invalidated even when each manager uses a different device. To avoid this, we use "thread_local" mode.
                 with torch.cuda.graph(
-                    graph,
-                    stream=compute_stream,
-                    pool=self.graph_pool,
-                    capture_error_mode="thread_local",
+                    graph, stream=compute_stream, pool=self.graph_pool, capture_error_mode="thread_local"
                 ):
-                    forward_fn(
-                        model, batch_data, logit_processor, do_sample, carry_over_ids, prev_output_ids, output_ids
-                    )
+                    forward_fn(model, batch_data, logit_processor, carry_over_ids, prev_output_ids, output_ids)
                 # Store
                 self.inputs_and_outputs.set_graph(graph)
 
@@ -488,7 +482,6 @@ def _forward_process_and_sample(
         model: nn.Module,
         batch_data: dict,
         logit_processor: LogitsProcessorList,
-        do_sample: bool,
         carry_over_ids: torch.Tensor,
         prev_output_ids: torch.Tensor,
         output_ids: torch.Tensor,
@@ -497,9 +490,8 @@ def _forward_process_and_sample(
         function to be easier to trace with OpenTelemetry."""
         self.inputs_and_outputs.carry_over_tokens(batch_data["input_ids"], carry_over_ids, prev_output_ids)
         logits = self._model_forward(model, batch_data)
-        # if self.log_prob_generation:    batch_processor.output_probs.copy_(logits)  # TODO
         probs = self._process_logit(batch_data, logits, logit_processor)
-        self._sample(probs, batch_data, do_sample, output_ids)
+        self._sample(probs, batch_data["logits_indices"], output_ids)
 
     @traced(span_name="model_forward")
     def _model_forward(self, model: nn.Module, batch_data: dict) -> torch.Tensor:
@@ -524,19 +516,40 @@ def _process_logit(
         return processed_logits_2d.view(batch_size, seq_len, vocab_size)
 
     @traced(span_name="sampling")
-    def _sample(self, probs: torch.Tensor, batch_data: dict, do_sample: bool, output_ids: torch.Tensor) -> None:
-        if do_sample:
-            probs = nn.functional.softmax(probs, dim=-1)
-            # probs[0] has shape [seq_len, vocab_size], multinomial returns [seq_len, 1]
-            next_tokens = torch.multinomial(probs[0], num_samples=1).squeeze(-1)  # Now [seq_len]
+    def _sample(self, probs: torch.Tensor, logits_indices: torch.Tensor, output_ids: torch.Tensor) -> None:
+        # Apply softmax if we are sampling or if we are generating log probabilities
+        if self.do_sample or self.return_logprobs:
+            probs = nn.functional.softmax(probs[0], dim=-1)  # shape [seq_len, vocab_size]
+        # Otherwise just remove the batch size dimension, which is always 1
+        else:
+            probs = probs.squeeze(0)  # shape [seq_len, vocab_size]
+
+        # Retrieve next tokens through sampling or argmax
+        if self.do_sample:
+            next_tokens = torch.multinomial(probs, num_samples=1)  # shape [seq_len, 1]
         else:
-            next_tokens = torch.argmax(probs, dim=-1)  # shape is [1, seq_len]
-            next_tokens = next_tokens.squeeze(0)  # shape is [seq_len]
-        tokens = next_tokens.size(0)  # Get seq_len dimension
-        #
-        indices = batch_data["logits_indices"][:tokens]
+            next_tokens = torch.argmax(probs, dim=-1, keepdim=True)  # shape [seq_len, 1]
+
+        # Maybe retrieve log probabilities
+        if self.return_logprobs:
+            per_token_probs = probs.gather(dim=1, index=next_tokens).squeeze(-1)
+            logprobs = per_token_probs.float().log()  # shape [seq_len]
+        # And always remove the extra dimension for the gather
+        next_tokens = next_tokens.squeeze(-1)  # shape [seq_len]
+
+        # Get seq_len dimension to slice the logits indices
+        tokens = next_tokens.size(0)
+        # Shuffle the next tokens to match the order of the batch's requests
+        indices = logits_indices[:tokens]
         next_tokens = next_tokens[indices]
-        output_ids[:tokens].copy_(next_tokens)
+        # Copy the next tokens and maybe their logprobs to the static output tensor
+        output_ids[0, :tokens].copy_(next_tokens)
+        if self.return_logprobs:
+            # Shuffle the logprobs the same way as the next tokens
+            logprobs = logprobs[indices]
+            # In order to match the dtype of output_ids, we cast the fp32 logprobs as int32 without changing the
+            # underlying data. It's just a trick to use the same storage for both tensors.
+            output_ids[1, :tokens].copy_(logprobs.view(dtype=torch.int32))
 
 
 # Manager Class (User Interface)
@@ -583,8 +596,6 @@ def __init__(
         self._request_lock = threading.Lock()
 
         # Generation config related arguments
-        self.log_prob_generation = getattr(generation_config, "log_prob_generation", False)
-        self.do_sample = getattr(generation_config, "do_sample", True)
         self.logit_processor: LogitsProcessorList = self.model._get_logits_processor(generation_config)
         num_return_sequences = getattr(generation_config, "num_return_sequences", None)
         self.num_return_sequences = num_return_sequences if num_return_sequences is not None else 1
@@ -605,10 +616,6 @@ def __init__(
         self.kv_padding_interval_size = self.continuous_batching_config.kv_padding_interval_size
         self.max_cached_graphs = self.continuous_batching_config.max_cached_graphs
 
-        # Log probability generation is not supported yet (TODO)
-        if self.log_prob_generation:
-            raise NotImplementedError("log_prob_generation is not supported yet")
-
     @traced
     def start(self) -> None:
         """Start the background generation thread."""
@@ -791,7 +798,7 @@ def _generation_step(self) -> None:
         """Perform a single generation step. This is mostly cuda graphed"""
         if self.batch_processor is None:
             raise RuntimeError("Tried to perform a generation step before the batch processor was initialized.")
-        self.batch_processor._generation_step(self.model, self.logit_processor, self.do_sample)
+        self.batch_processor._generation_step(self.model, self.logit_processor)
 
     def _run_generation_loop(self) -> None:
         """Main processing loop running in the background thread."""
diff --git a/src/transformers/generation/continuous_batching/input_outputs.py b/src/transformers/generation/continuous_batching/input_outputs.py
index b04caa1ae477..52a0872b1500 100644
--- a/src/transformers/generation/continuous_batching/input_outputs.py
+++ b/src/transformers/generation/continuous_batching/input_outputs.py
@@ -95,7 +95,8 @@ def __init__(
         config: PretrainedConfig,
         device: torch.device,
         model_dtype: torch.dtype,
-        max_graphs: int = 32,
+        max_graphs: int,
+        return_logprobs: bool,
     ) -> None:
         """Initialize the continuous batching I/O manager. Args:
         - cache: The [`PagedAttentionCache`] instance managing the KV cache. Meant to be unique.
@@ -103,6 +104,7 @@ def __init__(
         - device: The device to allocate tensors on. If the device is CPU, then the memory is pinned.
         - model_dtype: The data type for model computations.
         - max_graphs: Maximum number of CUDA graphs to cache. Uses LRU eviction when full.
+        - return_logprobs: Whether to return log probabilities along with the token IDs.
         """
         # Memoize attributes
         self.cache = cache
@@ -110,6 +112,7 @@ def __init__(
         self.config = config
         self.model_dtype = model_dtype
         self.sliding_window = 1 if getattr(config, "sliding_window", None) is None else config.sliding_window
+        self.return_logprobs = return_logprobs
         # Setup input-related accumulators
         self.num_q_tokens = 0  # number of query tokens in the batch. Can be padded.
         self.max_kv_read = 0  # number of KV tokens read from cache (maxed across all groups). Can be padded.
@@ -136,7 +139,7 @@ def _setup_static_tensors(self) -> None:
           `logits_indices`, `cumulative_seqlens_k`, `carry_over_ids`.
         - `attention_mask`: Optional attention masks (only for eager/SDPA implementations)
         - `write_index` and `read_index` storage: Cache indexing tensors for each attention group
-        - `output_ids`: Storage for generated token IDs
+        - `output_ids`: Storage for generated token IDs and maybe log probabilities if return_logprobs is True
         """
         num_groups = self.cache.num_groups
         max_batch_tokens = self.cache.max_batch_tokens
@@ -167,8 +170,9 @@ def _setup_static_tensors(self) -> None:
             self.cumulative_seqlens_k["sliding_attention"] = sliding_attention_cumulative_seqlens_k
 
         # Output tensor and scalars
+        num_output_rows = 2 if self.return_logprobs else 1
         self.output_ids = torch.empty(
-            (max_batch_tokens + 1,), dtype=torch.int32, device=self.device, pin_memory=pin_memory
+            (num_output_rows, max_batch_tokens + 1), dtype=torch.int32, device=self.device, pin_memory=pin_memory
         )
         # Last output token is never changed and set to 0 for async carry on purpose
         self.output_ids.zero_()
@@ -254,7 +258,7 @@ def _reset_static_tensors(self, full_reset: bool = False) -> None:
 
         # Reset the logits indices and output ids
         self.logits_indices[:q_len].zero_()
-        self.output_ids[:q_len].zero_()
+        self.output_ids[:, :q_len].zero_()
 
         # Reset the attributes that are either tensors or dict of tensors
         for layer_type in self.cumulative_seqlens_k:
@@ -291,10 +295,16 @@ def retrieve_device_outputs(self) -> None:
         if self.compute_stream is not None:
             self.compute_stream.synchronize()
 
-    def prepare_batch_update(self) -> tuple[list[FutureRequestState], list[int]]:
+    def prepare_batch_update(self) -> tuple[list[FutureRequestState], list[int], list[float] | None]:
         requests_in_batch = self.requests_in_batch
-        new_tokens = self.output_ids[: len(self.requests_in_batch)].tolist()
-        return requests_in_batch, new_tokens
+        new_tokens = self.output_ids[0, : len(self.requests_in_batch)].tolist()
+        # If logprobs are generated, we retrieve them from the output tensor and cast them to the right dtype
+        if self.return_logprobs:
+            logprobs = self.output_ids[1, : len(self.requests_in_batch)].view(dtype=torch.float32).tolist()
+        # Otherwise, we can return an empty list because they wont be used
+        else:
+            logprobs = None
+        return requests_in_batch, new_tokens, logprobs
 
     @traced
     def prepare_batch_tensors(
@@ -507,11 +517,14 @@ def __init__(
         config: PretrainedConfig,
         device: torch.device,
         model_dtype: torch.dtype,
-        max_graphs: int = 32,
+        max_graphs: int,
+        return_logprobs: bool,
     ) -> None:
         # The host IO has automatic pinned memory because it is created on the CPU
-        self.host_io = ContinuousBatchingIOs(cache, config, torch.device("cpu"), model_dtype, max_graphs)
-        self.device_io = ContinuousBatchingIOs(cache, config, device, model_dtype, max_graphs)
+        self.host_io = ContinuousBatchingIOs(
+            cache, config, torch.device("cpu"), model_dtype, max_graphs, return_logprobs
+        )
+        self.device_io = ContinuousBatchingIOs(cache, config, device, model_dtype, max_graphs, return_logprobs)
         # Create events only on CUDA devices
         self.h2d_over = torch.cuda.Event() if torch.cuda.is_available() else None
         self.compute_over = torch.cuda.Event() if torch.cuda.is_available() else None
@@ -578,14 +591,17 @@ def __init__(
         config: PretrainedConfig,
         device: torch.device,
         model_dtype: torch.dtype,
-        max_graphs: int = 32,
+        max_graphs: int,
+        return_logprobs: bool,
     ) -> None:
         # Async batching needs streams to function, so check is CUDA is available
         if not torch.cuda.is_available():
             raise RuntimeError(f"Async batching requires CUDA, but {torch.cuda.is_available() = }")
         # IO pairs used to avoid race conditions
         self.current_pair = 0
-        self.io_pairs = [HostDeviceIOPair(cache, config, device, model_dtype, max_graphs) for _ in range(2)]
+        self.io_pairs = [
+            HostDeviceIOPair(cache, config, device, model_dtype, max_graphs, return_logprobs) for _ in range(2)
+        ]
         # CUDA streams
         self.h2d_stream = torch.cuda.Stream(device=device)
         self.d2h_stream = torch.cuda.Stream(device=device)
@@ -664,7 +680,7 @@ def carry_over_tokens(
         before launching the forwar pass of batch N+1. This method performs the carry over, and is recorded in CUDA
         graphs if they are enabled."""
         # Compute tokens to carry over and the corresponding mask
-        carried_over_ids = prev_output_ids[carry_over_ids]
+        carried_over_ids = prev_output_ids[0, carry_over_ids]
         carried_over_mask = (carry_over_ids != -1).int()
         # Truncate everything to the right size
         carried_over_ids = carried_over_ids[: input_ids.size(1)]
@@ -701,7 +717,7 @@ def retrieve_device_outputs(self) -> None:
         self.current_pair = 1 - self.current_pair
 
     # This method is called after the switch and not during the first batch
-    def prepare_batch_update(self) -> tuple[list[FutureRequestState], list[int]]:
+    def prepare_batch_update(self) -> tuple[list[FutureRequestState], list[int], list[float] | None]:
         io_pair = self.io_pairs[self.current_pair]
         io_pair.d2h_over.synchronize()  # ty:ignore[unresolved-attribute]  <- this is always a CUDA event
         return io_pair.host_io.prepare_batch_update()
diff --git a/src/transformers/generation/continuous_batching/requests.py b/src/transformers/generation/continuous_batching/requests.py
index 60e4c63fe077..c1ee43a93cd2 100644
--- a/src/transformers/generation/continuous_batching/requests.py
+++ b/src/transformers/generation/continuous_batching/requests.py
@@ -153,6 +153,7 @@ class RequestState:
         default_factory=list
     )  # Initial tokens left to process (initialized in __post_init__)
     generated_tokens: list[int] = field(default_factory=list)  # Generated tokens
+    logprobs: list[float] = field(default_factory=list)  # Log probabilities of the generated tokens
     allocated_blocks: int = 0  # Number of blocks allocated to the request
     position_offset: int = 0  # Current position in the sequence for position_ids
     _status: RequestStatus = RequestStatus.PENDING  # Status of the request, hidden behind a property
@@ -222,15 +223,9 @@ def generated_len(self) -> int:
 
     # TODO: this logic seems one token off, check it out
     @traced
-    def update_and_check_completion(self, token_id: int) -> bool:
-        """Update the request with a newly generated token and check for completion.
-
-        Args:
-            token_id: The token ID to add to the output sequence
-
-        Returns:
-            bool: True if the request is now complete, False otherwise
-        """
+    def update_and_check_completion(self, token_id: int, logprob: float | None) -> bool:
+        """Update the request with a newly generated token (and optional log probability of the token) and check for
+        completion. Returns True if the request is now complete, False otherwise."""
         # Only update if we're in decoding state # TODO: seems useless (always true) -- remove this
         if self.status != RequestStatus.DECODING:
             return False
@@ -249,9 +244,10 @@ def update_and_check_completion(self, token_id: int) -> bool:
             self.generated_tokens.append(token_id)
             self.tokens_to_process = [token_id]  # this works for 2 levels of pipelines, but not sure for more
             current_len += 1
+            if logprob is not None:
+                self.logprobs.append(logprob)
         else:
             logger.warning(f"Request {self.request_id} generated a useless token: {token_id}")
-            self.generated_tokens.pop()
 
         if is_eos or current_len >= self._new_tokens_limit:
             self.status = RequestStatus.FINISHED
@@ -281,7 +277,7 @@ def to_generation_output(self):
             request_id=self.request_id,
             prompt_ids=self.initial_tokens,
             generated_tokens=self.generated_tokens,
-            logprobs=[],
+            logprobs=self.logprobs,
             error=self.error,
             status=self.status,
             created_time=self.created_time,
@@ -298,6 +294,7 @@ def fork(self, new_request_id: str) -> "RequestState":
             num_children=self.num_children,
             tokens_to_process=self.tokens_to_process[:],
             generated_tokens=self.generated_tokens[:],
+            logprobs=self.logprobs[:],
             allocated_blocks=self.allocated_blocks,
             position_offset=self.position_offset,
             _status=self.status,
@@ -317,18 +314,24 @@ def fork(self, new_request_id: str) -> "RequestState":
     def create_equivalent_initial_request(self) -> "RequestState":
         """Creates an equivalent new request by removing the generated tokens and adding them to the initial prompt. The
         created request has THE SAME request_id. Notably, we can retrieve the original request from the created one with
-        the _true_initial_tokens attribute."""
+        the _true_initial_tokens attribute. The logprobs of the generated tokens are kept in the new request."""
         max_new_tokens = None if self.max_new_tokens is None else (self.max_new_tokens - len(self.generated_tokens))
         new_state = RequestState(
             request_id=self.request_id,
             initial_tokens=self.initial_tokens + self.generated_tokens,
+            logprobs=self.logprobs[:],
             num_children=self.num_children,
             record_timestamps=self.record_timestamps,
             max_new_tokens=max_new_tokens,
             eos_token_id=self.eos_token_id,
             streaming=self.streaming,
         )
-        new_state._true_initial_tokens = self._true_initial_tokens + len(self.initial_tokens)
+        # If the request has been soft reset once already, this stays the same
+        if self._true_initial_tokens:
+            new_state._true_initial_tokens = self._true_initial_tokens
+        # Otherwise, we set the true initial tokens to the number of initial tokens
+        else:
+            new_state._true_initial_tokens = len(self.initial_tokens)
         return new_state
 
 
diff --git a/tests/generation/test_continuous_batching.py b/tests/generation/test_continuous_batching.py
index fd745076ba2b..eb7bd99c5775 100644
--- a/tests/generation/test_continuous_batching.py
+++ b/tests/generation/test_continuous_batching.py
@@ -626,6 +626,86 @@ def test_continuous_batching_long_generate(self) -> None:
             max_new_tokens=80,
         )
 
+    @parameterized.expand([(False, False), (False, True), (True, False), (True, True)])
+    @slow
+    def test_continuous_batching_log_probs(self, use_cuda_graph: bool, use_async_batching: bool) -> None:
+        """Test that log probabilities match between continuous batching and regular generate."""
+        model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
+        max_new_tokens = 10
+
+        tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left")
+        tokenizer.pad_token = tokenizer.eos_token
+        user_messages = ["What is 2+2?", "Hello world"]
+        chats = [[{"role": "user", "content": msg}] for msg in user_messages]
+        tokenized = [tokenizer.apply_chat_template(chat, add_generation_prompt=True) for chat in chats]
+        input_ids = [(x if isinstance(x, list) else x["input_ids"]) for x in tokenized]
+
+        # Load model for CB generation
+        model = AutoModelForCausalLM.from_pretrained(model_id, attn_implementation="sdpa", torch_dtype=torch.float32)
+        model = model.to(torch_device).eval()
+        eos_token_id = model.config.eos_token_id
+
+        gen_config = GenerationConfig(max_new_tokens=max_new_tokens, do_sample=False, eos_token_id=eos_token_id)
+
+        continuous_batching_config = ContinuousBatchingConfig(
+            use_cuda_graph=use_cuda_graph,
+            use_async_batching=use_async_batching,
+            allow_block_sharing=False,
+            return_logprobs=True,
+        )
+
+        cb_outputs = model.generate_batch(
+            inputs=input_ids, generation_config=gen_config, continuous_batching_config=continuous_batching_config
+        )
+
+        # Load fresh model for regular generate (same pattern as parity tests)
+        model = AutoModelForCausalLM.from_pretrained(model_id, attn_implementation="sdpa", torch_dtype=torch.float32)
+        model = model.to(torch_device).eval()
+
+        # Run regular generate with output_scores to get logits
+        inputs = tokenizer.apply_chat_template(
+            chats, add_generation_prompt=True, return_tensors="pt", padding=True, return_dict=True
+        )
+        gen_config_regular = GenerationConfig(
+            max_new_tokens=max_new_tokens, do_sample=False, output_scores=True, eos_token_id=eos_token_id
+        )
+        generate_outputs = model.generate(
+            **inputs.to(torch_device), generation_config=gen_config_regular, return_dict_in_generate=True
+        )
+
+        # Compare log_probs for each request, matching by prompt_ids
+        num_input_tokens = inputs.input_ids.shape[1]
+        for i in range(len(user_messages)):
+            # Find the corresponding CB output by matching prompt tokens
+            input_tokens = inputs.input_ids[i][inputs.attention_mask[i] == 1].tolist()
+            cb_output = None
+            for state in cb_outputs.values():
+                if state.prompt_ids == input_tokens:
+                    cb_output = state
+                    break
+            self.assertIsNotNone(cb_output, f"Could not find CB output for request {i}")
+
+            # Compute log_probs from regular generate scores
+            expected_logprobs = []
+            generated_tokens = generate_outputs.sequences[i, num_input_tokens:].tolist()
+            for score, token in zip(generate_outputs.scores, generated_tokens):
+                probs = torch.nn.functional.softmax(score[i], dim=-1)
+                expected_logprobs.append(probs[token].log().item())
+
+            # Truncate to same length (in case of padding differences)
+            min_len = min(len(cb_output.logprobs), len(expected_logprobs))
+            cb_logprobs = cb_output.logprobs[:min_len]
+            expected_logprobs = expected_logprobs[:min_len]
+
+            # Compare with tolerance for floating point differences
+            for j, (cb_lp, exp_lp) in enumerate(zip(cb_logprobs, expected_logprobs)):
+                self.assertAlmostEqual(
+                    cb_lp,
+                    exp_lp,
+                    places=4 if use_cuda_graph else 5,  # cuda graphs add padding, hence lower precision
+                    msg=f"logprob mismatch at position {j} for request {i}: CB={cb_lp}, expected={exp_lp}",
+                )
+
     def test_continuous_batching_with_default_compile_configs(self) -> None:
         """Test continuous batching with use_default_compile_configs=True in ContinuousBatchingConfig.
 
PATCH

echo "Patch applied successfully."
