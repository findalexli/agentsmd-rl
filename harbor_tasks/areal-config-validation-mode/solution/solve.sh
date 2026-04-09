#!/usr/bin/env bash
set -euo pipefail

cd /workspace/areal

# Idempotent: skip if already applied
if grep -q "Invalid wandb mode:" areal/api/cli_args.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/areal/api/cli_args.py b/areal/api/cli_args.py
index 7701dab08..e08c852ec 100644
--- a/areal/api/cli_args.py
+++ b/areal/api/cli_args.py
@@ -1968,7 +1968,13 @@ def __post_init__(self):
 class WandBConfig:
     """Configuration for Weights & Biases experiment tracking."""

-    mode: str = "disabled"
+    mode: str = field(
+        default="disabled",
+        metadata={
+            "help": "Tracking mode. One of 'online', 'offline', 'disabled', or 'shared'.",
+            "choices": ["online", "offline", "disabled", "shared"],
+        },
+    )
     wandb_base_url: str = ""
     wandb_api_key: str = ""
     entity: str | None = None
@@ -1981,6 +1987,14 @@ class WandBConfig:
     config: dict | None = None
     id_suffix: str | None = "train"

+    def __post_init__(self):
+        """Validate WandB configuration."""
+        valid_modes = ("online", "offline", "disabled", "shared")
+        if self.mode not in valid_modes:
+            raise ValueError(
+                f"Invalid wandb mode: '{self.mode}'. Must be one of: {', '.join(valid_modes)}."
+            )
+

 @dataclass
 class SwanlabConfig:
@@ -1990,11 +2004,23 @@ class SwanlabConfig:
     name: str | None = None
     config: dict | None = None
     logdir: str | None = None
-    mode: str | None = "disabled"
+    mode: str = field(
+        default="disabled",
+        metadata={
+            "help": "Tracking mode. One of 'cloud', 'local', 'disabled', or 'offline'.",
+            "choices": ["cloud", "local", "disabled", "offline"],
+        },
+    )
     # set None to prevent info-leak in docs
     api_key: str | None = None

     def __post_init__(self):
+        """Validate SwanLab configuration."""
+        valid_modes = ("cloud", "local", "disabled", "offline")
+        if self.mode not in valid_modes:
+            raise ValueError(
+                f"Invalid swanlab mode: '{self.mode}'. Must be one of: {', '.join(valid_modes)}."
+            )
         if self.api_key is None:
             self.api_key = os.getenv("SWANLAB_API_KEY")

PATCH

echo "Patch applied successfully."
