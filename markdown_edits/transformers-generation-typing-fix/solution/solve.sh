#!/bin/bash
set -e

cd /workspace/transformers

# Check if already applied
if grep -q "type checker" AGENTS.md 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

cat > /tmp/gold.patch << 'GOLDENDOFPATCH'
diff --git a/AGENTS.md b/AGENTS.md
index c7444840fc43..5b3eb6d5cdf 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -1,5 +1,5 @@
 ## Useful commands
-- `make style`: runs formatters and linters, necessary to pass code style checks
+- `make style`: runs formatters, linters and type checker, necessary to pass code style checks
 - `make fix-repo`: auto-fixes copies, modular conversions, doc TOCs, docstrings in addition to the `make style` fixes
 - `make check-repo` — CI-style consistency checks
 - Many tests are marked as 'slow' and skipped by default in the CI. To run them, use: `RUN_SLOW=1 pytest ...`

diff --git a/Makefile b/Makefile
index ba78e2a4d461..7df51963cf 100644
--- a/Makefile
+++ b/Makefile
@@ -6,10 +6,8 @@ export PYTHONPATH = src
 check_dirs := examples tests src utils scripts benchmark benchmark_v2
 exclude_folders :=  ""

-# Helper to find all Python files in directories (ty doesn't recursively scan directories)
-define get_py_files
-$(shell find $(1) -name "*.py" -type f 2>/dev/null)
-endef
+# Directories to type-check with ty
+ty_check_dirs := src/transformers/utils src/transformers/generation


 # this runs all linting/formatting scripts, most notably ruff
@@ -18,14 +16,14 @@ style:
 	ruff format $(check_dirs) setup.py conftest.py --exclude $(exclude_folders)
 	python utils/custom_init_isort.py
 	python utils/sort_auto_mappings.py
-
+	python utils/check_types.py $(ty_check_dirs)

 # Check that the repo is in a good state (both style and consistency CI checks)
 # Note: each line is run in its own shell, and doing `-` before the command ignores the errors if any, continuing with next command
 check-repo:
 	ruff check $(check_dirs) setup.py conftest.py
 	ruff format --check $(check_dirs) setup.py conftest.py
-	ty check $(call get_py_files,src/transformers/utils) --force-exclude --exclude '**/*_pb2*.py'
+	python utils/check_types.py $(ty_check_dirs)
 	-python utils/custom_init_isort.py --check_only
 	-python utils/sort_auto_mappings.py --check_only
 	-python -c "from transformers import *" || (echo '🚨 import failed, this means you introduced unprotected imports! 🚨'; exit 1)

diff --git a/src/transformers/utils/_typing.py b/src/transformers/_typing.py
similarity index 71%
rename from src/transformers/utils/_typing.py
rename to src/transformers/_typing.py
index c98703340ee1..68380d6bfb71 100644
--- a/src/transformers/utils/_typing.py
+++ b/src/transformers/_typing.py
@@ -1,4 +1,4 @@
-# Copyright 2025 The HuggingFace Inc. team.
+# Copyright 2026 The HuggingFace Inc. team.
 #
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
@@ -11,11 +11,19 @@
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
+"""Typing helpers shared across the Transformers library."""
+
 from __future__ import annotations

 import logging
 from collections.abc import Mapping, MutableMapping
-from typing import Any, Protocol, TypeAlias
+from typing import TYPE_CHECKING, Any, Protocol, TypeAlias
+
+
+if TYPE_CHECKING:
+    import torch
+
+    from .cache_utils import Cache


 # A few helpful type aliases
@@ -121,3 +129,44 @@ def debugStack(self, msg: object, *args: object, **kwargs: object) -> None: ...
     def warning_advice(self, msg: object, *args: object, **kwargs: object) -> None: ...
     def warning_once(self, msg: object, *args: object, **kwargs: object) -> None: ...
     def info_once(self, msg: object, *args: object, **kwargs: object) -> None: ...
+
+
+class GenerativePreTrainedModel(Protocol):
+    """Protocol for the model interface that GenerationMixin expects.
+
+    GenerationMixin is designed to be mixed into PreTrainedModel subclasses. This Protocol documents the
+    attributes and methods the mixin relies on from its host class. It is *not* used at runtime — its
+    purpose is to help the ``ty`` type checker resolve ``self.<attr>`` accesses inside the mixin.
+    """
+
+    config: Any  # PretrainedConfig — kept as Any to avoid circular imports
+    device: torch.device
+    dtype: torch.dtype
+    main_input_name: str
+    base_model_prefix: str
+    _is_stateful: bool
+    hf_quantizer: Any
+    encoder: Any
+    hf_device_map: dict[str, Any]
+    _cache: Cache
+
+    generation_config: Any  # GenerationConfig
+
+    def __getattr__(self, name: str) -> Any: ...
+    def forward(self, *args: Any, **kwargs: Any) -> Any: ...
+    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
+    def can_generate(self) -> bool: ...
+    def get_encoder(self) -> Any: ...
+    def get_output_embeddings(self) -> Any: ...
+    def get_input_embeddings(self) -> Any: ...
+    def set_output_embeddings(self, value: Any) -> None: ...
+    def set_input_embeddings(self, value: Any) -> None: ...
+    def get_compiled_call(self, compile_config: Any) -> Any: ...
+    def set_experts_implementation(self, *args: Any, **kwargs: Any) -> Any: ...
+    def _supports_logits_to_keep(self) -> bool: ...
+
+
+class WhisperGenerationConfigLike(Protocol):
+    """Protocol for Whisper-specific generation config fields accessed in generation internals."""
+
+    no_timestamps_token_id: int

diff --git a/src/transformers/generation/candidate_generator.py b/src/transformers/generation/candidate_generator.py
index c2ee95ea110e..51612dddb2cc 100644
--- a/src/transformers/generation/candidate_generator.py
+++ b/src/transformers/generation/candidate_generator.py
@@ -14,7 +14,7 @@

 import copy
 import weakref
-from typing import TYPE_CHECKING, Any, Optional
+from typing import TYPE_CHECKING, Any, Optional, cast

 import numpy as np
 import torch
@@ -387,7 +387,7 @@ def __init__(
         self.target_tokenizer = target_tokenizer
         self.assistant_tokenizer = assistant_tokenizer
         self.prev_target_ids_len: int | None = None
-        self.prev_assistant_ids = None
+        self.prev_assistant_ids: torch.LongTensor | None = None
         self.target_lookbehind = self.assistant_generation_config.target_lookbehind
         self.assistant_lookbehind = self.assistant_generation_config.assistant_lookbehind

@@ -591,7 +591,8 @@ def _process_assistant_outputs(
         self, input_ids: torch.LongTensor, assistant_sequences: torch.LongTensor
     ) -> torch.LongTensor:
         """Processes assistant outputs to obtain target input IDs."""
-        num_prev_assistant = self.prev_assistant_ids.shape[1]
+        prev_assistant_ids = cast(torch.LongTensor, self.prev_assistant_ids)
+        num_prev_assistant = prev_assistant_ids.shape[1]
         start_assistant_look_index = num_prev_assistant - self.assistant_lookbehind

         new_target_ids_from_window = self.convert_source_tokens_to_target_tokens(
@@ -721,7 +722,7 @@ def __init__(
         self.assistant_prune_lm_head = assistant_prune_lm_head and assistant_model is not None
         if len(self._suppress_input_ids) > 0:
             # the assistant vocab is not a subset of the target vocab
-            if self.assistant_prune_lm_head:
+            if self.assistant_prune_lm_head and assistant_model is not None:
                 self.assistant_overlap_token_ids = torch.tensor(
                     list(self.target_to_assistant_input_ids.values()),
                     dtype=torch.long,
@@ -1138,7 +1139,7 @@ def get_candidates(self, input_ids: torch.LongTensor) -> tuple[torch.LongTensor,
                 break

         # In case we didn't find a match return the input sequence unchanged, reverts back to autoregressive decoding
-        if not match_found or len(chosen_ids) == 0:
+        if not match_found or chosen_ids is None or len(chosen_ids) == 0:
             return input_ids, None

         # Now need extend input_ids with chosen_ids

diff --git a/src/transformers/generation/configuration_utils.py b/src/transformers/generation/configuration_utils.py
index 1e3b49247eca..a6e1089c1270 100644
--- a/src/transformers/generation/configuration_utils.py
+++ b/src/transformers/generation/configuration_utils.py
@@ -36,6 +36,8 @@


 if TYPE_CHECKING:
+    import torch
+
     from ..configuration_utils import PreTrainedConfig
     from ..modeling_utils import PreTrainedModel

@@ -338,6 +340,15 @@ class GenerationConfig(PushToHubMixin):

     extra_output_flags = ("output_attentions", "output_hidden_states", "output_scores", "output_logits")

+    # Tensor versions of token IDs, set by _prepare_special_tokens() at generation time
+    _bos_token_tensor: "torch.Tensor | None"
+    _eos_token_tensor: "torch.Tensor | None"
+    _pad_token_tensor: "torch.Tensor | None"
+    _decoder_start_token_tensor: "torch.Tensor | None"
+
+    # Hash to detect whether the instance was modified after loading
+    _original_object_hash: int | None
+
     def __init__(self, **kwargs):
         # Parameters that control the length of the output
         self.max_length = kwargs.pop("max_length", None)
@@ -793,7 +804,7 @@ def save_pretrained(

         if push_to_hub:
             commit_message = kwargs.pop("commit_message", None)
-            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
+            repo_id = kwargs.pop("repo_id", str(save_directory).split(os.path.sep)[-1])
             repo_id = create_repo(repo_id, exist_ok=True, **kwargs).repo_id
             files_timestamps = self._get_files_timestamps(save_directory)

diff --git a/src/transformers/generation/logits_process.py b/src/transformers/generation/logits_process.py
index 067e006be4d3..523e71aea3fd 100644
--- a/src/transformers/generation/logits_process.py
+++ b/src/transformers/generation/logits_process.py
@@ -15,11 +15,12 @@
 import inspect
 import math
 from collections.abc import Callable, Iterable
-from typing import TYPE_CHECKING
+from typing import TYPE_CHECKING, Any, cast

 import numpy as np
 import torch

+from .._typing import WhisperGenerationConfigLike
 from ..utils import add_start_docstrings
 from ..utils.logging import get_logger

@@ -1269,7 +1270,8 @@ class SequenceBiasLogitsProcessor(LogitsProcessor):
     """

     def __init__(self, sequence_bias: list[list[list[int] | float]]):
-        self.sequence_bias = sequence_bias
+        # After _convert_list_arguments_into_dict(), becomes dict[tuple[int, ...], float]
+        self.sequence_bias: Any = sequence_bias
         self._validate_arguments()
         self._convert_list_arguments_into_dict()

@@ -1964,8 +1966,9 @@ def __init__(
         begin_index: int,
         _detect_timestamp_from_logprob: bool | None = None,
     ):  # support for the kwargs
-        self.no_timestamps_token_id = generate_config.no_timestamps_token_id
-        self.timestamp_begin = generate_config.no_timestamps_token_id + 1
+        whisper_generate_config = cast(WhisperGenerationConfigLike, generate_config)
+        self.no_timestamps_token_id = whisper_generate_config.no_timestamps_token_id
+        self.timestamp_begin = whisper_generate_config.no_timestamps_token_id + 1
         self.eos_token_id = generate_config.eos_token_id or generate_config.bos_token_id

         # this variable is mostly just used for testing
@@ -2057,9 +2060,9 @@ def __init__(self, no_speech_token: int, begin_index: int, scores_is_logprobs: b
         self._no_speech_prob = [0.0]
         self.is_scores_logprobs = scores_is_logprobs

-        # overwritten dynamically
-        self.model = None
-        self.inputs = None
+        # overwritten dynamically via set_model()
+        self.model: Any = None
+        self.inputs: dict[str, Any] | None = None

     def set_model(self, model):
         self.model = model

diff --git a/src/transformers/generation/stopping_criteria.py b/src/transformers/generation/stopping_criteria.py
index 08fa9e7445d7..b57136f53416 100644
--- a/src/transformers/generation/stopping_criteria.py
+++ b/src/transformers/generation/stopping_criteria.py
@@ -335,7 +335,7 @@ def _stop_string_get_matching_positions(
         return token_valid_positions, token_end_overlaps

     @staticmethod
-    def _stop_string_create_embedding_vec(token_list, token_indices, stop_strings) -> dict[str, torch.tensor]:
+    def _stop_string_create_embedding_vec(token_list, token_indices, stop_strings) -> dict[str, torch.Tensor]:
         """This function precomputes everything needed for the run-time checks in StopStringCriteria, and packs
         them into an embedding tensor that can be accessed with pure tensor operations. For the specifics of the values
         that are precomputed and what they are used for, please refer to the StopStringCriteria docstring!"""

diff --git a/src/transformers/generation/streamers.py b/src/transformers/generation/streamers.py
index cc9f709f5116..e52dee60600e 100644
--- a/src/transformers/generation/streamers.py
+++ b/src/transformers/generation/streamers.py
@@ -15,12 +15,13 @@
 from __future__ import annotations

 import asyncio
+import sys
 from queue import Queue
-from typing import TYPE_CHECKING
+from typing import TYPE_CHECKING, Any, cast


 if TYPE_CHECKING:
-    from ..models.auto import AutoTokenizer
+    from ..tokenization_utils_base import PreTrainedTokenizerBase


 class BaseStreamer:
@@ -71,13 +72,13 @@ class TextStreamer(BaseStreamer):
         ```
     """

-    def __init__(self, tokenizer: AutoTokenizer, skip_prompt: bool = False, **decode_kwargs):
+    def __init__(self, tokenizer: PreTrainedTokenizerBase, skip_prompt: bool = False, **decode_kwargs: Any):
         self.tokenizer = tokenizer
         self.skip_prompt = skip_prompt
         self.decode_kwargs = decode_kwargs

         # variables used in the streaming process
-        self.token_cache = []
+        self.token_cache: list[int] = []
         self.print_len = 0
         self.next_tokens_are_prompt = True

@@ -96,7 +97,7 @@ def put(self, value):

         # Add the new token to the cache and decodes the entire thing.
         self.token_cache.extend(value.tolist())
-        text = self.tokenizer.decode(self.token_cache, **self.decode_kwargs)
+        text = cast(str, self.tokenizer.decode(self.token_cache, **self.decode_kwargs))

         # After the symbol for a new line, we flush the cache.
         if text.endswith("\n"):
@@ -119,7 +120,7 @@ def end(self):
         """Flushes any remaining cache and prints a newline to stdout."""
         # Flush the cache, if it exists
         if len(self.token_cache) > 0:
-            text = self.tokenizer.decode(self.token_cache, **self.decode_kwargs)
+            text = cast(str, self.tokenizer.decode(self.token_cache, **self.decode_kwargs))
             printable_text = text[self.print_len :]
             self.token_cache = []
             self.print_len = 0
@@ -205,7 +206,11 @@ class TextIteratorStreamer(TextStreamer):
     """

     def __init__(
-        self, tokenizer: AutoTokenizer, skip_prompt: bool = False, timeout: float | None = None, **decode_kwargs
+        self,
+        tokenizer: PreTrainedTokenizerBase,
+        skip_prompt: bool = False,
+        timeout: float | None = None,
+        **decode_kwargs: Any,
     ):
         super().__init__(tokenizer, skip_prompt, **decode_kwargs)
         self.text_queue = Queue()
@@ -283,14 +288,20 @@ class AsyncTextIteratorStreamer(TextStreamer):
     """

     def __init__(
-        self, tokenizer: AutoTokenizer, skip_prompt: bool = False, timeout: float | None = None, **decode_kwargs
+        self,
+        tokenizer: PreTrainedTokenizerBase,
+        skip_prompt: bool = False,
+        timeout: float | None = None,
+        **decode_kwargs: Any,
     ):
         super().__init__(tokenizer, skip_prompt, **decode_kwargs)
         self.text_queue = asyncio.Queue()
         self.stop_signal = None
         self.timeout = timeout
         self.loop = asyncio.get_running_loop()
-        self.has_asyncio_timeout = hasattr(asyncio, "timeout")
+        timeout_context = getattr(asyncio, "timeout", None)
+        self.has_asyncio_timeout = sys.version_info >= (3, 11) and callable(timeout_context)
+        self.asyncio_timeout = timeout_context if self.has_asyncio_timeout else None

     def on_finalized_text(self, text: str, stream_end: bool = False):
         """Put the new text in the queue. If the stream is ending, also put a stop signal in the queue."""
@@ -303,8 +314,8 @@ def __aiter__(self):

     async def __anext__(self):
         try:
-            if self.has_asyncio_timeout:
-                async with asyncio.timeout(self.timeout):
+            if self.has_asyncio_timeout and self.asyncio_timeout is not None:
+                async with self.asyncio_timeout(self.timeout):
                     value = await self.text_queue.get()
             else:
                 value = await asyncio.wait_for(self.text_queue.get(), timeout=self.timeout)

diff --git a/src/transformers/generation/utils.py b/src/transformers/generation/utils.py
index b6c900df1961..0955f3ee5ab4 100644
--- a/src/transformers/generation/utils.py
+++ b/src/transformers/generation/utils.py
@@ -20,7 +20,7 @@
 from collections.abc import Callable
 from contextlib import contextmanager
 from dataclasses import dataclass
-from typing import TYPE_CHECKING, Any, Optional
+from typing import TYPE_CHECKING, Any, Optional, cast

 import torch
 import torch.distributed as dist
@@ -110,6 +110,7 @@


 if TYPE_CHECKING:
+    from .._typing import GenerativePreTrainedModel
     from ..modeling_utils import PreTrainedModel
     from ..tokenization_utils_base import PreTrainedTokenizerBase
     from .streamers import BaseStreamer
@@ -367,7 +368,7 @@ class GenerationMixin(ContinuousMixin):
     output_modalities = ("text",)

     def adjust_generation_fn(
-        self,
+        self: "GenerativePreTrainedModel",
         generation_config,
         from_auto_class,
         from_pipeline,
@@ -491,7 +492,7 @@ def load_custom_generate(
         return custom_generate_function

     def prepare_inputs_for_generation(
-        self,
+        self: "GenerativePreTrainedModel",
         input_ids: torch.LongTensor,
         next_sequence_length: int | None = None,
         past_key_values: Cache | None = None,
@@ -517,11 +518,11 @@ def prepare_inputs_for_generation(
         # if `inputs_embeds` are passed, we only want to use them in the 1st generation step for every prompt.
         if not self.config.is_encoder_decoder and inputs_embeds is not None and is_first_iteration:
             model_inputs[input_ids_key] = None
-            inputs_embeds = (
+            prompt_embeds = (
                 inputs_embeds[:, -next_sequence_length:, :] if next_sequence_length is not None else inputs_embeds
             )
-            model_inputs["inputs_embeds"] = inputs_embeds.clone(memory_format=torch.contiguous_format)
-            batch_size, sequence_length = inputs_embeds.shape[:2]
+            model_inputs["inputs_embeds"] = prompt_embeds.clone(memory_format=torch.contiguous_format)
+            batch_size, sequence_length = prompt_embeds.shape[:2]
         else:
             # `clone` calls in this function ensure a consistent stride. See #32227
             input_ids = input_ids[:, -next_sequence_length:] if next_sequence_length is not None else input_ids
@@ -591,10 +592,10 @@ def prepare_inputs_for_generation(
         return model_inputs

     def _prepare_model_inputs(
-        self,
-        inputs: torch.Tensor | None = None,
-        bos_token_id: torch.Tensor | None = None,
-        model_kwargs: dict[str, torch.Tensor] | None = None,
+        self: "GenerativePreTrainedModel",
+        inputs: torch.Tensor | None,
+        bos_token_id: torch.Tensor | None,
+        model_kwargs: dict[str, torch.Tensor],
     ) -> tuple[torch.Tensor, str | None, dict[str, torch.Tensor]]:
         """
         This function extracts the model-specific `inputs` for generation.
@@ -656,19 +657,20 @@ def _prepare_model_inputs(
         return inputs, input_name, model_kwargs

     def _maybe_initialize_input_ids_for_generation(
-        self,
-        inputs: torch.Tensor | None = None,
-        bos_token_id: torch.Tensor | None = None,
-        model_kwargs: dict[str, torch.Tensor] | None = None,
+        self: "GenerativePreTrainedModel",
+        inputs: torch.Tensor | None,
+        bos_token_id: torch.Tensor | None,
+        model_kwargs: dict[str, torch.Tensor],
     ) -> torch.LongTensor:
         """Initializes input ids for generation, if necessary."""
         if inputs is not None:
             return inputs

         encoder_outputs = model_kwargs.get("encoder_outputs")
-        if self.config.is_encoder_decoder and encoder_outputs is not None:
+        last_hidden_state = getattr(encoder_outputs, "last_hidden_state", None)
+        if self.config.is_encoder_decoder and last_hidden_state is not None:
             # make dummy input_ids with value -100, as a sanity check ensuring that they won't be used for encoding
-            shape = encoder_outputs.last_hidden_state.size()[:-1]
+            shape = last_hidden_state.size()[:-1]
             return torch.ones(shape, dtype=torch.long, device=self.device) * -100

         # If there is some tensor in `model_kwargs`, we can infer the batch size from it. This is unique to this method
@@ -746,7 +748,7 @@ def _prepare_attention_mask_for_generation(
         return attention_mask

     def _prepare_encoder_decoder_kwargs_for_generation(
-        self,
+        self: "GenerativePreTrainedModel",
         inputs_tensor: torch.Tensor,
         model_kwargs,
         model_input_name: str | None,
@@ -787,7 +789,7 @@ def _prepare_encoder_decoder_kwargs_for_generation(
         self: "GenerativePreTrainedModel",
         batch_size: int,
         model_input_name: str,
-        model_kwargs: dict[str, torch.Tensor],
+        model_kwargs: dict[str, torch.Tensor],
     ) -> tuple[torch.LongTensor, dict[str, torch.Tensor]]:
         """
         Prepares the decoder input IDs for generation.
@@ -941,7 +943,7 @@ def _update_model_kwargs_for_generation(
         return model_kwargs

     def _get_candidate_generator(
-        self,
+        self: "GenerativePreTrainedModel",
         generation_config: GenerationConfig,
         input_ids: torch.LongTensor,
         inputs_tensor: torch.Tensor,
@@ -975,6 +977,9 @@ def _get_candidate_generator(
                 vocab_size=self.config.get_text_config().vocab_size,
             )
         elif different_tokenizers:
+            assistant_model = cast("PreTrainedModel", assistant_model)
+            target_tokenizer = cast("PreTrainedTokenizerBase", target_tokenizer)
+            assistant_tokenizer = cast("PreTrainedTokenizerBase", assistant_tokenizer)
             if generation_config.do_sample is True:
                 atm_translator = AssistantVocabTranslatorCache.get_translator(
                     target_tokenizer,
@@ -1023,7 +1028,7 @@ def _get_candidate_generator(
         return candidate_generator

     def _get_logits_processor(
-        self,
+        self: "GenerativePreTrainedModel",
         generation_config: GenerationConfig,
         input_ids_seq_length: int | None = None,
         encoder_input_ids: torch.LongTensor | None = None,
@@ -1060,7 +1065,7 @@ def _get_logits_processor(
             generation_config.encoder_repetition_penalty is not None
             and generation_config.encoder_repetition_penalty != 1.0
         ):
-            if len(encoder_input_ids.shape) == 2:
+            if encoder_input_ids is not None and len(encoder_input_ids.shape) == 2:
                 processors.append(
                     EncoderRepetitionPenaltyLogitsProcessor(
                         penalty=generation_config.encoder_repetition_penalty,
@@ -1081,7 +1086,7 @@ def _get_logits_processor(
             generation_config.encoder_no_repeat_ngram_size is not None
             and generation_config.encoder_no_repeat_ngram_size > 0
         ):
-            if len(encoder_input_ids.shape) == 2:
+            if encoder_input_ids is not None and len(encoder_input_ids.shape) == 2:
                 processors.append(
                     EncoderNoRepeatNGramLogitsProcessor(
                         generation_config.encoder_no_repeat_ngram_size,
@@ -1246,7 +1251,7 @@ def _get_logits_processor(
         return processors

     def _get_stopping_criteria(
-        self,
+        self: "GenerativePreTrainedModel",
         generation_config: GenerationConfig,
         stopping_criteria: StoppingCriteriaList | None,
         tokenizer: Optional["PreTrainedTokenizerBase"] = None,
@@ -1321,7 +1326,7 @@ def _merge_criteria_processor_list(
         return final_list

     def compute_transition_scores(
-        self,
+        self: "GenerativePreTrainedModel",
         sequences: torch.Tensor,
         scores: tuple[torch.Tensor],
         beam_indices: torch.Tensor | None = None,
@@ -1410,13 +1415,15 @@ def compute_transition_scores(
         # 2. reshape scores as [batch_size*vocab_size, # generation steps] with # generation steps being
         # seq_len - input_length
-        scores = torch.stack(scores).reshape(len(scores), -1).transpose(0, 1)
+        stacked_scores: torch.Tensor = torch.stack(scores).reshape(len(scores), -1).transpose(0, 1)

         # 3. Optionally normalize the logits (across the vocab dimension)
         if normalize_logits:
-            scores = scores.reshape(-1, self.config.get_text_config().vocab_size, scores.shape[-1])
-            scores = torch.nn.functional.log_softmax(scores, dim=1)
-            scores = scores.reshape(-1, scores.shape[-1])
+            stacked_scores = stacked_scores.reshape(
+                -1, self.config.get_text_config().vocab_size, stacked_scores.shape[-1]
+            )
+            stacked_scores = torch.nn.functional.log_softmax(stacked_scores, dim=1)
+            stacked_scores = stacked_scores.reshape(-1, stacked_scores.shape[-1])

         # 4. cut beam_indices to longest beam length
         beam_indices_mask = beam_indices < 0
@@ -1435,14 +1442,16 @@ def compute_transition_scores(
         indices = sequences[:, cut_idx:] + beam_sequence_indices

         # 8. Compute scores
-        transition_scores = scores.gather(0, indices)
+        transition_scores = stacked_scores.gather(0, indices)

         # 9. Mask out transition scores of beams that stopped early
         transition_scores[beam_indices_mask] = 0

         return transition_scores

-    def _validate_generation_mode(self, generation_mode, generation_config, generation_mode_kwargs):
+    def _validate_generation_mode(
+        self: "GenerativePreTrainedModel", generation_mode, generation_config, generation_mode_kwargs
+    ):
         if generation_mode == GenerationMode.BEAM_SEARCH and "streamer" in generation_mode_kwargs:
             raise ValueError(
                 "`streamer` cannot be used with beam search (yet!). Make sure that `num_beams` is set to 1."
@@ -1488,7 +1497,7 @@ def _validate_generation_mode(
                         f"The main and assistant models have different tokenizers.  Please provide `tokenizer` and `assistant_tokenizer` to `generate()` {doc_reference}."
                     )

-    def _validate_model_kwargs(self, model_kwargs: dict[str, Any]):
+    def _validate_model_kwargs(self: "GenerativePreTrainedModel", model_kwargs: dict[str, Any]):
         """Validates model kwargs for generation. Generate argument typos will also be caught here."""
         # Excludes arguments that are handled before calling any model function
         if self.config.is_encoder_decoder:
@@ -1543,7 +1552,9 @@ def _validate_model_kwargs(self, model_kwargs: dict[str, Any]):
                 " generate arguments will also show up in this list)"
             )

-    def _validate_generated_length(self, generation_config, input_ids_length, has_default_max_length):
+    def _validate_generated_length(
+        self: "GenerativePreTrainedModel", generation_config, input_ids_length, has_default_max_length
+    ):
         """Performs validation related to the resulting generated length"""
         # 1. Max length warnings related to poor parameterization
         if has_default_max_length and generation_config.max_new_tokens is None:
@@ -1588,7 +1599,7 @@ def _validate_generated_length(self, generation_config, input_ids_length, has_d
                 )

     def _prepare_generated_length(
-        self,
+        self: "GenerativePreTrainedModel",
         generation_config,
         has_default_max_length,
         has_default_min_length,
@@ -1644,7 +1655,7 @@ def _prepare_generated_length(
         return generation_config

     def _prepare_generation_config(
-        self,
+        self: "GenerativePreTrainedModel",
         generation_config: GenerationConfig | None,
         **kwargs: Any,
     ) -> tuple[GenerationConfig, dict]:
@@ -1710,7 +1721,7 @@ def _prepare_generation_config(
         utils.py

         return generation_config, model_kwargs

-    def _get_initial_cache_position(self: "GenerativePreTrainedModel", seq_length, device, model_kwargs):
+    def _get_initial_cache_position(self: "GenerativePreTrainedModel", seq_length, device, model_kwargs):
         """Calculates `cache_position` for the pre-fill stage based on `input_ids` and optionally past length"""
         # `torch.compile`-friendly `torch.arange` from a shape -- the lines below are equivalent to `torch.arange`
         if "cache_position" in model_kwargs and model_kwargs["cache_position"] is not None:
@@ -1737,7 +1748,7 @@ def _get_initial_cache_position(self: "GenerativePreTrainedModel", seq_length,
         return model_kwargs

     def _prepare_static_cache(
-        self, cache_implementation: str, batch_size: int, max_cache_len: int, model_kwargs
+        self: "GenerativePreTrainedModel", cache_implementation: str, batch_size: int, max_cache_len: int, model_kwargs
     ) -> Cache:
         """
         Sets a cache for `generate`, that will persist across calls. A new cache will only be initialized a
@@ -1747,20 +1758,26 @@ def _prepare_static_cache(
         """
         offload_cache = "offloaded" in cache_implementation

+        cache_to_check: StaticCache | None = None
         if hasattr(self, "_cache"):
-            cache_to_check = self._cache.self_attention_cache if self.config.is_encoder_decoder else self._cache
+            if isinstance(self._cache, EncoderDecoderCache):
+                cache_to_check = self._cache.self_attention_cache
+            elif isinstance(self._cache, StaticCache):
+                cache_to_check = self._cache

         need_new_cache = (
-            not hasattr(self, "_cache")
+            cache_to_check is None
             or cache_to_check.offloading != offload_cache
             or cache_to_check.max_batch_size != batch_size
             or cache_to_check.max_cache_len < max_cache_len
         )

-        if self.config.is_encoder_decoder and hasattr(self, "_cache"):
+        encoder_decoder_cache = getattr(self, "_cache", None)
+        if isinstance(encoder_decoder_cache, EncoderDecoderCache):
             need_new_cache = (
                 need_new_cache
-                or self._cache.cross_attention_cache.max_cache_len != model_kwargs["encoder_outputs"][0].shape[1]
+                or encoder_decoder_cache.cross_attention_cache.max_cache_len
+                != model_kwargs["encoder_outputs"][0].shape[1]
             )

         if need_new_cache:
@@ -1782,7 +1799,7 @@ def _prepare_static_cache(
         return self._cache

     @classmethod
-    def _supports_default_dynamic_cache(cls) -> bool:
+    def _supports_default_dynamic_cache(cls: type["GenerativePreTrainedModel"]) -> bool:
         """
         Return `True` if current model can use a `DynamicCache` instance when initializing the `past_key_values`.
         This adds exception for some models like `Mamba` models which use their own caches.
@@ -1801,7 +1818,7 @@ def _supports_default_dynamic_cache(cls) -> bool:
         )

     def _prepare_cache_for_generation(
-        self,
+        self: "GenerativePreTrainedModel",
         generation_config: GenerationConfig,
         model_kwargs: dict,
         generation_mode: GenerationMode,
@@ -1904,7 +1921,7 @@ def _prepare_cache_for_generation(
                 DynamicCache(**dynamic_cache_kwargs),  # cross-attention cache
             )

-    def _supports_logits_to_keep(self) -> bool:
+    def _supports_logits_to_keep(self: "GenerativePreTrainedModel") -> bool:
         """
         Return True if the current model supports the keyword argument `logits_to_keep` in forward()
         to save memory. Checking it in this way allows to avoid using a new model attribute.
@@ -1912,7 +1929,7 @@ def _supports_logits_to_keep(self) -> bool:
         return "logits_to_keep" in set(inspect.signature(self.forward).parameters.keys())

     def _prepare_special_tokens(
-        self,
+        self: "GenerativePreTrainedModel",
         generation_config: GenerationConfig,
         kwargs_has_attention_mask: bool | None = None,
         device: torch.device | str | None = None,
@@ -1990,7 +2007,9 @@ def _tensor_or_none(token, device=None):
         generation_config._pad_token_tensor = pad_token_tensor
         generation_config._decoder_start_token_tensor = decoder_start_token_tensor

-    def _valid_auto_compile_criteria(self, model_kwargs: dict[str, Any], generation_config: GenerationConfig) -> bool:
+    def _valid_auto_compile_criteria(
+        self: "GenerativePreTrainedModel", model_kwargs: dict[str, Any], generation_config: GenerationConfig
+    ) -> bool:
         """
         Determines whether to trigger auto-compilation of the model's forward pass at generation time.
         """
@@ -2046,7 +2065,7 @@ def _valid_auto_compile_criteria(self, model_kwargs: dict[str, Any], generation
         return can_compile

     @contextmanager
-    def _optimize_model_for_decode(self):
+    def _optimize_model_for_decode(self: "GenerativePreTrainedModel"):
         original_experts_implementation = self.config._experts_implementation
         # On non-CPU devices, 'batched_mm' can trade off a bit of memory (by duplicating selected experts weights)
         # for the much better speed during decoding, especially for smaller inputs. On CPU, grouped_mm is usually better.
@@ -2104,8 +2123,9 @@ def _extract_generation_mode_kwargs(
             "assistant_model": assistant_model,
             "streamer": streamer,
         }
+        world_size = dist.get_world_size() if dist.is_available() and dist.is_initialized() else 1  # type: ignore
         generation_mode_kwargs["synced_gpus"] = (
-            (is_deepspeed_zero3_enabled() or is_fsdp_managed_module(self)) and dist.get_world_size() > 1
+            (is_deepspeed_zero3_enabled() or is_fsdp_managed_module(self)) and world_size > 1
             if synced_gpus is None
             else synced_gpus
         )
@@ -2121,7 +2141,7 @@ def _extract_generation_mode_kwargs(

     @torch.no_grad()
     def generate(
-        self,
+        self: "GenerativePreTrainedModel",
         inputs: torch.Tensor | None = None,
         generation_config: GenerationConfig | None = None,
         logits_processor: LogitsProcessorList | None = None,
@@ -2554,7 +2574,7 @@ def _has_unfinished_sequences(self, this_peer_finished: bool, synced_gpus: bool,
             # The following logic allows an early break if all peers finished generating their sequence
             this_peer_finished_flag = torch.tensor(0.0 if this_peer_finished else 1.0, device=device)
             # send 0.0 if we finished, 1.0 otherwise
-            dist.all_reduce(this_peer_finished_flag, op=dist.ReduceOp.SUM)
+            dist.all_reduce(this_peer_finished_flag, op=dist.ReduceOp.SUM)  # type: ignore
             # did all peers finish? the reduced sum will be 0.0 then
             if this_peer_finished_flag.item() == 0.0:
                 return False
@@ -2605,9 +2625,9 @@ def heal_tokens(
         # their tokenization (e.g. 'Ġ') to enable search for tokens prefixed with a whitespace
         if tokenizer.convert_tokens_to_ids(" ") is not None:
             space_tok = tokenizer.convert_ids_to_tokens(tokenizer.convert_tokens_to_ids(" "))[0]
-            tail_toks = (tokenizer.decode(t).replace(" ", space_tok) for t in tail_ids)
+            tail_toks = (cast(str, tokenizer.decode(t)).replace(" ", space_tok) for t in tail_ids)
         else:
-            tail_toks = (tokenizer.decode(t) for t in tail_ids)
+            tail_toks = (cast(str, tokenizer.decode(t)) for t in tail_ids)

         for batch_idx, (tail_id, tail_tok) in enumerate(zip(tail_ids, tail_toks)):
             batch_ids = input_ids[batch_idx]
@@ -2648,7 +2668,7 @@ def heal_tokens(
         return input_ids

     def _sample(
-        self,
+        self: "GenerativePreTrainedModel",
         input_ids: torch.LongTensor,
         logits_processor: LogitsProcessorList,
         stopping_criteria: StoppingCriteriaList,
@@ -3066,7 +3086,7 @@ def _update_finished_beams(
     # end of auxiliary functions for beam search

     def _beam_search(
-        self,
+        self: "GenerativePreTrainedModel",
         input_ids: torch.LongTensor,
         logits_processor: LogitsProcessorList,
         stopping_criteria: StoppingCriteriaList,
         -3415,7 +3435,7 @@ def _beam_search(
             return sequences

     def _assisted_decoding(
-        self,
+        self: "GenerativePreTrainedModel",
         input_ids: torch.LongTensor,
         logits_processor: LogitsProcessorList,
         stopping_criteria: StoppingCriteriaList,
@@ -3688,7 +3708,7 @@ def _assisted_decoding(
             streamer.end()

         if (
-            hasattr(candidate_generator, "assistant_model")
+            isinstance(candidate_generator, AssistedCandidateGenerator)
             and candidate_generator.assistant_model.generation_config.num_assistant_tokens_schedule == "heuristic"
         ):
             candidate_generator.assistant_model.generation_config.num_assistant_tokens = (
@@ -3725,7 +3745,7 @@ def _assisted_decoding(

     # TODO: v5.1: make public once API stabilized
     def _prefill(
-        self,
+        self: "GenerativePreTrainedModel",
         input_ids: torch.LongTensor,
         generation_config: GenerationConfig,
         model_kwargs: dict,

diff --git a/src/transformers/generation/watermarking.py b/src/transformers/generation/watermarking.py
index c6e88407fdda..b42a949d4389 100644
--- a/src/transformers/generation/watermarking.py
+++ b/src/transformers/generation/watermarking.py
@@ -124,7 +124,7 @@ def __init__(
         self,
         model_config: "PreTrainedConfig",
         device: str,
-        watermarking_config: Union["WatermarkingConfig", dict] | None,
+        watermarking_config: Union["WatermarkingConfig", dict],
         ignore_repeated_ngrams: bool = False,
         max_cache_size: int = 128,
     ):

diff --git a/src/transformers/models/clvp/modeling_clvp.py b/src/transformers/models/clvp/modeling_clvp.py
index 3f7b4ee0cc38..f810b8ee2e9f 100644
--- a/src/transformers/models/clvp/modeling_clvp.py
+++ b/src/transformers/models/clvp/modeling_clvp.py
@@ -1266,9 +1266,9 @@ def set_input_embeddings(self, new_embeddings):

     def _prepare_model_inputs(
         self,
-        inputs: torch.Tensor | None = None,
-        bos_token_id: int | None = None,
-        model_kwargs: dict[str, torch.Tensor] | None = None,
+        inputs: torch.Tensor | None,
+        bos_token_id: int | None,
+        model_kwargs: dict[str, torch.Tensor],
     ) -> tuple[torch.Tensor, str | None, dict[str, torch.Tensor]]:
         """
         This function extracts the model-specific `inputs` for generation.

diff --git a/src/transformers/models/musicgen/modeling_musicgen.py b/src/transformers/models/musicgen/modeling_musicgen.py
index 79f108b3e956..0bc741bb5c02 100644
--- a/src/transformers/models/musicgen/modeling_musicgen.py
+++ b/src/transformers/models/musicgen/modeling_musicgen.py
@@ -1956,9 +1956,9 @@ def freeze_text_encoder(self):

     def _maybe_initialize_input_ids_for_generation(
         self,
-        inputs: torch.Tensor | None = None,
-        bos_token_id: int | None = None,
-        model_kwargs: dict[str, torch.Tensor] | None = None,
+        inputs: torch.Tensor | None,
+        bos_token_id: int | None,
+        model_kwargs: dict[str, torch.Tensor],
     ) -> torch.LongTensor:
         """Initializes input ids for generation, if necessary."""
         if inputs is not None:

diff --git a/src/transformers/models/musicgen_melody/modeling_musicgen_melody.py b/src/transformers/models/musicgen_melody/modeling_musicgen_melody.py
index d2b93de21897..1f085ef99862 100644
--- a/src/transformers/models/musicgen_melody/modeling_musicgen_melody.py
+++ b/src/transformers/models/musicgen_melody/modeling_musicgen_melody.py
@@ -1853,9 +1853,9 @@ def resize_token_embeddings(self, *args, **kwargs):

     def _maybe_initialize_input_ids_for_generation(
         self,
-        inputs: torch.Tensor | None = None,
-        bos_token_id: int | None = None,
-        model_kwargs: dict[str, torch.Tensor] | None = None,
+        inputs: torch.Tensor | None,
+        bos_token_id: int | None,
+        model_kwargs: dict[str, torch.Tensor],
     ) -> torch.LongTensor:
         """Initializes input ids for generation, if necessary."""
         if inputs is not None:

diff --git a/src/transformers/utils/logging.py b/src/transformers/utils/logging.py
index 4b38b824ede7..58fdd0e37123 100644
--- a/src/transformers/utils/logging.py
+++ b/src/transformers/utils/logging.py
@@ -33,7 +33,7 @@
 import huggingface_hub.utils as hf_hub_utils
 from tqdm import auto as tqdm_lib

-from ._typing import TransformersLogger
+from .._typing import TransformersLogger


 _lock = threading.Lock()

diff --git a/utils/check_types.py b/utils/check_types.py
new file mode 100644
index 000000000000..a87a521dda0d
--- /dev/null
+++ b/utils/check_types.py
@@ -0,0 +1,25 @@
+"""Run ty type checking on specified directories.
+
+Usage:
+    python utils/check_types.py src/transformers/utils src/transformers/generation
+"""
+
+import subprocess
+import sys
+
+
+def main():
+    if len(sys.argv) < 2:
+        print(f"Usage: {sys.argv[0]} <directory> [<directory> ...]")
+        sys.exit(1)
+
+    directories = sys.argv[1:]
+    print(f"Running ty check on: {', '.join(directories)}")
+    result = subprocess.run(
+        ["ty", "check", "--respect-ignore-files", "--exclude", "**/*_pb*", *directories],
+    )
+    sys.exit(result.returncode)
+
+
+if __name__ == "__main__":
+    main()
GOLDENDOFPATCH

# Apply the patch
cd /workspace/transformers
git apply /tmp/gold.patch || git apply --3way /tmp/gold.patch || (echo "Patch failed to apply"; exit 1)

echo "Gold patch applied successfully"
