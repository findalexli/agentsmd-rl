#!/usr/bin/env bash
set -euo pipefail

FILE="areal/api/cli_args.py"

# Idempotency: check if already fixed (Literal removed from ray_placement_strategy line)
if grep -q 'ray_placement_strategy: str = field' "$FILE"; then
    echo "Already patched."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/api/cli_args.py b/areal/api/cli_args.py
index 2f63ed39b..6ef562f75 100644
--- a/areal/api/cli_args.py
+++ b/areal/api/cli_args.py
@@ -5,7 +5,7 @@
 from dataclasses import asdict, dataclass, field, fields
 from enum import Enum
 from pathlib import Path
-from typing import TYPE_CHECKING, Any, ClassVar, Literal
+from typing import TYPE_CHECKING, Any, ClassVar

 import uvloop
 import yaml
@@ -854,7 +854,7 @@ class SchedulingSpec:
     exclude: str | None = field(
         default=None, metadata={"help": "sbatch/srun's `--exclude` option for slurm."}
     )
-    ray_placement_strategy: Literal["shared", "separate", "deferred"] = field(
+    ray_placement_strategy: str = field(
         default="shared",
         metadata={
             "help": "Which placement strategy to use for Ray scheduling. "
@@ -865,6 +865,15 @@ class SchedulingSpec:
         },
     )

+    def __post_init__(self):
+        """Validate scheduling spec configuration."""
+        valid_strategies = {"shared", "separate", "deferred"}
+        if self.ray_placement_strategy not in valid_strategies:
+            raise ValueError(
+                f"ray_placement_strategy must be one of {valid_strategies}, "
+                f"got '{self.ray_placement_strategy}'"
+            )
+

 @dataclass
 class TrainEngineConfig:

PATCH

echo "Patch applied successfully."
