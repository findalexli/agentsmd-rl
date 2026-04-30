#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency: if the distinctive line is already present, the patch was applied.
if grep -q "self.classifier = self.classifier.to(self.dtype)" \
        src/transformers/models/switch_transformers/modeling_switch_transformers.py; then
    echo "Gold patch already applied — skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/transformers/models/switch_transformers/modeling_switch_transformers.py b/src/transformers/models/switch_transformers/modeling_switch_transformers.py
index 262825fe9ea4..d1a3123c8537 100644
--- a/src/transformers/models/switch_transformers/modeling_switch_transformers.py
+++ b/src/transformers/models/switch_transformers/modeling_switch_transformers.py
@@ -91,6 +91,7 @@ def forward(self, hidden_states: torch.Tensor) -> tuple[torch.Tensor, torch.Tens
         if self.training and self.jitter_noise > 0:
             # Multiply the token inputs by the uniform distribution - adding some noise
             hidden_states *= torch.empty_like(hidden_states).uniform_(1.0 - self.jitter_noise, 1.0 + self.jitter_noise)
+        self.classifier = self.classifier.to(self.dtype)
         router_logits = self.classifier(hidden_states)

         # Apply Softmax and cast back to the original `dtype`
diff --git a/src/transformers/models/switch_transformers/modular_switch_transformers.py b/src/transformers/models/switch_transformers/modular_switch_transformers.py
index 5cbe267b1043..5c0f253cfb78 100644
--- a/src/transformers/models/switch_transformers/modular_switch_transformers.py
+++ b/src/transformers/models/switch_transformers/modular_switch_transformers.py
@@ -158,6 +158,7 @@ def forward(self, hidden_states: torch.Tensor) -> tuple[torch.Tensor, torch.Tens
         if self.training and self.jitter_noise > 0:
             # Multiply the token inputs by the uniform distribution - adding some noise
             hidden_states *= torch.empty_like(hidden_states).uniform_(1.0 - self.jitter_noise, 1.0 + self.jitter_noise)
+        self.classifier = self.classifier.to(self.dtype)
         router_logits = self.classifier(hidden_states)

         # Apply Softmax and cast back to the original `dtype`
diff --git a/src/transformers/models/timm_wrapper/modeling_timm_wrapper.py b/src/transformers/models/timm_wrapper/modeling_timm_wrapper.py
index e49f3d77011f..17e87cb8f959 100644
--- a/src/transformers/models/timm_wrapper/modeling_timm_wrapper.py
+++ b/src/transformers/models/timm_wrapper/modeling_timm_wrapper.py
@@ -243,7 +243,7 @@ def forward(
                 "different architecture or updating the timm package to a compatible version."
             )

-        pixel_values = pixel_values.to(self.device)
+        pixel_values = pixel_values.to(self.device, self.dtype)

         if self.features_only:
             last_hidden_state = self.timm_model.forward(pixel_values, **kwargs)
PATCH

echo "Gold patch applied."
