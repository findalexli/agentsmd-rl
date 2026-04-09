#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotent: skip if already applied
if grep -qP '^\s{16}models = make_mcore_model\(' areal/engine/megatron_engine.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/engine/megatron_engine.py b/areal/engine/megatron_engine.py
index d7a219a56..54bdb8a8b 100644
--- a/areal/engine/megatron_engine.py
+++ b/areal/engine/megatron_engine.py
@@ -262,15 +262,15 @@ def initialize(self, addr: str | None, ft_spec: FinetuneSpec, *args, **kwargs):
             self._check_and_apply_fp8_config()
             self._validate_fp8_consistency()

-        with self.device:
-            models = make_mcore_model(
-                hf_config=self.hf_config,
-                tf_config=self.tf_config,
-                mcore_config=self.mcore_config,
-                bridge=self.bridge,
-                bridge_type=self.bridge_cls,
-                is_critic=self.config.is_critic,
-            )
+            with self.device:
+                models = make_mcore_model(
+                    hf_config=self.hf_config,
+                    tf_config=self.tf_config,
+                    mcore_config=self.mcore_config,
+                    bridge=self.bridge,
+                    bridge_type=self.bridge_cls,
+                    is_critic=self.config.is_critic,
+                )

         self.model = _MegatronModelList(models)

PATCH

echo "Patch applied successfully."
