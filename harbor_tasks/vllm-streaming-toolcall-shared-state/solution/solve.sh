#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

TARGET="vllm/entrypoints/openai/chat_completion/serving.py"

# Idempotency check: if the list comprehension fix is already present, skip
if grep -q 'all_previous_token_ids = \[.*for _ in range' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/entrypoints/openai/chat_completion/serving.py b/vllm/entrypoints/openai/chat_completion/serving.py
index 493c26d3aed9..a426836afd35 100644
--- a/vllm/entrypoints/openai/chat_completion/serving.py
+++ b/vllm/entrypoints/openai/chat_completion/serving.py
@@ -548,7 +548,7 @@ async def chat_completion_stream_generator(
         # all_previous_token_ids will not be used twice in the same iteration.
         if tool_choice_auto or reasoning_parser:
             # These are only required in "auto" tool choice case
-            all_previous_token_ids = [[]] * num_choices
+            all_previous_token_ids = [[] for _ in range(num_choices)]
             # For reasoning parser and tool call all enabled
             added_content_delta_arr = [False] * num_choices
             reasoning_end_arr = [False] * num_choices
@@ -566,7 +566,8 @@ async def chat_completion_stream_generator(

                 tool_parsers: list[ToolParser | None] = [
                     self.tool_parser(tokenizer, request.tools)
-                ] * num_choices
+                    for _ in range(num_choices)
+                ]
             else:
                 tool_parsers = [None] * num_choices
         except Exception as e:

PATCH

echo "Patch applied successfully."
