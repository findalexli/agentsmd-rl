#!/usr/bin/env bash
set -euo pipefail

# Check if already applied (granite config already accepts int for embedding_multiplier)
if grep -q 'embedding_multiplier: float | int' src/transformers/models/granite/configuration_granite.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/granite/configuration_granite.py b/src/transformers/models/granite/configuration_granite.py
index 85b20ad2e8f2..e026cbbe5ff3 100644
--- a/src/transformers/models/granite/configuration_granite.py
+++ b/src/transformers/models/granite/configuration_granite.py
@@ -80,10 +80,10 @@ class GraniteConfig(PreTrainedConfig):
     attention_bias: bool = False
     attention_dropout: float | int = 0.0
     mlp_bias: bool = False
-    embedding_multiplier: float = 1.0
-    logits_scaling: float = 1.0
-    residual_multiplier: float = 1.0
-    attention_multiplier: float = 1.0
+    embedding_multiplier: float | int = 1.0
+    logits_scaling: float | int = 1.0
+    residual_multiplier: float | int = 1.0
+    attention_multiplier: float | int = 1.0

     def __post_init__(self, **kwargs):
         if self.num_key_value_heads is None:
diff --git a/src/transformers/models/granitemoe/configuration_granitemoe.py b/src/transformers/models/granitemoe/configuration_granitemoe.py
index 836b818bb989..55f6fea129d0 100644
--- a/src/transformers/models/granitemoe/configuration_granitemoe.py
+++ b/src/transformers/models/granitemoe/configuration_granitemoe.py
@@ -64,10 +64,10 @@ class GraniteMoeConfig(PreTrainedConfig):
     rope_parameters: RopeParameters | dict | None = None
     attention_bias: bool = False
     attention_dropout: float | int | None = 0.0
-    embedding_multiplier: float | None = 1.0
-    logits_scaling: float | None = 1.0
-    residual_multiplier: float | None = 1.0
-    attention_multiplier: float | None = 1.0
+    embedding_multiplier: float | int | None = 1.0
+    logits_scaling: float | int | None = 1.0
+    residual_multiplier: float | int | None = 1.0
+    attention_multiplier: float | int | None = 1.0
     num_local_experts: int | None = 8
     num_experts_per_tok: int | None = 2
     output_router_logits: bool | None = False
diff --git a/src/transformers/models/granitemoeshared/configuration_granitemoeshared.py b/src/transformers/models/granitemoeshared/configuration_granitemoeshared.py
index 4d1b0ff85f94..9d782c089e36 100644
--- a/src/transformers/models/granitemoeshared/configuration_granitemoeshared.py
+++ b/src/transformers/models/granitemoeshared/configuration_granitemoeshared.py
@@ -75,10 +75,10 @@ class GraniteMoeSharedConfig(PreTrainedConfig):
     rope_parameters: RopeParameters | dict | None = None
     attention_bias: bool = False
     attention_dropout: float | int | None = 0.0
-    embedding_multiplier: float | None = 1.0
-    logits_scaling: float | None = 1.0
-    residual_multiplier: float | None = 1.0
-    attention_multiplier: float | None = 1.0
+    embedding_multiplier: float | int | None = 1.0
+    logits_scaling: float | int | None = 1.0
+    residual_multiplier: float | int | None = 1.0
+    attention_multiplier: float | int | None = 1.0
     num_local_experts: int | None = 8
     num_experts_per_tok: int | None = 2
     output_router_logits: bool | None = False

PATCH

echo "Patch applied successfully."
