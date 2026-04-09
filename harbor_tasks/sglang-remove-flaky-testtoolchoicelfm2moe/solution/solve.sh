#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied (check if TestToolChoiceLfm2Moe class exists)
if ! grep -q 'class TestToolChoiceLfm2Moe' test/registered/openai_server/function_call/test_tool_choice.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch - remove the TestToolChoiceLfm2Moe class
git apply - <<'PATCH'
--- a/test/registered/openai_server/function_call/test_tool_choice.py
+++ b/test/registered/openai_server/function_call/test_tool_choice.py
@@ -888,33 +888,5 @@ def setUpClass(cls):
         cls.tokenizer = get_tokenizer(cls.model)


-class TestToolChoiceLfm2Moe(TestToolChoiceLlama32):
-    """Test tool_choice functionality with LiquidAI LFM2-MoE model"""
-
-    @classmethod
-    def setUpClass(cls):
-        cls.flaky_tests = {
-            "test_multi_tool_scenario_auto",
-            "test_multi_tool_scenario_required",
-        }
-
-        cls.model = "LiquidAI/LFM2-8B-A1B"
-        cls.base_url = DEFAULT_URL_FOR_TEST
-        cls.api_key = "sk-123456"
-
-        cls.process = popen_launch_server(
-            cls.model,
-            cls.base_url,
-            timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
-            api_key=cls.api_key,
-            other_args=[
-                "--tool-call-parser",
-                "lfm2",
-            ],
-        )
-        cls.base_url += "/v1"
-        cls.tokenizer = get_tokenizer(cls.model)
-
-
 if __name__ == "__main__":
     unittest.main()

PATCH

echo "Patch applied successfully."
