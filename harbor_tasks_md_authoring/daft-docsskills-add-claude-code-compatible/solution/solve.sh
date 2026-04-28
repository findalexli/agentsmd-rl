#!/usr/bin/env bash
set -euo pipefail

cd /workspace/daft

# Idempotency guard
if grep -qF "| **Streaming** | `into_batches(N)` | Heavy data (images, tensors) | **Low memor" ".claude/skills/daft-distributed-scaling/SKILL.md" && grep -qF "description: \"Navigate Daft documentation. Invoke when user asks general questio" ".claude/skills/daft-docs-navigation/SKILL.md" && grep -qF "description: \"Optimize Daft UDF performance. Invoke when user needs GPU inferenc" ".claude/skills/daft-udf-tuning/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/daft-distributed-scaling/SKILL.md b/.claude/skills/daft-distributed-scaling/SKILL.md
@@ -0,0 +1,65 @@
+---
+name: "daft-distributed-scaling"
+description: "Scale Daft workflows to distributed Ray clusters. Invoke when optimizing performance or handling large data."
+---
+
+# Daft Distributed Scaling
+
+Scale single-node workflows to distributed execution.
+
+## Core Strategies
+
+| Strategy | API | Use Case | Pros/Cons |
+|---|---|---|---|
+| **Shuffle** | `repartition(N)` | Light data (e.g. file paths), Joins | **Global balance**. High memory usage (materializes data). |
+| **Streaming** | `into_batches(N)` | Heavy data (images, tensors) | **Low memory** (streaming). High scheduling overhead if batches too small. |
+
+## Quick Recipes
+
+### 1. Light Data: Repartitioning
+Best for distributing file paths before heavy reads.
+
+```python
+# Create enough partitions to saturate workers
+df = daft.read_parquet("s3://metadata").repartition(100)
+df = df.with_column("data", read_heavy_data(df["path"]))
+```
+
+### 2. Heavy Data: Streaming Batches
+Best for processing large partitions without OOM.
+
+```python
+# Stream 1GB partition in 64-row chunks to control memory
+df = df.read_parquet("heavy_data").into_batches(64)
+df = df.with_column("embed", model.predict(df["img"]))
+```
+
+## Advanced Tuning: The ByteDance Formula
+
+Target: Keep all actors busy without OOM or scheduling bottlenecks.
+
+### Formula 1: Repartitioning (Light Data / Paths)
+Calculate the **Max Partition Count** to ensure each task has enough data to feed local actors.
+
+1.  **Min Rows Per Partition** = `Batch Size * (Total Concurrency / Nodes)`
+2.  **Max Partitions** = `Total Rows / Min Rows Per Partition`
+
+**Example**:
+- 1M rows, 4 nodes, 16 total concurrency, Batch Size 64.
+- **Min Rows**: `64 * (16/4) = 256`.
+- **Max Partitions**: `1,000,000 / 256 ≈ 3906`.
+- *Recommendation*: Use ~1000 partitions to run multiple batches per task.
+
+```python
+df = df.repartition(1000) # Balanced fan-out
+```
+
+### Formula 2: Streaming (Heavy Data / Images)
+Avoid creating tiny partitions. Use `into_batches` to stream data within larger partitions.
+
+**Strategy**: Keep partitions large (e.g. 1GB+), use `into_batches(Batch Size)` to control memory.
+
+```python
+# Stream batches to control memory usage per actor
+df = df.into_batches(64).with_column("preds", model(max_concurrency=16).predict(df["img"]))
+```
diff --git a/.claude/skills/daft-docs-navigation/SKILL.md b/.claude/skills/daft-docs-navigation/SKILL.md
@@ -0,0 +1,35 @@
+---
+name: "daft-docs-navigation"
+description: "Navigate Daft documentation. Invoke when user asks general questions about APIs, concepts, or examples, or wants to search the docs."
+---
+
+# Daft Docs Navigation
+
+Navigate Daft's documentation for APIs, concepts, and examples.
+
+## Documentation Structure
+
+1.  **Live Site**: [`https://docs.daft.ai`](https://docs.daft.ai) (Primary source, searchable).
+2.  **Source Repo**: `docs/` directory in the repository.
+    -   If `docs/` is missing or empty, clone the repo: `git clone https://github.com/Eventual-Inc/Daft.git`
+
+## Key Locations in `docs/`
+
+-   **API Reference**: `api/` (e.g., `api/io.md` for reading/writing).
+-   **Optimization**: `optimization/` (e.g., `optimization/partitioning.md`).
+-   **Distributed**: `distributed/` (e.g., `distributed/ray.md`).
+-   **UDFs**: `custom-code/` (e.g., `func.md`, `cls.md`).
+-   **Connectors**: `connectors/` (e.g., S3, Lance).
+-   **Table of Contents**: `docs/SUMMARY.md`.
+
+## Usage
+
+**Search for API Usage:**
+```bash
+grep_search(pattern='from_glob', path='docs/')
+```
+
+**Browse Topics:**
+```bash
+read(file_path='docs/SUMMARY.md')
+```
diff --git a/.claude/skills/daft-udf-tuning/SKILL.md b/.claude/skills/daft-udf-tuning/SKILL.md
@@ -0,0 +1,50 @@
+---
+name: "daft-udf-tuning"
+description: "Optimize Daft UDF performance. Invoke when user needs GPU inference, encounters slow UDFs, or asks about async/batch processing."
+---
+
+# Daft UDF Tuning
+
+Optimize User-Defined Functions for performance.
+
+## UDF Types
+
+| Type | Decorator | Use Case |
+|---|---|---|
+| **Stateless** | `@daft.func` | Simple transforms. Use `async` for I/O-bound tasks. |
+| **Stateful** | `@daft.cls` | Expensive init (e.g., loading models). Supports `gpus=N`. |
+| **Batch** | `@daft.func.batch` | Vectorized CPU/GPU ops (NumPy/PyTorch). Faster. |
+
+## Quick Recipes
+
+### 1. Async I/O (Web APIs)
+
+```python
+@daft.func
+async def fetch(url: str):
+    async with aiohttp.ClientSession() as s:
+        return await s.get(url).text()
+```
+
+### 2. GPU Batch Inference (PyTorch/Models)
+
+```python
+@daft.cls(gpus=1)
+class Classifier:
+    def __init__(self):
+        self.model = load_model().cuda() # Run once per worker
+
+    @daft.method.batch(batch_size=32)
+    def predict(self, images):
+        return self.model(images.to_pylist())
+
+# Run with concurrency
+df.with_column("preds", Classifier(max_concurrency=4).predict(df["img"]))
+```
+
+## Tuning Keys
+
+-   **`max_concurrency`**: Total parallel UDF instances.
+-   **`gpus=N`**: GPU request per instance.
+-   **`batch_size`**: Rows per call. Too small = overhead; too big = OOM.
+-   **`into_batches(N)`**: Pre-slice partitions if memory is tight.
PATCH

echo "Gold patch applied."
