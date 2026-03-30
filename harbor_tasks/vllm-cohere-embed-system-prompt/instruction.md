# Fix Cohere v2/embed to apply task instruction as system prompt

## Bug Description

In `vllm/entrypoints/pooling/embed/io_processor.py`, the `_pre_process_cohere_online` method and the `_mixed_input_to_messages` helper have two issues with how task instructions (like "query: " or "search_document: ") are applied:

1. **Task instructions prepended to text content instead of used as system prompt**: The `_mixed_input_to_messages` method prepends the `task_prefix` to each text part's content. This is incorrect when a chat template is available -- the task instruction should be rendered as a system prompt message, not prepended to the user text. This affects embedding quality because the model expects the task instruction as a separate system-level instruction.

2. **Text-only inputs always go through the completion path**: When `request.texts` is provided (no images or mixed inputs), the code always uses `_preprocess_completion_online` with prepended task instructions. When a chat template is available, text inputs with task instructions should instead go through `_batch_render_chat` with the task instruction as a system prompt.

## Expected Fix

1. Modify `_mixed_input_to_messages` so that when `task_prefix` is given, it is added as a system prompt message (role="system") instead of being prepended to each text content.

2. Modify `_pre_process_cohere_online` to:
   - When processing text-only inputs (`request.texts`): check if a chat template is available. If so, wrap each text as a `CohereEmbedInput` and use `_batch_render_chat`. If not (or no task prefix), fall back to the completion path.
   - Add a `_has_chat_template()` helper method.
   - Add a `_preprocess_cohere_text_completion()` helper to reduce duplication.

## Files to Modify

- `vllm/entrypoints/pooling/embed/io_processor.py` -- main logic changes
