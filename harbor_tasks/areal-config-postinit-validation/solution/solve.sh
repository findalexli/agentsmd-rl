#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotency: check if NormConfig already has __post_init__
if grep -q 'def __post_init__' areal/api/cli_args.py 2>/dev/null && \
   python3 -c "
import ast, sys
src = open('areal/api/cli_args.py').read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NormConfig':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__post_init__':
                sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/api/cli_args.py b/areal/api/cli_args.py
index d92807f54..dbf303b44 100644
--- a/areal/api/cli_args.py
+++ b/areal/api/cli_args.py
@@ -67,6 +67,24 @@ class NormConfig:
         default=1, metadata={"help": "Group size for group-level normalization"}
     )

+    def __post_init__(self):
+        """Validate normalization configuration."""
+        valid_levels = {"batch", "group", None}
+        if self.mean_level not in valid_levels:
+            raise ValueError(
+                f"mean_level must be 'batch', 'group' or None, got {self.mean_level}"
+            )
+        if self.std_level not in valid_levels:
+            raise ValueError(
+                f"std_level must be 'batch', 'group', or None, got {self.std_level}"
+            )
+        if (
+            self.mean_level == "group" or self.std_level == "group"
+        ) and self.group_size < 1:
+            raise ValueError(
+                f"group_size must be a positive integer when using group normalization, got {self.group_size}"
+            )
+

 @dataclass
 class MicroBatchSpec:
@@ -1137,7 +1155,8 @@ def should_compute_prox_logp(self) -> bool:
         )

     def __post_init__(self):
-        """Validate MIS/TIS configuration."""
+        """Validate PPO actor configuration."""
+        # Validate MIS/TIS configuration
         if self.behave_imp_weight_mode == "disabled":
             if self.behave_imp_weight_cap is not None:
                 raise ValueError(
@@ -1166,6 +1185,21 @@ def __post_init__(self):
                     "Set use_decoupled_loss=True to enable decoupled loss with importance weight correction."
                 )

+        # Validate SAPO configuration
+        if self.use_sapo_loss:
+            if self.sapo_tau_pos <= 0 or self.sapo_tau_neg <= 0:
+                raise ValueError(
+                    f"SAPO temperatures (sapo_tau_pos, sapo_tau_neg) must be positive. "
+                    f"Got sapo_tau_pos={self.sapo_tau_pos}, sapo_tau_neg={self.sapo_tau_neg}."
+                )
+            if self.use_decoupled_loss:
+                raise ValueError(
+                    "SAPO is not compatible with `use_decoupled_loss=True`. "
+                    "Please set `actor.use_decoupled_loss=false` in your configuration."
+                )
+
+        super().__post_init__()
+

 @dataclass
 class PPOCriticConfig(TrainEngineConfig):
@@ -2062,6 +2096,13 @@ class BaseExperimentConfig:

     scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)

+    def __post_init__(self):
+        """Validate training configuration."""
+        if self.total_train_epochs <= 0:
+            raise ValueError(
+                f"total_train_epochs must be positive, got {self.total_train_epochs}"
+            )
+

 @dataclass
 class SFTConfig(BaseExperimentConfig):
@@ -2107,6 +2148,7 @@ def __post_init__(self):
         """Validate the eval generation config."""
         if self.eval_gconfig is None:
             self.eval_gconfig = self.gconfig.new()
+        super().__post_init__()


 @dataclass
diff --git a/areal/utils/data.py b/areal/utils/data.py
index f77694351..44ab80b12 100644
--- a/areal/utils/data.py
+++ b/areal/utils/data.py
@@ -1162,19 +1162,6 @@ class Normalization:
     """

     def __init__(self, config: NormConfig):
-        if config.mean_level not in {"batch", "group", None}:
-            raise ValueError(
-                f"mean_level must be 'batch', 'group' or None, got {config.mean_level}"
-            )
-        if config.std_level not in {"batch", "group", None}:
-            raise ValueError(
-                f"std_level must be 'batch', 'group', or None, got {config.std_level}"
-            )
-        if (
-            config.mean_level == "group" or config.std_level == "group"
-        ) and config.group_size is None:
-            raise ValueError("group_size must be provided if using group normalization")
-
         self.mean_level = config.mean_level
         self.mean_leave1out = config.mean_leave1out
         self.std_level = config.std_level
diff --git a/tests/test_adv_norm_config.py b/tests/test_adv_norm_config.py
index 189f09a1e..fb1553fee 100644
--- a/tests/test_adv_norm_config.py
+++ b/tests/test_adv_norm_config.py
@@ -154,11 +154,12 @@ def test_adv_norm_initialization_validation():
         config = NormConfig(mean_level="batch", std_level="invalid", group_size=1)
         Normalization(config)

-    # Test missing group_size for group normalization
+    # Test invalid group_size for group normalization
     with pytest.raises(
-        ValueError, match="group_size must be provided if using group normalization"
+        ValueError,
+        match="group_size must be a positive integer when using group normalization",
     ):
-        config = NormConfig(mean_level="group", std_level="batch", group_size=None)
+        config = NormConfig(mean_level="group", std_level="batch", group_size=0)
         Normalization(config)


diff --git a/tests/test_prox_approx.py b/tests/test_prox_approx.py
index ed6ae95f4..cbfc762a5 100644
--- a/tests/test_prox_approx.py
+++ b/tests/test_prox_approx.py
@@ -977,11 +977,6 @@ def mock_stat(**kwargs):
             # All imp_weight metrics should use "behave_imp_weight"
             if "imp_weight" in key and "importance_weight" not in key:
                 assert "behave_imp_weight" in key, f"Metric {key} uses wrong spelling"
-        for key in logged_stats.keys():
-            # Should use "behave_imp_weight" not "behave_imp_weight"
-            if "imp_weight" in key and "importance_weight" not in key:
-                assert "behave_imp_weight" in key, f"Metric {key} uses wrong spelling"
-                assert "behave_imp_weight" not in key, f"Metric {key} uses old spelling"


 if __name__ == "__main__":

PATCH
