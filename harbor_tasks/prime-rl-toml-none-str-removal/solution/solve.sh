#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency: check if fix is already applied
if grep -q 'exclude_none=True' src/prime_rl/entrypoints/rl.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/entrypoints/inference.py b/src/prime_rl/entrypoints/inference.py
index 9ef6791202..37c3597e05 100644
--- a/src/prime_rl/entrypoints/inference.py
+++ b/src/prime_rl/entrypoints/inference.py
@@ -5,7 +5,7 @@
 import tomli_w

 from prime_rl.configs.inference import InferenceConfig
-from prime_rl.utils.config import cli, none_to_none_str
+from prime_rl.utils.config import cli
 from prime_rl.utils.logger import setup_logger
 from prime_rl.utils.pathing import get_config_dir

@@ -18,7 +18,7 @@ def write_config(config: InferenceConfig, output_dir: Path, exclude: set[str] |
     output_dir.mkdir(parents=True, exist_ok=True)
     config_path = output_dir / INFERENCE_TOML
     with open(config_path, "wb") as f:
-        tomli_w.dump(none_to_none_str(config.model_dump(exclude=exclude, mode="json")), f)
+        tomli_w.dump(config.model_dump(exclude=exclude, exclude_none=True, mode="json"), f)
     return config_path


diff --git a/src/prime_rl/entrypoints/rl.py b/src/prime_rl/entrypoints/rl.py
index d9cb8623cf..ad09848f1d 100644
--- a/src/prime_rl/entrypoints/rl.py
+++ b/src/prime_rl/entrypoints/rl.py
@@ -12,7 +12,7 @@
 import tomli_w

 from prime_rl.configs.rl import RLConfig
-from prime_rl.utils.config import cli, none_to_none_str
+from prime_rl.utils.config import cli
 from prime_rl.utils.logger import setup_logger
 from prime_rl.utils.pathing import validate_output_dir
 from prime_rl.utils.process import cleanup_processes, cleanup_threads, monitor_process
@@ -42,7 +42,7 @@ def get_physical_gpu_ids() -> list[int]:
 def write_config(config: RLConfig, output_dir: Path, exclude: set[str] | None = None) -> None:
     """Write resolved config to disk, excluding launcher-only fields."""
     output_dir.mkdir(parents=True, exist_ok=True)
-    config_dict = none_to_none_str(config.model_dump(exclude=exclude, mode="json"))
+    config_dict = config.model_dump(exclude=exclude, exclude_none=True, mode="json")
     with open(output_dir / RL_TOML, "wb") as f:
         tomli_w.dump(config_dict, f)

@@ -52,19 +52,19 @@ def write_subconfigs(config: RLConfig, output_dir: Path) -> None:
     output_dir.mkdir(parents=True, exist_ok=True)

     with open(output_dir / TRAINER_TOML, "wb") as f:
-        tomli_w.dump(none_to_none_str(config.trainer.model_dump(mode="json")), f)
+        tomli_w.dump(config.trainer.model_dump(exclude_none=True, mode="json"), f)

     with open(output_dir / ORCHESTRATOR_TOML, "wb") as f:
-        tomli_w.dump(none_to_none_str(config.orchestrator.model_dump(mode="json")), f)
+        tomli_w.dump(config.orchestrator.model_dump(exclude_none=True, mode="json"), f)

     if config.inference is not None:
         with open(output_dir / INFERENCE_TOML, "wb") as f:
-            tomli_w.dump(none_to_none_str(config.inference.model_dump(mode="json")), f)
+            tomli_w.dump(config.inference.model_dump(exclude_none=True, mode="json"), f)

     teacher_inference = getattr(config, "teacher_inference", None)
     if teacher_inference is not None:
         with open(output_dir / TEACHER_INFERENCE_TOML, "wb") as f:
-            tomli_w.dump(none_to_none_str(teacher_inference.model_dump(mode="json")), f)
+            tomli_w.dump(teacher_inference.model_dump(exclude_none=True, mode="json"), f)


 def check_gpus_available(gpu_ids: list[int]) -> None:
diff --git a/src/prime_rl/entrypoints/sft.py b/src/prime_rl/entrypoints/sft.py
index 2544c973ab..033e4b2690 100644
--- a/src/prime_rl/entrypoints/sft.py
+++ b/src/prime_rl/entrypoints/sft.py
@@ -9,7 +9,7 @@
 import tomli_w

 from prime_rl.configs.sft import SFTConfig
-from prime_rl.utils.config import cli, none_to_none_str
+from prime_rl.utils.config import cli
 from prime_rl.utils.logger import setup_logger
 from prime_rl.utils.pathing import get_config_dir, get_log_dir, validate_output_dir
 from prime_rl.utils.process import cleanup_processes, cleanup_threads, monitor_process
@@ -22,7 +22,7 @@
 def write_config(config: SFTConfig, config_path: Path, exclude: set[str] | None = None) -> None:
     """Write resolved config to disk, excluding launcher-only fields."""
     config_path.parent.mkdir(parents=True, exist_ok=True)
-    config_dict = none_to_none_str(config.model_dump(exclude=exclude, mode="json"))
+    config_dict = config.model_dump(exclude=exclude, exclude_none=True, mode="json")
     with open(config_path, "wb") as f:
         tomli_w.dump(config_dict, f)

diff --git a/src/prime_rl/utils/config.py b/src/prime_rl/utils/config.py
index 74f24f0f0f..d0efebccec 100644
--- a/src/prime_rl/utils/config.py
+++ b/src/prime_rl/utils/config.py
@@ -3,26 +3,6 @@
 from pydantic_config import cli  # noqa: F401


-def _convert_none(value):
-    """Recursively convert None to ``"None"`` strings for TOML serialization."""
-    if value is None:
-        return "None"
-    if isinstance(value, dict):
-        return {k: _convert_none(v) for k, v in value.items()}
-    if isinstance(value, list):
-        return [_convert_none(item) for item in value]
-    return value
-
-
-def none_to_none_str(data: dict) -> dict:
-    """Convert None values to ``"None"`` strings so they survive TOML serialization.
-
-    TOML has no null type, so we use the ``"None"`` string convention which
-    ``BaseConfig._none_str_to_none`` converts back to ``None`` on load.
-    """
-    return _convert_none(data)
-
-
 def get_all_fields(model: BaseModel | type) -> list[str]:
     if isinstance(model, BaseModel):
         model_cls = model.__class__

PATCH

echo "Patch applied successfully."
