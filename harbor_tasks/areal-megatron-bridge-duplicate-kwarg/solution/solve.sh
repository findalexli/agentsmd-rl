#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotency: check if the duplicate kwarg has already been removed
# The buggy code has two trust_remote_code=True on separate lines in from_hf_pretrained call
DUPES=$(grep -c 'trust_remote_code=True' areal/engine/megatron_engine.py || true)
if [ "$DUPES" -le 2 ]; then
    echo "Fix already applied (trust_remote_code appears $DUPES times, expected <=2)."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/engine/megatron_engine.py b/areal/engine/megatron_engine.py
index b972d240a..d7a219a56 100644
--- a/areal/engine/megatron_engine.py
+++ b/areal/engine/megatron_engine.py
@@ -353,7 +353,9 @@ def initialize(self, addr: str | None, ft_spec: FinetuneSpec, *args, **kwargs):

     def _build_hf_mcore_bridge(self):
         if self.bridge_cls == "mbridge":
-            self.bridge = mbridge.AutoBridge.from_pretrained(self.config.path, trust_remote_code=True)
+            self.bridge = mbridge.AutoBridge.from_pretrained(
+                self.config.path, trust_remote_code=True
+            )
             self.bridge.dtype = self.dtype
             if self.config.gradient_checkpointing:
                 self.bridge.set_extra_args(
@@ -376,7 +378,6 @@ def _build_hf_mcore_bridge(self):
                 self.config.path,
                 trust_remote_code=True,
                 dtype=self.config.dtype,
-                trust_remote_code=True,
             )
             self.logger.info(
                 "Using megatron-bridge to create models and hf model save/load in MegatronEngine."

PATCH

echo "Fix applied: removed duplicate trust_remote_code kwarg."
