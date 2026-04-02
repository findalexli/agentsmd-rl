#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Idempotency check: skip if already applied
if grep -q 'resolve_messages' src/prime_rl/trainer/sft/data.py 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/docs/entrypoints.md b/docs/entrypoints.md
index 118300b3bb..d79a82faed 100644
--- a/docs/entrypoints.md
+++ b/docs/entrypoints.md
@@ -50,7 +50,7 @@ For more details on multi-node deployment options, see the [deployment](deployme

 We provide a fairly straight-forward SFT trainer which is capable of fine-tuning any conversational model on multi-turn conversation with tool calling. It shares a lot of components with the RL trainer, such as the modeling code, parallelism techniques, checkpoint format, logger, etc. which ensures a seemless post-training workflow.

-To start an SFT training, you need to prepare a dataset in [prompt-completion format](https://huggingface.co/docs/trl/en/dataset_formats#prompt-completion) (we do not support any other format). Single-turn fine-tuning should be compatible with the chat templates of most models. However, to properly handle loss masking, we require that the tokenizer's chat template satisfies a prefix property: the tokenization of any conversation prefix must be a prefix of the tokenization of the full conversation. For instance, tokenizing message 1 should yield a token sequence that forms a prefix of tokenizing messages 1 and 2, which in turn should be a prefix of tokenizing messages 1, 2, 3, and so forth. An example of a chat template that *does not* satisfy this property is Qwen3's chat template, as it strips away past think sections.
+To start an SFT training, you need to prepare a conversational dataset in either [prompt-completion format](https://huggingface.co/docs/trl/en/dataset_formats#prompt-completion) or raw `messages` format. If `messages` is provided, the trainer interprets the full conversation as a single sample with an empty prompt and applies role-based loss masking across the whole chat. If both `messages` and `prompt` / `completion` are present, `messages` takes precedence. Single-turn fine-tuning should be compatible with the chat templates of most models. However, to properly handle loss masking, we require that the tokenizer's chat template satisfies a prefix property: the tokenization of any conversation prefix must be a prefix of the tokenization of the full conversation. For instance, tokenizing message 1 should yield a token sequence that forms a prefix of tokenizing messages 1 and 2, which in turn should be a prefix of tokenizing messages 1, 2, 3, and so forth. An example of a chat template that *does not* satisfy this property is Qwen3's chat template, as it strips away past think sections.

 On a single GPU, start the training with the `sft` entrypoint

diff --git a/src/prime_rl/trainer/sft/data.py b/src/prime_rl/trainer/sft/data.py
index 41bd118099..34ad868df2 100644
--- a/src/prime_rl/trainer/sft/data.py
+++ b/src/prime_rl/trainer/sft/data.py
@@ -14,7 +14,12 @@

 from prime_rl.configs.sft import DataConfig, LossMaskConfig, SFTDataConfig
 from prime_rl.trainer.world import get_world
-from prime_rl.utils.chat_template import build_incremental_token_mask, deserialize_tool_calls, strip_message_content
+from prime_rl.utils.chat_template import (
+    build_incremental_token_mask,
+    deserialize_tool_calls,
+    normalize_messages,
+    strip_message_content,
+)
 from prime_rl.utils.logger import get_logger

 STACKING_DATASET_BUCKET_TIMEOUT = 10
@@ -108,7 +113,7 @@ def __iter__(self):


 class SFTDataset(StatefulIterableDataset):
-    """A dataset wrapping a HF SFT dataset with prompt + completion format."""
+    """A dataset wrapping a HF SFT dataset with prompt/completion or raw messages format."""

     def __init__(
         self,
@@ -157,19 +162,30 @@ def _process(self, example: dict) -> dict | None:
         if self.tokenizer is None:
             return example

-        # Assert that the example has a 'prompt' and 'completion' column
-        if "prompt" not in example or "completion" not in example:
-            raise ValueError("All examples in the dataset must have a 'prompt' and 'completion' column for SFT")
+        def resolve_messages(example: dict) -> list[dict]:
+            # `messages` takes precedence over explicit split fields and is interpreted
+            # as a whole-chat training sample with an empty prompt.
+            if "messages" in example:
+                messages = normalize_messages(example["messages"], default_role="assistant")
+            elif "prompt" in example and "completion" in example:
+                messages = normalize_messages(example["prompt"], default_role="user") + normalize_messages(
+                    example["completion"], default_role="assistant"
+                )
+            else:
+                raise ValueError(
+                    "All examples in the dataset must have either a 'messages' column "
+                    "or both 'prompt' and 'completion' columns for SFT"
+                )
+
+            # Deserialize tool call arguments from message list, if present - assumes OAI format
+            # Reference: https://platform.openai.com/docs/guides/function-calling#handling-function-calls
+            messages = deserialize_tool_calls(messages)

-        # Deserialize tool call arguments from message list, if present - assumes OAI format
-        # Reference: https://platform.openai.com/docs/guides/function-calling#handling-function-calls
-        prompt = deserialize_tool_calls(example["prompt"])
-        completion = deserialize_tool_calls(example["completion"])
+            # Strip content from all messages so that incremental tokenization works
+            # NOTE: This has the side effect that we do never train on leading or trailing whitespace
+            return strip_message_content(messages)

-        # Strip content from all messages so that incremental tokenization works
-        # NOTE: This has the side effect that we do never train on leading or trailing whitespace
-        prompt = strip_message_content(prompt)
-        completion = strip_message_content(completion)
+        messages = resolve_messages(example)

         # Parse available tools, if present - assumes OAI format
         # Reference: https://platform.openai.com/docs/guides/function-calling#function-tool-example
@@ -191,7 +207,7 @@ def should_mask(message: dict) -> bool:

         input_ids, loss_mask = build_incremental_token_mask(
             self.tokenizer,
-            prompt + completion,
+            messages,
             role_to_mask=should_mask,
             tools=tools,
             chat_template_kwargs=example.get("chat_template_kwargs", {}),
diff --git a/tests/unit/train/sft/test_sft_dataset.py b/tests/unit/train/sft/test_sft_dataset.py
index 0bd5c34a03..b8465e59d7 100644
--- a/tests/unit/train/sft/test_sft_dataset.py
+++ b/tests/unit/train/sft/test_sft_dataset.py
@@ -21,7 +21,7 @@ def test_init_sft_dataset(build_dummy_dataset):


 def test_raise_error_if_no_prompt_and_completion(build_dummy_dataset):
-    """Tests that an error is raised if no prompt and completion are provided but a tokenizer is provided."""
+    """Tests that an error is raised if no supported SFT message fields are provided."""
     dataset = build_dummy_dataset("a", 1)
     tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
     sft_dataset = SFTDataset(dataset, tokenizer=tokenizer)
@@ -260,3 +260,55 @@ def test_multiturn_loss_mask_with_tools():
     dataset = SFTDataset(dataset, tokenizer=tokenizer, max_examples=1)
     sample = next(iter(dataset))
     print_sample(sample["input_ids"], sample["loss_mask"], tokenizer)
+
+
+def test_messages_rows_are_equivalent_to_empty_prompt_completion():
+    messages = [
+        {"role": "system", "content": "You are a helpful assistant with access to tools."},
+        {"role": "user", "content": "What's the weather in San Francisco?"},
+        {
+            "role": "assistant",
+            "content": None,
+            "tool_calls": [
+                {
+                    "id": "call_1",
+                    "type": "function",
+                    "function": {"name": "get_weather", "arguments": '{"location": "San Francisco, CA"}'},
+                }
+            ],
+        },
+        {"role": "tool", "content": '{"temperature": 65, "condition": "Sunny"}', "tool_call_id": "call_1"},
+        {"role": "assistant", "content": "It is 65F and sunny in San Francisco."},
+    ]
+
+    tokenizer = AutoTokenizer.from_pretrained("PrimeIntellect/Qwen3-0.6B")
+    messages_dataset = SFTDataset(Dataset.from_list([{"messages": messages}]), tokenizer=tokenizer, max_examples=1)
+    split_dataset = SFTDataset(
+        Dataset.from_list([{"prompt": [], "completion": messages}]),
+        tokenizer=tokenizer,
+        max_examples=1,
+    )
+
+    assert next(iter(messages_dataset)) == next(iter(split_dataset))
+
+
+def test_messages_take_precedence_over_prompt_and_completion():
+    tokenizer = AutoTokenizer.from_pretrained("PrimeIntellect/Qwen3-0.6B")
+    row = {
+        "messages": [
+            {"role": "system", "content": "System from messages"},
+            {"role": "user", "content": "Prompt from messages"},
+            {"role": "assistant", "content": "Completion from messages"},
+        ],
+        "prompt": [{"role": "user", "content": "Ignored prompt"}],
+        "completion": [{"role": "assistant", "content": "Ignored completion"}],
+    }
+
+    messages_dataset = SFTDataset(Dataset.from_list([row]), tokenizer=tokenizer, max_examples=1)
+    expected_dataset = SFTDataset(
+        Dataset.from_list([{"prompt": [], "completion": row["messages"]}]),
+        tokenizer=tokenizer,
+        max_examples=1,
+    )
+
+    assert next(iter(messages_dataset)) == next(iter(expected_dataset))

PATCH

echo "Patch applied successfully"
