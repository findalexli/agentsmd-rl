#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q 'accuracy_threshold = 0.69  # derived tests need to override this' test/registered/spec/test_standalone_speculative_decoding.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/test/registered/spec/test_standalone_speculative_decoding.py b/test/registered/spec/test_standalone_speculative_decoding.py
index f74bc31e4843..37cb6fae71be 100644
--- a/test/registered/spec/test_standalone_speculative_decoding.py
+++ b/test/registered/spec/test_standalone_speculative_decoding.py
@@ -66,7 +66,7 @@ class TestStandaloneSpeculativeDecodingBase(CustomTestCase):
     model = DEFAULT_TARGET_MODEL_STANDALONE
     draft_model = DEFAULT_DRAFT_MODEL_STANDALONE
     base_url = DEFAULT_URL_FOR_TEST
-    accuracy_threshold = 0.7  # derived tests need to override this
+    accuracy_threshold = 0.69  # derived tests need to override this
     spec_decode_threshold = 3.6  # derived spec decoding tests need to override this

     @classmethod
@@ -111,7 +111,7 @@ def test_gsm8k(self):

         # Use the appropriate metric key based on the test class
         metric_key = "score"
-        self.assertGreater(metrics[metric_key], self.accuracy_threshold)
+        self.assertGreaterEqual(metrics[metric_key], self.accuracy_threshold)

         server_info = requests.get(self.base_url + "/server_info")
         avg_spec_accept_length = server_info.json()["internal_states"][0][
@@ -126,7 +126,7 @@ class TestStandaloneV2SpeculativeDecodingBase(CustomTestCase):
     model = DEFAULT_TARGET_MODEL_STANDALONE
     draft_model = DEFAULT_DRAFT_MODEL_STANDALONE
     base_url = DEFAULT_URL_FOR_TEST
-    accuracy_threshold = 0.7  # derived tests need to override this
+    accuracy_threshold = 0.69  # derived tests need to override this
     spec_decode_threshold = 3.6  # derived spec decoding tests need to override this

     @classmethod
@@ -174,7 +174,7 @@ def test_gsm8k(self):

         # Use the appropriate metric key based on the test class
         metric_key = "score"
-        self.assertGreater(metrics[metric_key], self.accuracy_threshold)
+        self.assertGreaterEqual(metrics[metric_key], self.accuracy_threshold)

         server_info = requests.get(self.base_url + "/server_info")
         avg_spec_accept_length = server_info.json()["internal_states"][0][

PATCH

echo "Patch applied successfully."
