#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotent: skip if already applied
if grep -q 'STRING_DELIM fragments' vllm/tool_parsers/gemma4_tool_parser.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/tool_parsers/gemma4_tool_parser.py b/vllm/tool_parsers/gemma4_tool_parser.py
index 3d0e4e7c4ab0..406ba9e70205 100644
--- a/vllm/tool_parsers/gemma4_tool_parser.py
+++ b/vllm/tool_parsers/gemma4_tool_parser.py
@@ -675,10 +675,11 @@ def _emit_argument_diff(self, raw_args_str: str) -> DeltaMessage | None:
         current_args_json = json.dumps(current_args, ensure_ascii=False)

         # Withhold trailing closing characters that may shift as more
-        # tokens arrive. Strip trailing '}', '"', and ']' sequences
-        # to get the "safe prefix".
+        # tokens arrive. Strip trailing '}', '"', ']' and partial
+        # STRING_DELIM fragments ('<', '|', '\\', '>') to get the
+        # "safe prefix".
         safe_json = current_args_json
-        while safe_json and safe_json[-1] in ("}", '"', "]"):
+        while safe_json and safe_json[-1] in ("}", '"', "]", "<", "|", "\\", ">"):
             safe_json = safe_json[:-1]

         prev_streamed = self.streamed_args_for_tool[self.current_tool_id]

PATCH

echo "Patch applied successfully."
