#!/usr/bin/env bash
set -euo pipefail

FILE="tests/models/language/pooling/test_splade_sparse_pooler.py"

# Idempotency: check if already fixed
if grep -q "from vllm.v1.pool.metadata import PoolingMetadata" "$FILE" 2>/dev/null; then
    echo "Already patched."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tests/models/language/pooling/test_splade_sparse_pooler.py b/tests/models/language/pooling/test_splade_sparse_pooler.py
index af4fd764ef53..38a90d07abeb 100644
--- a/tests/models/language/pooling/test_splade_sparse_pooler.py
+++ b/tests/models/language/pooling/test_splade_sparse_pooler.py
@@ -1,8 +1,6 @@
 # SPDX-License-Identifier: Apache-2.0
 # SPDX-FileCopyrightText: Copyright contributors to the vLLM project

-import types
-
 import pytest
 import torch
 import torch.nn as nn
@@ -11,6 +9,8 @@
     BertMLMHead,
     SPLADESparsePooler,
 )
+from vllm.pooling_params import PoolingParams
+from vllm.v1.pool.metadata import PoolingMetadata, PoolingStates

 # ---------------------------------------------------------------------
 # Functional test: SPLADE formula correctness (no HF download needed)
@@ -38,8 +38,12 @@ def test_splade_pooler_matches_reference_formula(B, T, H, V):
         ],
         dtype=torch.long,
     )
-    meta = types.SimpleNamespace(
-        prompt_lens=prompt_lens_tenser, prompt_token_ids=token_ids
+    meta = PoolingMetadata(
+        prompt_lens=prompt_lens_tenser,
+        prompt_token_ids=token_ids,
+        prompt_token_ids_cpu=token_ids,
+        pooling_params=[PoolingParams(task="embed")] * B,
+        pooling_states=[PoolingStates() for _ in range(B)],
     )

     # MLM head (prefer BertMLMHead, fallback to Linear if unavailable)

PATCH

echo "Patch applied successfully."
