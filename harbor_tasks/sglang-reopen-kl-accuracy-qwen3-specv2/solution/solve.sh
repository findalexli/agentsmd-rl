#!/usr/bin/env bash
set -e

cd /workspace/sglang

# Idempotency check: check for distinctive line in TestQwen3NextMTPV2 class
# The class after fix has: class TestQwen3NextMTPV2(GSM8KMixin, KLDivergenceMixin, DefaultServerBase):
# The class before fix has: class TestQwen3NextMTPV2(GSM8KMixin, DefaultServerBase):
if grep -q "class TestQwen3NextMTPV2(GSM8KMixin, KLDivergenceMixin, DefaultServerBase)" test/registered/4-gpu-models/test_qwen3_next_models_mtp.py 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/test/registered/4-gpu-models/test_qwen3_next_models_mtp.py b/test/registered/4-gpu-models/test_qwen3_next_models_mtp.py
index 0ac3c5f62ef8..649cddf035d6 100644
--- a/test/registered/4-gpu-models/test_qwen3_next_models_mtp.py
+++ b/test/registered/4-gpu-models/test_qwen3_next_models_mtp.py
@@ -68,11 +68,10 @@ class TestQwen3NextMTPTopk(
     ]


-# TODO(hzh): After merging the PR that fixes specv2 to correctly return log probs,
-# add KLDivergenceMixin back. https://github.com/sgl-project/sglang/pull/18645
-class TestQwen3NextMTPV2(GSM8KMixin, DefaultServerBase):
+class TestQwen3NextMTPV2(GSM8KMixin, KLDivergenceMixin, DefaultServerBase):
     model = QWEN3_NEXT_MODEL
     gsm8k_accuracy_thres = 0.93
+    kl_div_thres = 0.0025
     other_args = [
         "--trust-remote-code",
         "--speculative-algorithm",
PATCH

echo "Patch applied successfully"
