#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied (check for distinctive method in new file)
if grep -q 'def test_reasoning_tokens_thinking' python/sglang/test/kits/reasoning_tokens_kit.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/python/sglang/test/kits/reasoning_tokens_kit.py b/python/sglang/test/kits/reasoning_tokens_kit.py
new file mode 100644
index 000000000000..c3b02ad81c2c
--- /dev/null
+++ b/python/sglang/test/kits/reasoning_tokens_kit.py
@@ -0,0 +1,114 @@
+import json
+
+import requests
+
+from sglang.srt.parser.reasoning_parser import ReasoningParser
+from sglang.srt.utils.hf_transformers_utils import get_tokenizer
+
+
+class ReasoningTokenUsageMixin:
+    """Mixin for reasoning_tokens usage tests.
+
+    Required attributes on the test class:
+        model: str
+        base_url: str
+        reasoning_parser_name: str
+
+    Optional attributes:
+        api_key: str (if not set, no auth)
+
+    Call cls.init_reasoning_token_verifier() in setUpClass.
+    """
+
+    reasoning_parser_name = None
+
+    @classmethod
+    def init_reasoning_token_verifier(cls):
+        assert cls.reasoning_parser_name, "reasoning_parser_name must be set"
+        cls.tokenizer = get_tokenizer(cls.model)
+        parser = ReasoningParser(cls.reasoning_parser_name)
+        cls.think_end_token_id = cls.tokenizer.convert_tokens_to_ids(
+            parser.detector.think_end_token
+        )
+        assert cls.think_end_token_id is not None
+
+    def _reasoning_chat_request(self, enable_thinking, stream=False):
+        api_key = getattr(self, "api_key", None)
+        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
+        payload = {
+            "model": self.model,
+            "messages": [{"role": "user", "content": "What is 1+3?"}],
+            "max_tokens": 1024,
+            "chat_template_kwargs": {"enable_thinking": enable_thinking},
+        }
+        if stream:
+            payload["stream"] = True
+            payload["stream_options"] = {"include_usage": True}
+        return requests.post(
+            f"{self.base_url}/v1/chat/completions",
+            headers=headers,
+            json=payload,
+            stream=stream,
+        )
+
+    def _extract_streaming_usage(self, response):
+        usage = None
+        for line in response.iter_lines():
+            if not line:
+                continue
+            decoded = line.decode("utf-8")
+            if not decoded.startswith("data:") or decoded.startswith("data: [DONE]"):
+                continue
+            data = json.loads(decoded[len("data:") :].strip())
+            if data.get("usage"):
+                usage = data["usage"]
+        return usage
+
+    def test_reasoning_tokens_thinking(self):
+        resp = self._reasoning_chat_request(enable_thinking=True)
+        self.assertEqual(resp.status_code, 200, resp.text)
+        usage = resp.json()["usage"]
+        self.assertGreater(usage["reasoning_tokens"], 0)
+        self.assertLess(usage["reasoning_tokens"], usage["completion_tokens"])
+
+    def test_reasoning_tokens_non_thinking(self):
+        resp = self._reasoning_chat_request(enable_thinking=False)
+        self.assertEqual(resp.status_code, 200, resp.text)
+        self.assertEqual(resp.json()["usage"]["reasoning_tokens"], 0)
+
+    def test_reasoning_tokens_thinking_stream(self):
+        with self._reasoning_chat_request(enable_thinking=True, stream=True) as resp:
+            self.assertEqual(resp.status_code, 200, resp.text)
+            usage = self._extract_streaming_usage(resp)
+            self.assertIsNotNone(usage, "No usage in stream")
+            self.assertGreater(usage["reasoning_tokens"], 0)
+            self.assertLess(usage["reasoning_tokens"], usage["completion_tokens"])
+
+    def test_reasoning_tokens_non_thinking_stream(self):
+        with self._reasoning_chat_request(enable_thinking=False, stream=True) as resp:
+            self.assertEqual(resp.status_code, 200, resp.text)
+            usage = self._extract_streaming_usage(resp)
+            self.assertIsNotNone(usage, "No usage in stream")
+            self.assertEqual(usage["reasoning_tokens"], 0)
+
+    def test_reasoning_tokens_generate_exact_count(self):
+        api_key = getattr(self, "api_key", None)
+        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
+        messages = [{"role": "user", "content": "What is 1+3?"}]
+        prompt = self.tokenizer.apply_chat_template(
+            messages, add_generation_prompt=True, tokenize=False
+        )
+        resp = requests.post(
+            f"{self.base_url}/generate",
+            headers=headers,
+            json={
+                "text": prompt,
+                "sampling_params": {"max_new_tokens": 1024},
+                "require_reasoning": True,
+            },
+        )
+        self.assertEqual(resp.status_code, 200, resp.text)
+        data = resp.json()
+        reported = data["meta_info"]["reasoning_tokens"]
+        actual = data["output_ids"].index(self.think_end_token_id) + 1
+        self.assertEqual(reported, actual)
diff --git a/test/registered/4-gpu-models/test_qwen35_models.py b/test/registered/4-gpu-models/test_qwen35_models.py
index 562d201f21e6..233518f6d0ba 100644
--- a/test/registered/4-gpu-models/test_qwen35_models.py
+++ b/test/registered/4-gpu-models/test_qwen35_models.py
@@ -7,6 +7,7 @@
 from sglang.srt.utils import kill_process_tree
 from sglang.test.accuracy_test_runner import AccuracyTestParams
 from sglang.test.ci.ci_register import register_cuda_ci
+from sglang.test.kits.reasoning_tokens_kit import ReasoningTokenUsageMixin

 # This eval harness applies the chat_template, which is critical for qwen3.5
 # to get good accuracy on gsm8k
@@ -20,13 +21,13 @@
     popen_launch_server,
 )

-register_cuda_ci(est_time=1400, suite="stage-c-test-4-gpu-b200")
+register_cuda_ci(est_time=790, suite="stage-c-test-4-gpu-b200")

 QWEN35_FP4_MODEL = "nvidia/Qwen3.5-397B-A17B-NVFP4"
 ACC_THRESHOLDS = {QWEN35_FP4_MODEL: {"gsm8k": 0.95}}


-class TestQwen35FP4(unittest.TestCase):
+class TestQwen35FP4(CustomTestCase):
     def test_gsm8k(self):
         base_args = [
             "--tp-size",
@@ -82,11 +83,14 @@ def test_gsm8k(self):
         )


-class TestQwen35FP4MTP(CustomTestCase):
+class TestQwen35FP4MTP(ReasoningTokenUsageMixin, CustomTestCase):
+    reasoning_parser_name = "qwen3"
+
     @classmethod
     def setUpClass(cls):
         cls.model = QWEN35_FP4_MODEL
         cls.base_url = DEFAULT_URL_FOR_TEST
+        cls.init_reasoning_token_verifier()
         cls.process = popen_launch_server(
             cls.model,
             cls.base_url,
@@ -157,11 +161,14 @@ def test_gsm8k(self):
         self.assertGreater(avg_spec_accept_length, 3.3)


-class TestQwen35FP4MTPV2(CustomTestCase):
+class TestQwen35FP4MTPV2(ReasoningTokenUsageMixin, CustomTestCase):
+    reasoning_parser_name = "qwen3"
+
     @classmethod
     def setUpClass(cls):
         cls.model = QWEN35_FP4_MODEL
         cls.base_url = DEFAULT_URL_FOR_TEST
+        cls.init_reasoning_token_verifier()
         envs.SGLANG_ENABLE_SPEC_V2.set(True)
         cls.process = popen_launch_server(
             cls.model,
diff --git a/test/registered/openai_server/features/test_enable_thinking.py b/test/registered/openai_server/features/test_enable_thinking.py
index 6ee28866aa05..51ae25351bc8 100644
--- a/test/registered/openai_server/features/test_enable_thinking.py
+++ b/test/registered/openai_server/features/test_enable_thinking.py
@@ -13,6 +13,7 @@

 from sglang.srt.utils import kill_process_tree
 from sglang.test.ci.ci_register import register_amd_ci, register_cuda_ci
+from sglang.test.kits.reasoning_tokens_kit import ReasoningTokenUsageMixin
 from sglang.test.test_utils import (
     DEFAULT_ENABLE_THINKING_MODEL_NAME_FOR_TEST,
     DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
@@ -21,16 +22,19 @@
     popen_launch_server,
 )

-register_cuda_ci(est_time=103, suite="stage-b-test-1-gpu-large")
+register_cuda_ci(est_time=109, suite="stage-b-test-1-gpu-large")
 register_amd_ci(est_time=200, suite="stage-b-test-1-gpu-small-amd")


-class TestEnableThinking(CustomTestCase):
+class TestEnableThinking(ReasoningTokenUsageMixin, CustomTestCase):
+    reasoning_parser_name = "qwen3"
+
     @classmethod
     def setUpClass(cls):
         cls.model = DEFAULT_ENABLE_THINKING_MODEL_NAME_FOR_TEST
         cls.base_url = DEFAULT_URL_FOR_TEST
         cls.api_key = "sk-1234"
+        cls.init_reasoning_token_verifier()
         cls.process = popen_launch_server(
             cls.model,
             cls.base_url,
diff --git a/test/registered/openai_server/features/test_reasoning_usage_tokens.py b/test/registered/openai_server/features/test_reasoning_usage_tokens.py
deleted file mode 100644
index d53ef88c440e..000000000000
--- a/test/registered/openai_server/features/test_reasoning_usage_tokens.py
+++ /dev/null
@@ -1,180 +0,0 @@
-"""Usage:
-python3 -m unittest openai_server.features.test_reasoning_usage_tokens.TestNormalReasoningTokenUsage
-python3 -m unittest openai_server.features.test_reasoning_usage_tokens.TestSpecReasoningTokenUsage
-python3 -m unittest openai_server.features.test_reasoning_usage_tokens.TestSpecV2ReasoningTokenUsage
-"""
-
-import json
-import os
-import unittest
-
-import requests
-from openai import OpenAI
-
-from sglang.srt.parser.reasoning_parser import ReasoningParser
-from sglang.srt.utils import kill_process_tree
-from sglang.srt.utils.hf_transformers_utils import get_tokenizer
-from sglang.test.ci.ci_register import register_cuda_ci
-from sglang.test.test_utils import (
-    DEFAULT_REASONING_MODEL_NAME_FOR_TEST,
-    DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
-    DEFAULT_URL_FOR_TEST,
-    CustomTestCase,
-    popen_launch_server,
-)
-
-register_cuda_ci(est_time=90, suite="stage-b-test-1-gpu-large")
-
-
-def remove_prefix(text: str, prefix: str) -> str:
-    return text[len(prefix) :] if text.startswith(prefix) else text
-
-
-class ReasoningTokenUsageMixin:
-    model = ""
-    reasoning_parser_name = ""
-    extra_server_args = []
-    extra_env_vars = {}
-    max_new_tokens = 1024
-
-    @classmethod
-    def setUpClass(cls):
-        for k, v in cls.extra_env_vars.items():
-            os.environ[k] = v
-
-        assert cls.model
-        cls.base_url = DEFAULT_URL_FOR_TEST
-        cls.api_key = "sk-1234"
-
-        # get think_end_token_id
-        cls.tokenizer = get_tokenizer(cls.model)
-        reasoning_parser = ReasoningParser(cls.reasoning_parser_name)
-        cls.think_end_token_id = cls.tokenizer.convert_tokens_to_ids(
-            reasoning_parser.detector.think_end_token
-        )
-        assert (
-            cls.think_end_token_id
-        ), f"think_end_token_id for {cls.reasoning_parser_name} shouldn't be None"
-
-        cls.process = popen_launch_server(
-            cls.model,
-            cls.base_url,
-            timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
-            api_key=cls.api_key,
-            other_args=[
-                "--reasoning-parser",
-                cls.reasoning_parser_name,
-            ]
-            + cls.extra_server_args,
-        )
-        cls.client = OpenAI(base_url=f"{cls.base_url}/v1", api_key=cls.api_key)
-        cls.messages = [{"role": "user", "content": "What is 1+3?"}]
-
-    @classmethod
-    def tearDownClass(cls):
-        if hasattr(cls, "process"):
-            kill_process_tree(cls.process.pid)
-
-    def test_generate_api_non_streaming(self):
-        response = requests.post(
-            url=f"{self.base_url}/generate",
-            headers={"Authorization": f"Bearer {self.api_key}"},
-            json={
-                "text": self.tokenizer.apply_chat_template(
-                    self.messages, add_generation_prompt=True, tokenize=False
-                ),
-                "model": self.model,
-                "require_reasoning": True,
-                "sampling_params": {"max_new_tokens": self.max_new_tokens},
-            },
-        )
-        response.raise_for_status()
-        res_json = response.json()
-        report_reasoning_tokens = res_json["meta_info"]["reasoning_tokens"]
-        actual_reasoning_tokens = (
-            res_json["output_ids"].index(self.think_end_token_id) + 1
-        )
-        assert (
-            report_reasoning_tokens == actual_reasoning_tokens
-        ), f"Expected {actual_reasoning_tokens}, got {report_reasoning_tokens}"
-
-    def test_generate_api_streaming(self):
-        response = requests.post(
-            url=f"{self.base_url}/generate",
-            headers={"Authorization": f"Bearer {self.api_key}"},
-            json={
-                "text": self.tokenizer.apply_chat_template(
-                    self.messages, add_generation_prompt=True, tokenize=False
-                ),
-                "model": self.model,
-                "require_reasoning": True,
-                "sampling_params": {"max_new_tokens": 1024},
-                "stream": True,
-            },
-            stream=True,
-        )
-        response.raise_for_status()
-        for chunk in response.iter_lines():
-            if not chunk:
-                continue
-            decoded_str = remove_prefix(chunk.decode("utf-8"), "data: ")
-            if decoded_str != "[DONE]":
-                data = json.loads(decoded_str)
-                report_reasoning_tokens = data["meta_info"]["reasoning_tokens"]
-                if self.think_end_token_id in data["output_ids"]:
-                    actual_reasoning_tokens = (
-                        data["output_ids"].index(self.think_end_token_id) + 1
-                    )
-                else:
-                    actual_reasoning_tokens = len(data["output_ids"])
-                assert report_reasoning_tokens == actual_reasoning_tokens
-
-    def test_chat_api_non_streaming(self):
-        response = self.client.chat.completions.create(
-            model=self.model, messages=self.messages, max_tokens=1024
-        )
-        assert response.usage is not None
-        assert response.usage.reasoning_tokens > 0
-
-    def test_chat_api_streaming(self):
-        response = self.client.chat.completions.create(
-            model=self.model,
-            messages=self.messages,
-            max_tokens=1024,
-            stream=True,
-            stream_options={"include_usage": True, "continuous_usage_stats": True},
-        )
-        for chunk in response:
-            if chunk.usage:
-                assert chunk.usage.reasoning_tokens > 0
-
-
-class TestNormalReasoningTokenUsage(ReasoningTokenUsageMixin, CustomTestCase):
-    model = DEFAULT_REASONING_MODEL_NAME_FOR_TEST
-    reasoning_parser_name = "deepseek-r1"
-    extra_server_args = ["--cuda-graph-max-bs", "2"]
-
-
-class TestSpecReasoningTokenUsage(ReasoningTokenUsageMixin, CustomTestCase):
-    model = "Qwen/Qwen3-30B-A3B"  # select this model due to its suitable eagle model
-    reasoning_parser_name = "qwen3"
-    extra_env_vars = {"SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN": "1"}
-    extra_server_args = [
-        "--speculative-algorithm",
-        "EAGLE3",
-        "--speculative-draft-model-path",
-        "nex-agi/SGLANG-EAGLE3-Qwen3-30B-A3B-Nex-N1",
-        "--cuda-graph-max-bs",
-        "2",
-    ]
-
-
-class TestSpecV2ReasoningTokenUsage(TestSpecReasoningTokenUsage):
-    extra_env_vars = {
-        "SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN": "1",
-        "SGLANG_ENABLE_SPEC_V2": "1",
-    }
-
-
-if __name__ == "__main__":
-    unittest.main()

PATCH

echo "Patch applied successfully."
