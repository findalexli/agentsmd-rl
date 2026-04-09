#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied
if grep -q "### Benchmarking" README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/README.md b/README.md
index ee5f787e0c..1f12142bee 100644
--- a/README.md
+++ b/README.md
@@ -337,6 +337,43 @@ CUDA_VISIBLE_DEVICES=1 uv run trainer @ configs/trainer/reverse_text.toml \
   --orchestrator.monitor.wandb.id <orchestrator-run-id>
 ```

+### Benchmarking
+
+We provide a convenient way to benchmark the performance of the inference engine and trainer using the `--bench` flag. It will run each module in isolation for a few steps and log performance statistics to the console and, optionally, W&B.
+
+**Inference**
+
+To benchmark inference, first spin up the inference server with an experiment configuration
+
+```bash
+uv run inference @ configs/inference/reverse_text.toml
+```
+
+Then, start the orchestrator with the matching configuration file in benchmark mode
+
+```bash
+uv run orchestrator @ configs/orchestrator/reverse_text.toml --bench
+```
+
+**Trainer**
+
+To benchmark the trainer, simply run the trainer against a fake data loader matching the way the orchestrator would write the training batch.
+
+```bash
+uv run trainer @ configs/trainer/reverse_text.toml --bench --data.fake "{'micro_batch_size': 8, 'batch_size': 128, 'seq_len': 128}"
+```
+
+**RL**
+
+Often it will be most convenient to benchmark the full RL run. This will automatically set the training batch configuration to match the way the orchestrator would have written it. Also, if W&B is configured for this project, it will synchronize the benchmark results to the project name, but suffixed with `-bench`.
+
+```bash
+uv run rl   \
+  --trainer @ configs/trainer/reverse_text.toml  \
+  --orchestrator @ configs/orchestrator/reverse_text.toml \
+  --inference @ configs/inference/reverse_text.toml \
+  --bench
+```

 ### Tests

diff --git a/src/prime_rl/orchestrator/config.py b/src/prime_rl/orchestrator/config.py
index e90efb2634..87300684bc 100644
--- a/src/prime_rl/orchestrator/config.py
+++ b/src/prime_rl/orchestrator/config.py
@@ -270,7 +270,7 @@ def validate_batch_size(self):
         return self

     @model_validator(mode="after")
-    def validate_bench(self):
+    def auto_setup_bench(self):
         if self.bench:
             self.max_steps = 6  # Run for 1 warmup step + 5 evaluation steps
             self.async_level = 1e9  # Never wait for RL weight checkpoints
diff --git a/src/prime_rl/orchestrator/orchestrator.py b/src/prime_rl/orchestrator/orchestrator.py
index f872b3ae7a..debdcf20ce 100644
--- a/src/prime_rl/orchestrator/orchestrator.py
+++ b/src/prime_rl/orchestrator/orchestrator.py
@@ -16,7 +16,6 @@ from prime_rl.orchestrator.ckpt import CheckpointManager, Progress
 from prime_rl.environments.registry import get_environment
 from prime_rl.orchestrator.client import (
-    tokenize,
     check_has_model,
     check_health,
     reload_weights,
@@ -34,7 +33,7 @@ from prime_rl.orchestrator.client import (
 )
 from prime_rl.utils.monitor import setup_monitor
 from prime_rl.utils.pydantic_config import parse_argv
-from prime_rl.utils.utils import clean_exit, to_col_format
+from prime_rl.utils.utils import clean_exit, to_col_format, format_num


 @clean_exit
@@ -44,6 +43,12 @@ async def orchestrate(config: OrchestratorConfig):
     logger = setup_logger(config.log)
     logger.info("Starting orchestrator")

+    # Print warning if running in benchmark mode
+    if config.bench:
+        logger.warning(
+            f"Running in benchmark mode (max_steps={config.max_steps}, async_level={format_num(config.async_level, precision=0)})"
+        )
+
     # Setup client
     logger.info(f"Initializing OpenAI client ({config.client.base_url})")
     client = setup_client(config.client)
diff --git a/src/prime_rl/orchestrator/utils.py b/src/prime_rl/orchestrator/utils.py
index 30e23053be..5dfb9656c5 100644
--- a/src/prime_rl/orchestrator/utils.py
+++ b/src/prime_rl/orchestrator/utils.py
@@ -132,7 +132,7 @@ def print_benchmark(history: dict[str, list[Any]]) -> None:
     df = pd.DataFrame(dict(history.items()))
     columns = {
         "perf/infer/throughput": "Throughput",
-        "time/infer": "Step Time",
+        "time/orchestrator": "Step Time",
     }
     df = df[columns.keys()].rename(columns=columns)
     df = df.iloc[1:]  # Exclude first row
diff --git a/src/prime_rl/rl.py b/src/prime_rl/rl.py
index c76ca5098e..1b305f8217 100644
--- a/src/prime_rl/rl.py
+++ b/src/prime_rl/rl.py
@@ -17,7 +17,7 @@ from typing import Annotated, TypeAlias

 from prime_rl.inference.config import InferenceConfig
 from prime_rl.orchestrator.config import OrchestratorConfig
-from prime_rl.trainer.config import CheckpointConfig, TrainerConfig
+from prime_rl.trainer.config import CheckpointConfig, FakeDataLoaderConfig, TrainerConfig
 from prime_rl.utils.config import WandbMonitorConfig
 from prime_rl.utils.logger import format_message, format_time, get_logger, set_logger, setup_handlers
 from prime_rl.utils.pydantic_config import BaseSettings, get_temp_toml_file, parse_argv
@@ -55,6 +55,13 @@ class RLConfig(BaseSettings):
     trainer_gpus: Annotated[int, Field(description="The number of GPUs to use for trainer.")] = 1
     inference_gpus: Annotated[int, Field(description="The number of GPUs to use for inference.")] = 1

+    bench: Annotated[
+        bool,
+        Field(
+            description="Whether to run in benchmark mode. It will automatically set the trainer and orchestrator to benchmark mode and, if present, configure the W&B project by suffixing the project with `-bench`.",
+        ),
+    ] = False
+
     clean: Annotated[
         bool,
         Field(
@@ -75,6 +82,30 @@ def validate_device(self):
             )
         return self

+    @model_validator(mode="after")
+    def auto_setup_bench(self):
+        if self.bench:
+            # Set trainer and orchestrator to benchmark mode
+            self.trainer.bench = True
+            self.orchestrator.bench = True
+
+            # Configure the trainer fake data to match the orchestrator config
+            self.trainer.data.fake = FakeDataLoaderConfig(
+                micro_batch_size=self.orchestrator.micro_batch_size,
+                batch_size=self.orchestrator.batch_size,
+                seq_len=self.orchestrator.seq_len,
+            )
+
+            # Suffix the W&B project with "-bench"
+            if self.trainer.monitor.wandb:
+                self.trainer.monitor.wandb.project = f"{self.trainer.monitor.wandb.project}-bench"
+
+            # Disable evaluation
+            self.orchestrator.eval = None
+            self.orchestrator.monitor.wandb.log_samples = None
+
+        return self
+
     @model_validator(mode="after")
     def auto_setup_logs(self):
         # Copy log level
diff --git a/src/prime_rl/trainer/config.py b/src/prime_rl/trainer/config.py
index 2eb0cbb7b9..1841031b50 100644
--- a/src/prime_rl/trainer/config.py
+++ b/src/prime_rl/trainer/config.py
@@ -208,3 +208,18 @@ class TrainerConfig(BaseSettings):
             description="Whether to recompute the logprobs. If True, will always recompute logprobs and overwrite those found in the training batch.",
         ),
     ] = True
+
+    bench: Annotated[
+        bool,
+        Field(
+            description="Whether to run in benchmark mode. It will automatically set the maximum number of steps to run to 5 and use fake data.",
+        ),
+    ] = False
+
+    @model_validator(mode="after")
+    def auto_setup_bench(self):
+        if self.bench:
+            self.max_steps = 6  # 1 Warmup + 5 Benchmark
+            if not self.data.fake:
+                self.data.fake = FakeDataLoaderConfig()
+        return self
diff --git a/src/prime_rl/trainer/train.py b/src/prime_rl/trainer/train.py
index 2007a8207a..26cbf642c5 100644
--- a/src/prime_rl/trainer/train.py
+++ b/src/prime_rl/trainer/train.py
@@ -26,11 +26,12 @@ from prime_rl.trainer.utils import (
     copy_model_to_cpu,
     offload_model_to_cpu,
     wake_up_model_from_cpu,
+    print_benchmark,
 )
 from prime_rl.trainer.world import get_world
 from prime_rl.utils.monitor import setup_monitor
 from prime_rl.utils.pydantic_config import parse_argv
-from prime_rl.utils.utils import clean_exit
+from prime_rl.utils.utils import clean_exit, to_col_format


 @clean_exit
@@ -41,6 +42,10 @@ def train(config: TrainerConfig):
     logger = setup_logger(config.log, world)
     logger.info(f"Starting trainer in {world}")

+    # Print warning if running in benchmark mode
+    if config.bench:
+        logger.warning(f"Running in benchmark mode (max_steps={config.max_steps}, {config.data.fake=})")
+
     # Setup the monitor
     logger.info(f"Initializing monitor ({config.monitor})")
     monitor = setup_monitor(config.monitor, run_config=config)
@@ -350,6 +355,10 @@ def train(config: TrainerConfig):
     logger.info(f"Peak memory: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")
     logger.success("Trainer finished!")

+    # Optionally, print benchmark table
+    if config.bench:
+        print_benchmark(to_col_format(monitor.history))
+

 def main():
     train(parse_argv(TrainerConfig))
diff --git a/src/prime_rl/trainer/utils.py b/src/prime_rl/trainer/utils.py
index 35d587d718..f33c980d57 100644
--- a/src/prime_rl/trainer/utils.py
+++ b/src/prime_rl/trainer/utils.py
@@ -1,11 +1,15 @@
 from itertools import chain
-from typing import TypeAlias
+from typing import Any, TypeAlias

+import pandas as pd
 import torch
+from rich.console import Console
+from rich.table import Table
 from torch import Tensor
 from torch.distributed.tensor import DTensor

 from prime_rl.trainer.model import Model
+from prime_rl.utils.utils import format_num, format_time


 class FakeTokenizer:
@@ -67,3 +71,54 @@ def wake_up_model_from_cpu(model: Model, tensors: OffloadedTensor):
         data.untyped_storage().resize_(storage_size)
         data.copy_(cpu_data, non_blocking=True)
     torch.cuda.synchronize()
+
+
+def print_benchmark(history: dict[str, list[Any]]) -> None:
+    """
+    Print benchmark results as rich table. Shows formatted values for the
+    training throughput and overall step time. First first N rows show the
+    per-step values, and the last row shows the mean, std, min, and max values.
+    """
+    history.pop("step")
+    assert all(len(v) for v in history.values()), "All metrics must have logged the same number of steps"
+
+    # Turn metric history into pd.DataFrame
+    df = pd.DataFrame(dict(history.items()))
+    columns = {
+        "perf/train/throughput": "Throughput",
+        "time/train": "Step Time",
+    }
+    df = df[columns.keys()].rename(columns=columns)
+    df = df.iloc[1:]  # Exclude first row
+
+    # Setup console
+    console = Console()
+    table = Table(title="Benchmark")
+
+    # Add columns
+    table.add_column("Step", justify="right")
+    for col in df.columns:
+        table.add_column(col, justify="center", style="magenta")
+
+    # Add formatted rows
+    formatted_df = pd.DataFrame(columns=df.columns)
+    formatted_df["Step Time"] = df["Step Time"].apply(format_time)
+    formatted_df["Throughput"] = df["Throughput"].apply(format_num, precision=2)
+    for step, row in formatted_df.iterrows():
+        table.add_row(*([str(step)] + [str(x) for x in row]))
+
+    # Separator
+    table.add_row(*([""] * len(row)))
+
+    # Add row for formatted, aggregated statistics
+    mean_df = df.describe().loc[["mean", "std", "min", "max"], :]
+    formatted_mean_df = pd.DataFrame(columns=mean_df.columns)
+    formatted_mean_df["Step Time"] = mean_df["Step Time"].apply(format_time)
+    formatted_mean_df["Throughput"] = mean_df["Throughput"].apply(format_num, precision=2)
+    mean_row = ["Overall"] + formatted_mean_df.T.apply(
+        lambda row: f"{row['mean']} ± {row['std']} [{row['min']}, {row['max']}]", axis=1
+    ).tolist()
+    table.add_row(*mean_row)
+
+    # Display table
+    console.print(table)

PATCH

echo "Patch applied successfully."
