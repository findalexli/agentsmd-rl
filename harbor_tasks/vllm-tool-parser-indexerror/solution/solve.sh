#!/usr/bin/env bash
set -euo pipefail
cd /workspace/vllm

# Idempotent: skip if already applied (check for the "should_check =" variable)
grep -q 'should_check = ' vllm/entrypoints/openai/chat_completion/serving.py && exit 0

git apply - <<'PATCH'
diff --git a/vllm/entrypoints/openai/chat_completion/serving.py b/vllm/entrypoints/openai/chat_completion/serving.py
index 62a0192e7b7a..6b39bc5ec404 100644
--- a/vllm/entrypoints/openai/chat_completion/serving.py
+++ b/vllm/entrypoints/openai/chat_completion/serving.py
@@ -1089,6 +1089,7 @@ async def chat_completion_stream_generator(
                         #   any tokens that were generated but previously
                         #   matched by partial json parsing
                         # only happens if we are NOT using structured outputs
+                        index = 0
                         auto_tools_called = False
                         if tool_parser:
                             auto_tools_called = len(tool_parser.prev_tool_call_arr) > 0
@@ -1097,15 +1098,14 @@ async def chat_completion_stream_generator(
                                 if auto_tools_called
                                 else 0
                             )
-                        else:
-                            index = 0
-
-                        if (
+                        should_check = (
                             self._should_check_for_unstreamed_tool_arg_tokens(
                                 delta_message, output
                             )
-                            and tool_parser
-                        ):
+                        )
+                        # only check if there are any tool calls
+                        # detected by partial parsing
+                        if should_check and tool_parser and auto_tools_called:
                             latest_delta_len = 0
                             if (
                                 isinstance(

PATCH
