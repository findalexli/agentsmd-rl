#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency: skip if already applied
if grep -q 'gen_multi_turn_loss_mask_qwen3_5' slime/utils/mask_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/rollout/sft_rollout.py b/slime/rollout/sft_rollout.py
index 6b914a964e..4407463d23 100644
--- a/slime/rollout/sft_rollout.py
+++ b/slime/rollout/sft_rollout.py
@@ -47,6 +47,10 @@ def generate_rollout(args, rollout_id, data_buffer, evaluation=False):
         tools = sample.metadata.get("tools", None)

         token_ids, loss_mask = MASK_GENERATOR.get_loss_mask(messages, tools=tools)
+        if len(token_ids) != len(loss_mask):
+            raise ValueError(
+                f"SFT rollout produced mismatched token_ids/loss_mask lengths: {len(token_ids)=}, {len(loss_mask)=}"
+            )

         response_length = MASK_GENERATOR.get_response_lengths([loss_mask])[0]

diff --git a/slime/utils/arguments.py b/slime/utils/arguments.py
index 1d4fa24d33..daeb1180d6 100644
--- a/slime/utils/arguments.py
+++ b/slime/utils/arguments.py
@@ -1270,7 +1270,7 @@ def add_rollout_buffer_arguments(parser):
                 "--loss-mask-type",
                 type=str,
                 default="qwen",
-                choices=["qwen", "qwen3", "distill_qwen"],
+                choices=["qwen", "qwen3", "qwen3_5", "distill_qwen"],
                 help="Loss mask type",
             )
             parser.add_argument(
diff --git a/slime/utils/mask_utils.py b/slime/utils/mask_utils.py
index 1806c79008..efe5e159f1 100644
--- a/slime/utils/mask_utils.py
+++ b/slime/utils/mask_utils.py
@@ -9,8 +9,11 @@ def get_response_lengths(loss_masks: list[list[int]]) -> list[int]:
 class MultiTurnLossMaskGenerator:
     def __init__(self, tokenizer: AutoTokenizer, tokenizer_type: str = "qwen"):
         self.tokenizer = tokenizer
-        self.system_message_length, self.gen_token_length = self.get_system_message_length()
         self.tokenizer_type = tokenizer_type
+        self.system_message_length = 0
+        self.gen_token_length = 0
+        if self.tokenizer_type in ("qwen", "qwen3"):
+            self.system_message_length, self.gen_token_length = self.get_system_message_length()

     def get_response_lengths(self, loss_masks: list[list[int]]) -> list[int]:
         return get_response_lengths(loss_masks)
@@ -121,6 +124,77 @@ def gen_multi_turn_loss_mask_qwen3(

         return all_token_ids, all_loss_masks

+    def gen_multi_turn_loss_mask_qwen3_5(
+        self, messages: list[dict], tools: list[dict] = None
+    ) -> tuple[list[int], list[int]]:
+        rendered_text = self.tokenizer.apply_chat_template(messages, tokenize=False, tools=tools, return_dict=False)
+        tokenized = self.tokenizer(rendered_text, add_special_tokens=False, return_offsets_mapping=True)
+        token_ids = tokenized["input_ids"]
+        offset_mapping = tokenized.get("offset_mapping")
+
+        if offset_mapping is None:
+            raise ValueError(
+                "Qwen3.5 loss mask generation requires a fast tokenizer " "with `return_offsets_mapping` support."
+            )
+
+        expected_token_ids = self.tokenizer.apply_chat_template(
+            messages, tokenize=True, tools=tools, return_dict=False
+        )
+        if token_ids != expected_token_ids:
+            raise ValueError(
+                "Qwen3.5 rendered text tokenization does not match "
+                "`apply_chat_template(..., tokenize=True)` output."
+            )
+
+        assistant_header = "<|im_start|>assistant\n"
+        think_prefix = "<think>\n"
+        end_marker = "<|im_end|>"
+
+        char_mask = [0] * len(rendered_text)
+        cursor = 0
+
+        for message in messages:
+            if message["role"] != "assistant":
+                continue
+
+            header_pos = rendered_text.find(assistant_header, cursor)
+            if header_pos < 0:
+                raise ValueError("Failed to locate assistant message in rendered Qwen3.5 chat template output.")
+
+            content_start = header_pos + len(assistant_header)
+            end_pos = rendered_text.find(end_marker, content_start)
+            if end_pos < 0:
+                raise ValueError("Failed to locate <|im_end|> for assistant message in rendered text.")
+
+            span_end = end_pos + len(end_marker)
+            if span_end < len(rendered_text) and rendered_text[span_end] == "\n":
+                span_end += 1
+            cursor = span_end
+
+            if message.get("step_loss_mask", 1) != 1:
+                continue
+
+            if rendered_text[content_start : content_start + len(think_prefix)] == think_prefix:
+                mask_start = content_start + len(think_prefix)
+            else:
+                mask_start = content_start
+
+            for pos in range(mask_start, span_end):
+                char_mask[pos] = 1
+
+        char_mask_prefix_sum = [0]
+        for value in char_mask:
+            char_mask_prefix_sum.append(char_mask_prefix_sum[-1] + value)
+
+        loss_mask = []
+        for start, end in offset_mapping:
+            if end <= start:
+                loss_mask.append(0)
+            else:
+                loss_mask.append(1 if char_mask_prefix_sum[end] - char_mask_prefix_sum[start] > 0 else 0)
+
+        return token_ids, loss_mask
+
     def gen_multi_turn_loss_mask_distill_qwen(
         self, messages: list[dict], tools: list[dict] = None
     ) -> tuple[list[int], list[int]]:
@@ -147,6 +221,8 @@ def get_loss_mask(self, messages: list[dict], tools: list[dict] = None) -> tuple
             return self.gen_multi_turn_loss_mask_qwen(messages, tools)
         elif self.tokenizer_type == "qwen3":
             return self.gen_multi_turn_loss_mask_qwen3(messages, tools)
+        elif self.tokenizer_type == "qwen3_5":
+            return self.gen_multi_turn_loss_mask_qwen3_5(messages, tools)
         elif self.tokenizer_type == "distill_qwen":
             return self.gen_multi_turn_loss_mask_distill_qwen(messages, tools)
         else:

PATCH

echo "Patch applied successfully."
