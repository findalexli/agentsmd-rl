#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency check: if _get_template_variables already exists, patch is applied
if grep -q '_get_template_variables' src/transformers/utils/chat_template_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/smolvlm/processing_smolvlm.py b/src/transformers/models/smolvlm/processing_smolvlm.py
index 21d7f24466a5..351eb265926d 100644
--- a/src/transformers/models/smolvlm/processing_smolvlm.py
+++ b/src/transformers/models/smolvlm/processing_smolvlm.py
@@ -20,7 +20,7 @@

 from ...feature_extraction_utils import BatchFeature
 from ...image_utils import ImageInput, make_nested_list_of_images
-from ...processing_utils import AllKwargsForChatTemplate, ProcessingKwargs, ProcessorMixin, Unpack
+from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack
 from ...tokenization_utils_base import BatchEncoding, TextInput
 from ...utils import auto_docstring, is_num2words_available, is_vision_available, logging
 from ...video_utils import VideoInput
@@ -292,7 +292,8 @@ def apply_chat_template(
         self,
         conversation: list[dict[str, str]] | list[list[dict[str, str]]],
         chat_template: str | None = None,
-        **kwargs: Unpack[AllKwargsForChatTemplate],
+        processor_kwargs: dict | None = None,
+        **kwargs,
     ) -> str:
         """
         Similar to the `apply_chat_template` method on tokenizers, this method applies a Jinja template to input
@@ -336,10 +337,15 @@ def apply_chat_template(
             # re-assign to the correct default template for BC, if user is not requesting their own template
             chat_template = DEFAULT_CHAT_TEMPLATE

-        kwargs.setdefault("num_frames", self.video_processor.num_frames)
-        kwargs.setdefault("fps", self.video_processor.fps)
+        # Users might be passing processor kwargs simply as `**kwargs`
+        if processor_kwargs:
+            processor_kwargs.setdefault("num_frames", self.video_processor.num_frames)
+            processor_kwargs.setdefault("fps", self.video_processor.fps)
+        else:
+            kwargs.setdefault("num_frames", self.video_processor.num_frames)
+            kwargs.setdefault("fps", self.video_processor.fps)

-        return super().apply_chat_template(conversation, chat_template, **kwargs)
+        return super().apply_chat_template(conversation, chat_template, processor_kwargs=processor_kwargs, **kwargs)


 __all__ = ["SmolVLMProcessor"]
diff --git a/src/transformers/models/voxtral/processing_voxtral.py b/src/transformers/models/voxtral/processing_voxtral.py
index 53fad27179e7..5757a490692a 100644
--- a/src/transformers/models/voxtral/processing_voxtral.py
+++ b/src/transformers/models/voxtral/processing_voxtral.py
@@ -28,8 +28,9 @@

 from ...audio_utils import AudioInput, load_audio_as, make_list_of_audio
 from ...feature_extraction_utils import BatchFeature
-from ...processing_utils import AllKwargsForChatTemplate, AudioKwargs, ProcessingKwargs, ProcessorMixin, Unpack
+from ...processing_utils import AudioKwargs, ProcessingKwargs, ProcessorMixin, Unpack
 from ...tokenization_utils_base import PreTokenizedInput, TextInput
+from ...utils.chat_template_utils import _get_template_variables


 logger = logging.get_logger(__name__)
@@ -97,7 +98,18 @@ def _retrieve_input_features(self, audio, max_source_positions, **kwargs):
     def apply_chat_template(
         self,
         conversation: list[dict[str, str]] | list[list[dict[str, str]]],
-        **kwargs: Unpack[AllKwargsForChatTemplate],
+        chat_template: str | None = None,
+        tools: list[dict] | None = None,
+        documents: list[dict[str, str]] | None = None,
+        add_generation_prompt: bool = False,
+        continue_final_message: bool = False,
+        return_assistant_tokens_mask: bool = False,
+        tokenize: bool = False,
+        return_tensors: str | None = None,
+        return_dict: bool = False,
+        load_audio_from_video: bool = False,
+        processor_kwargs: dict | None = None,
+        **kwargs,
     ) -> str:
         """
         This method applies the model's chat completion template given a conversation. It relies on MistralCommonBackend's
@@ -139,12 +151,12 @@ def apply_chat_template(
             conversation (`Union[list[Dict, [str, str]], list[list[dict[str, str]]]]`):
                 The conversation to format.
         """
-        if kwargs.get("continue_final_message", False):
-            if kwargs.get("add_generation_prompt", False):
+        if continue_final_message:
+            if add_generation_prompt:
                 raise ValueError(
                     "continue_final_message and add_generation_prompt are not compatible. Use continue_final_message when you want the model to continue the final message, and add_generation_prompt when you want to add a header that will prompt it to start a new assistant message instead."
                 )
-            if kwargs.get("return_assistant_tokens_mask", False):
+            if return_assistant_tokens_mask:
                 raise ValueError("continue_final_message is not compatible with return_assistant_tokens_mask.")

         if isinstance(conversation, (list, tuple)) and (
@@ -156,21 +168,23 @@ def apply_chat_template(
             is_batched = False
             conversations = [conversation]

-        # - `sampling_rate` is already fixed in `VoxtralProcessorKwargs._defaults` and audio loading is
-        #   delegated to `mistral_common`'s tokenizer which handles it internally.
-        # - `load_audio_from_video` is irrelevant as Voxtral is a speech-only model with no video support.
-        # We strip them here to avoid passing unrecognized kwargs to `_merge_kwargs`.
-        unsupported_keys = {"sampling_rate", "load_audio_from_video"} & kwargs.keys()
-        if unsupported_keys:
-            for key in unsupported_keys:
-                kwargs.pop(key)
+        # Users might still be passing processing kwargs in `**kwargs` so we need to filter
+        # out additional kwargs that the template expects via Jinja2 template introspection
+        # We strip unrelated kwargs to avoid passing unrecognized kwargs to `_merge_kwargs`.
+        processor_kwargs = processor_kwargs or {}
+        template_kwargs = _get_template_variables(chat_template)
+        processor_kwargs_from_kwargs = {k: v for k, v in kwargs.items() if k not in template_kwargs}
+        if processor_kwargs_from_kwargs:
             logger.warning(
-                f"{', '.join(sorted(unsupported_keys))} {'is' if len(unsupported_keys) == 1 else 'are'} not supported for VoxtralProcessor's apply_chat_template and will be ignored."
+                "Kwargs passed to `processor.__call__` have to be in `processor_kwargs` dict, not in `**kwargs`"
             )
+            processor_kwargs = processor_kwargs_from_kwargs

+        if return_tensors:
+            processor_kwargs["return_tensors"] = return_tensors
         output_kwargs = self._merge_kwargs(
             VoxtralProcessorKwargs,
-            **kwargs,
+            **processor_kwargs,
         )
         text_kwargs = output_kwargs["text_kwargs"]
         audio_kwargs = output_kwargs["audio_kwargs"]
diff --git a/src/transformers/processing_utils.py b/src/transformers/processing_utils.py
index 24cefad6a222..6c8d1f3af8dc 100644
--- a/src/transformers/processing_utils.py
+++ b/src/transformers/processing_utils.py
@@ -58,7 +58,7 @@
     list_repo_templates,
     logging,
 )
-from .utils.chat_template_utils import render_jinja_template
+from .utils.chat_template_utils import _get_template_variables, render_jinja_template
 from .utils.type_validators import (
     device_validator,
     image_size_validator,
@@ -472,6 +472,7 @@ class CustomProcessorKwargs(ProcessingKwargs, total=False):

 class TokenizerChatTemplateKwargs(TypedDict, total=False):
     """
+    NOTE: `TokenizerChatTemplateKwargs` is deprecated and will be removed in future versions
     Keyword arguments for tokenizer's `apply_chat_template`, when it is called from within a processor.

     tools (`list[Dict]`, *optional*):
@@ -516,6 +517,8 @@ class TokenizerChatTemplateKwargs(TypedDict, total=False):

 class ProcessorChatTemplateKwargs(TokenizerChatTemplateKwargs, total=False):
     """
+    NOTE: `ProcessorChatTemplateKwargs` is deprecated and will be removed in future versions
+
     Keyword arguments for processor's `apply_chat_template`.

     tokenize (`bool`, *optional*, defaults to `False`):
@@ -533,6 +536,8 @@ class ProcessorChatTemplateKwargs(TokenizerChatTemplateKwargs, total=False):


 class AllKwargsForChatTemplate(TypedDict, total=False):
+    "NOTE: `AllKwargsForChatTemplate` is deprecated and will be removed in future versions"
+
     processor_kwargs: ProcessingKwargs
     template_kwargs: ProcessorChatTemplateKwargs

@@ -1637,7 +1642,17 @@ def apply_chat_template(
         self,
         conversation: list[dict[str, str]] | list[list[dict[str, str]]],
         chat_template: str | None = None,
-        **kwargs: Unpack[AllKwargsForChatTemplate],
+        tools: list[dict] | None = None,
+        documents: list[dict[str, str]] | None = None,
+        add_generation_prompt: bool = False,
+        continue_final_message: bool = False,
+        return_assistant_tokens_mask: bool = False,
+        tokenize: bool = False,
+        return_tensors: str | TensorType | None = None,
+        return_dict: bool = False,
+        load_audio_from_video: bool = False,
+        processor_kwargs: dict | None = None,
+        **kwargs,
     ) -> str:
         """
         Similar to the `apply_chat_template` method on tokenizers, this method applies a Jinja template to input
@@ -1664,6 +1679,8 @@ def apply_chat_template(
                 The Jinja template to use for formatting the conversation. If not provided, the tokenizer's
                 chat template is used.
         """
+        processor_kwargs = processor_kwargs or {}
+
         if chat_template is None:
             if isinstance(self.chat_template, dict) and "default" in self.chat_template:
                 chat_template = self.chat_template["default"]
@@ -1687,6 +1704,16 @@ def apply_chat_template(
                 # It's a template string, render it directly
                 pass

+        # Users might still be passing processing kwargs in `**kwargs` so we need to filter
+        # out additional kwargs that the template expects via Jinja2 template introspection
+        template_kwargs = _get_template_variables(chat_template)
+        processor_kwargs_from_kwargs = {k: v for k, v in kwargs.items() if k not in template_kwargs}
+        if processor_kwargs_from_kwargs:
+            logger.warning(
+                "Kwargs passed to `processor.__call__` have to be in `processor_kwargs` dict, not in `**kwargs`"
+            )
+            processor_kwargs = processor_kwargs_from_kwargs
+
         # Check if tokenizer is fast - use backend attribute if available, otherwise fall back to class name
         is_tokenizers_fast = False
         if hasattr(self, "tokenizer"):
@@ -1696,42 +1723,32 @@ def apply_chat_template(
                 # Fallback to class name check
                 is_tokenizers_fast = self.tokenizer.__class__.__name__.endswith("Fast")

-        if kwargs.get("continue_final_message", False):
-            if kwargs.get("add_generation_prompt", False):
+        if continue_final_message:
+            if add_generation_prompt:
                 raise ValueError(
                     "continue_final_message and add_generation_prompt are not compatible. Use continue_final_message when you want the model to continue the final message, and add_generation_prompt when you want to add a header that will prompt it to start a new assistant message instead."
                 )
-            if kwargs.get("return_assistant_tokens_mask", False):
+            if return_assistant_tokens_mask:
                 raise ValueError("continue_final_message is not compatible with return_assistant_tokens_mask.")

-        if kwargs.get("return_assistant_tokens_mask", False):
+        if return_assistant_tokens_mask:
             if not is_tokenizers_fast:
                 raise ValueError(
                     "`return_assistant_tokens_mask` is not possible with slow tokenizers. Make sure you have `tokenizers` installed. "
                     "If the error persists, open an issue to support a Fast tokenizer for your model."
                 )
             else:
-                kwargs["return_offsets_mapping"] = True  # force offset mapping so we can infer token boundaries
-
-        # Fill sets of kwargs that should be used by jinja template, filtering out kwargs used in `processor.__call__`
-        # NOTE: we don't only filter but also set the default values here. Without default values, we can remove it
-        template_kwargs = {}
-        for key in AllKwargsForChatTemplate.__annotations__["template_kwargs"].__annotations__:
-            kwarg_type_defaults = AllKwargsForChatTemplate.__annotations__["template_kwargs"]
-            default_value = getattr(kwarg_type_defaults, key, None)
-            value = kwargs.pop(key, default_value)
-            if value is not None and not isinstance(value, dict):
-                template_kwargs[key] = value
-
-        # Pass unprocessed custom kwargs
-        template_kwargs.update(kwargs)
+                processor_kwargs["return_offsets_mapping"] = (
+                    True  # force offset mapping so we can infer token boundaries
+                )

         # Set the sampling rate to load the audio files if user hasn't already passed with `kwargs`
-        if "sampling_rate" not in template_kwargs:
+        sampling_rate = kwargs.get("sampling_rate", processor_kwargs.get("sampling_rate"))
+        if sampling_rate is None:
             if hasattr(self, "feature_extractor") and hasattr(self.feature_extractor, "sampling_rate"):
-                template_kwargs["sampling_rate"] = self.feature_extractor.sampling_rate
+                sampling_rate = self.feature_extractor.sampling_rate
             else:
-                template_kwargs["sampling_rate"] = 16_000
+                sampling_rate = 16_000

         if isinstance(conversation, (list, tuple)) and (
             isinstance(conversation[0], (list, tuple)) or hasattr(conversation[0], "content")
@@ -1759,9 +1776,6 @@ def apply_chat_template(
                         new_content.append(content)
                 message["content"] = new_content

-        tokenize = template_kwargs.pop("tokenize", False)
-        return_dict = template_kwargs.pop("return_dict", True)
-
         if tokenize:
             batch_images, batch_videos = [], []
             batch_audios = []
@@ -1791,29 +1805,31 @@ def apply_chat_template(
                     videos.extend(video_fnames)

                     # Audio models do not accept nested list of audios (yet!) so we construct a flat input audio list
-                    if not template_kwargs["load_audio_from_video"]:
+                    if not load_audio_from_video:
                         for fname in audio_fnames:
-                            batch_audios.append(load_audio(fname, sampling_rate=template_kwargs["sampling_rate"]))
+                            batch_audios.append(load_audio(fname, sampling_rate=sampling_rate))
                     else:
                         for fname in video_fnames:
-                            batch_audios.append(load_audio(fname, sampling_rate=template_kwargs["sampling_rate"]))
+                            batch_audios.append(load_audio(fname, sampling_rate=sampling_rate))

                 # Currently all processors can accept nested list of batches, but not flat list of visuals
                 # So we'll make a batched list of images and let the processor handle it
                 batch_images.append(images)
                 batch_videos.append(videos)

-        special_tokens_map = {}
-        if hasattr(self, "tokenizer") and hasattr(self.tokenizer, "special_tokens_map"):
-            special_tokens = self.tokenizer.special_tokens_map
-            # Filter out tokens that conflict with template kwargs
-            special_tokens_map = {k: v for k, v in special_tokens.items() if k not in template_kwargs}
-
+        template_kwargs = {
+            **self.tokenizer.special_tokens_map,
+            **kwargs,
+        }  # kwargs overwrite special tokens if both are present
         prompt, generation_indices = render_jinja_template(
             conversations=conversations,
+            tools=tools,
+            documents=documents,
             chat_template=chat_template,
-            **template_kwargs,  # different flags such as `return_assistant_mask`
-            **special_tokens_map,  # tokenizer special tokens are used by some templates
+            return_assistant_tokens_mask=return_assistant_tokens_mask,
+            continue_final_message=continue_final_message,
+            add_generation_prompt=add_generation_prompt,
+            **template_kwargs,
         )

         if not is_batched:
@@ -1828,14 +1844,18 @@ def apply_chat_template(
             # without actionable solution for users
             single_prompt = prompt[0] if is_batched else prompt
             if self.tokenizer.bos_token is not None and single_prompt.startswith(self.tokenizer.bos_token):
-                kwargs["add_special_tokens"] = False
+                processor_kwargs["add_special_tokens"] = False

             # Always sample frames by default unless explicitly set to `False` by users. If users do not pass `num_frames`/`fps`
             # sampling should not done for BC.
-            if "do_sample_frames" not in kwargs and (
-                kwargs.get("fps") is not None or kwargs.get("num_frames") is not None
+            if "do_sample_frames" not in processor_kwargs and (
+                processor_kwargs.get("fps") is not None or processor_kwargs.get("num_frames") is not None
             ):
-                kwargs["do_sample_frames"] = True
+                processor_kwargs["do_sample_frames"] = True
+
+            # Set only is user passes a non-None value. Otherwise wa want to use each processor's own defaults
+            if return_tensors:
+                processor_kwargs["return_tensors"] = return_tensors

             images_exist = any((im is not None) for im_list in batch_images for im in im_list)
             videos_exist = any((vid is not None) for vid_list in batch_videos for vid in vid_list)
@@ -1844,11 +1864,11 @@ def apply_chat_template(
                 images=batch_images if images_exist else None,
                 videos=batch_videos if videos_exist else None,
                 audio=batch_audios if batch_audios else None,
-                **kwargs,
+                **processor_kwargs,
             )

             if return_dict:
-                if template_kwargs.get("return_assistant_tokens_mask", False):
+                if return_assistant_tokens_mask:
                     assistant_masks = []
                     offset_mapping = out.pop("offset_mapping")
                     input_ids = out["input_ids"]
@@ -1874,7 +1894,7 @@ def apply_chat_template(
                                 current_mask[token_id] = 1
                         assistant_masks.append(current_mask)
                     out["assistant_masks"] = assistant_masks
-                    out.convert_to_tensors(tensor_type=kwargs.get("return_tensors"))
+                    out.convert_to_tensors(tensor_type=return_tensors)
                 return out
             else:
                 return out["input_ids"]
diff --git a/src/transformers/utils/chat_template_utils.py b/src/transformers/utils/chat_template_utils.py
index 75cafbcac281..a1cf268bbb09 100644
--- a/src/transformers/utils/chat_template_utils.py
+++ b/src/transformers/utils/chat_template_utils.py
@@ -36,6 +36,7 @@
     import jinja2
     import jinja2.exceptions
     import jinja2.ext
+    import jinja2.meta
     import jinja2.nodes
     import jinja2.runtime
     from jinja2.ext import Extension
@@ -382,6 +383,21 @@ def get_json_schema(func: Callable) -> dict:
     return {"type": "function", "function": output}


+@lru_cache
+@no_type_check
+def _get_template_variables(chat_template: str) -> frozenset[str]:
+    """Return the set of undeclared variables referenced by a chat template.
+
+    Uses ``jinja2.meta.find_undeclared_variables`` so that callers can
+    automatically distinguish template-level kwargs from processor kwargs
+    without maintaining a manual allowlist. Needed only to support BC as we
+    allowed all `kwargs` to be merged into one in the past
+    """
+    compiled = _compile_jinja_template(chat_template)
+    ast = compiled.environment.parse(chat_template)
+    return frozenset(jinja2.meta.find_undeclared_variables(ast))
+
+
 def _render_with_assistant_indices(
     compiled_template, messages, tools, documents, add_generation_prompt, **template_kwargs
 ):
diff --git a/tests/models/aria/test_processing_aria.py b/tests/models/aria/test_processing_aria.py
index a196f9bed1a9..2b58095dd30f 100644
--- a/tests/models/aria/test_processing_aria.py
+++ b/tests/models/aria/test_processing_aria.py
@@ -236,8 +236,10 @@ def test_image_chat_template_accepts_processing_kwargs(self):
             messages,
             add_generation_prompt=True,
             tokenize=True,
-            padding="max_length",
-            max_length=50,
+            processor_kwargs={
+                "padding": "max_length",
+                "max_length": 50,
+            },
         )
         self.assertEqual(len(formatted_prompt_tokenized[0]), 50)

@@ -245,8 +247,7 @@ def test_image_chat_template_accepts_processing_kwargs(self):
             messages,
             add_generation_prompt=True,
             tokenize=True,
-            truncation=True,
-            max_length=5,
+            processor_kwargs={"max_length": 5, "truncation": True},
         )
         self.assertEqual(len(formatted_prompt_tokenized[0]), 5)

@@ -264,8 +265,8 @@ def test_image_chat_template_accepts_processing_kwargs(self):
             add_generation_prompt=True,
             tokenize=True,
             return_dict=True,
-            max_image_size=980,
             return_tensors="pt",
+            processor_kwargs={"max_image_size": 980},
         )
         self.assertListEqual(list(out_dict[self.images_input_name].shape), [1, 3, 980, 980])

diff --git a/tests/test_processing_common.py b/tests/test_processing_common.py
index a921292cc9fe..8cd573e3e3ac 100644
--- a/tests/test_processing_common.py
+++ b/tests/test_processing_common.py
@@ -857,7 +857,7 @@ def test_processor_text_has_no_visual(self):
                 tokenize=True,
                 return_dict=True,
                 return_tensors="pt",
-                padding=True,
+                processor_kwargs={"padding": True},
             )
             self.assertTrue(self.text_input_name in inputs_chat_template)

@@ -1579,10 +1579,12 @@ def _test_apply_chat_template(
             batch_messages,
             add_generation_prompt=True,
             tokenize=True,
-            padding="max_length",
-            truncation=True,
             return_tensors=return_tensors,
-            max_length=self.chat_template_max_length,
+            processor_kwargs={
+                "padding": "max_length",
+                "truncation": True,
+                "max_length": self.chat_template_max_length,
+            },
         )
         self.assertEqual(len(tokenized_prompt_100[0]), self.chat_template_max_length)

@@ -1608,7 +1610,7 @@ def _test_apply_chat_template(
             tokenize=True,
             return_dict=True,
             return_tensors=return_tensors,
-            num_frames=2,  # by default no more than 2 frames, otherwise too slow
+            processor_kwargs={"num_frames": 2},  # by default no more than 2 frames, otherwise too slow
         )
         input_name = getattr(self, input_name)
         self.assertTrue(input_name in out_dict)
@@ -1712,8 +1714,8 @@ def test_apply_chat_template_video_frame_sampling(self):
             add_generation_prompt=True,
             tokenize=True,
             return_dict=True,
-            num_frames=num_frames,
             return_tensors="pt",
+            processor_kwargs={"num_frames": num_frames},
         )
         self.assertTrue(self.videos_input_name in out_dict_with_video)
         self.assertEqual(len(out_dict_with_video[self.videos_input_name]), 1)
@@ -1726,8 +1728,8 @@ def test_apply_chat_template_video_frame_sampling(self):
             add_generation_prompt=True,
             tokenize=True,
             return_dict=True,
-            fps=fps,
             return_tensors="pt",
+            processor_kwargs={"fps": fps},
         )
         self.assertTrue(self.videos_input_name in out_dict_with_video)
         self.assertEqual(len(out_dict_with_video[self.videos_input_name]), 1)
@@ -1741,9 +1743,11 @@ def test_apply_chat_template_video_frame_sampling(self):
             add_generation_prompt=True,
             tokenize=True,
             return_dict=True,
-            do_sample_frames=False,
-            fps=fps,
-            return_tensors="pt",
+            processor_kwargs={
+                "do_sample_frames": False,
+                "fps": fps,
+                "return_tensors": "pt",
+            },
         )
         self.assertTrue(self.videos_input_name in out_dict_with_video)
         self.assertEqual(len(out_dict_with_video[self.videos_input_name]), 1)
@@ -1756,8 +1760,7 @@ def test_apply_chat_template_video_frame_sampling(self):
                 add_generation_prompt=True,
                 tokenize=True,
                 return_dict=True,
-                fps=fps,
-                num_frames=num_frames,
+                processor_kwargs={"fps": fps, "num_frames": num_frames},
             )

         # Load without any arg should load the whole video
@@ -1802,7 +1805,7 @@ def test_apply_chat_template_video_frame_sampling(self):
                 add_generation_prompt=True,
                 tokenize=True,
                 return_dict=True,
-                do_sample_frames=True,
+                processor_kwargs={"do_sample_frames": True},
             )

     @require_librosa

PATCH

echo "Patch applied successfully."
