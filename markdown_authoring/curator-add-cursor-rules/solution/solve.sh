#!/usr/bin/env bash
set -euo pipefail

cd /workspace/curator

# Idempotency guard
if grep -qF "All changes to NeMo Curator's source code must be accompanied with relevant test" ".cursor/rules/coding-standards.mdc" && grep -qF "- Especially useful when stages require different resources (e.g., a CPU-based s" ".cursor/rules/composite-stage-patterns.mdc" && grep -qF "Executors are the runtime engines that execute NeMo Curator pipelines. They hand" ".cursor/rules/executors.mdc" && grep -qF "Other subdirectories of `nemo_curator/stages/` are `deduplication` and `syntheti" ".cursor/rules/modality-structure.mdc" && grep -qF "When a pipeline is built, any `CompositeStage` instances are automatically decom" ".cursor/rules/pipeline-structure.mdc" && grep -qF "Processing stages operate on `Task` objects (or subclasses of `Task` such as `Do" ".cursor/rules/processing-stage-patterns.mdc" && grep -qF "- `gpu_memory_gb` automatically calculates required GPU fraction based on availa" ".cursor/rules/resources-configuration.mdc" && grep -qF "- **_EmptyTask**: A singleton dummy task (`data: None`) used as input for stages" ".cursor/rules/task-patterns.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/coding-standards.mdc b/.cursor/rules/coding-standards.mdc
@@ -0,0 +1,84 @@
+---
+alwaysApply: true
+---
+
+# NeMo Curator Coding Standards
+
+## Linting and Formatting
+
+The project uses **Ruff** for linting and formatting with line length of 119 characters.
+
+## Key Style Rules
+
+### Allowed Patterns
+
+- ✅ Print statements (T20 ignored)
+- ✅ Boolean arguments in functions (FBT ignored)
+- ✅ `df` as variable name for DataFrames (PD901 ignored)
+- ✅ TODOs without author/link (TD002, TD003 ignored)
+- ✅ Long exception messages (TRY003 ignored)
+- ✅ Accessing private attributes (SLF001 ignored)
+- ✅ Branching after return (RET505-508 ignored)
+
+### Required Patterns
+
+- ❌ No docstrings required (D ignored)
+- ❌ No pathlib enforcement (PTH ignored)
+- ❌ No logging enforcement (G ignored)
+- ✅ Type annotations for functions (except `*args`, `**kwargs`, special methods)
+
+## File-Specific Exceptions
+
+### `examples/` directory
+- No `__init__.py` required (INP001)
+
+### `tests/` directory
+- Allow assertions (S101)
+- Allow magic values (PLR2004)
+- No return type annotations required (ANN201)
+
+### `tutorials/` directory
+- No `__init__.py` required (INP001)
+- Ignore Unicode complaint (PLE2515)
+
+## Copyright Header
+
+All non-empty Python files must include the NVIDIA copyright header:
+
+```python
+# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
+#
+# Licensed under the Apache License, Version 2.0 (the "License");
+# you may not use this file except in compliance with the License.
+# You may obtain a copy of the License at
+#
+#     http://www.apache.org/licenses/LICENSE-2.0
+#
+# Unless required by applicable law or agreed to in writing, software
+# distributed under the License is distributed on an "AS IS" BASIS,
+# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+# See the License for the specific language governing permissions and
+# limitations under the License.
+```
+
+## Python Version Support
+
+Supports Python 3.10, 3.11, and 3.12 (requires >=3.10, <3.13)
+
+## Loguru
+
+NeMo Curator uses loguru for logging:
+
+```python
+from loguru import logger
+```
+
+Common uses include `logger.info`, `logger.warning`, and `logger.error`.
+
+## PyTest Standards
+
+All changes to NeMo Curator's source code must be accompanied with relevant tests. Tests which require a GPU and cannot be run on a CPU-only machine must be marked with `@pytest.mark.gpu`.
+
+NeMo Curator enforces 80% PyTest coverage within the `nemo_curator/` directory.
+
+For straightforward navigation purposes, the `tests/` directory structure matches the `nemo_curator/` directory structure.
diff --git a/.cursor/rules/composite-stage-patterns.mdc b/.cursor/rules/composite-stage-patterns.mdc
@@ -0,0 +1,70 @@
+---
+alwaysApply: true
+---
+
+# `CompositeStage` Patterns
+
+## When to Use `CompositeStage`
+
+Use `CompositeStage` for high-level, user-facing stages that decompose into multiple low-level execution stages:
+
+- Provide simplified API while maintaining fine-grained execution control
+- Bundle multiple related stages into a single logical operation
+- Especially useful when stages require different resources (e.g., a CPU-based stage followed by a GPU-based stage)
+- Decomposed during pipeline planning
+
+## Creating a `CompositeStage`
+
+```python
+from dataclasses import dataclass
+
+from nemo_curator.stages.base import CompositeStage, ProcessingStage
+
+
+@dataclass
+class MyCompositeStage(CompositeStage[InputTaskType, OutputTaskType]):
+    param1: str
+    param2: int
+
+    def __post_init__(self) -> None:
+        super().__init__()
+
+        self.stages = [
+            StageA(param1=self.param1),
+            StageB(param2=self.param2),
+            StageC(),
+        ]
+
+    def inputs(self) -> tuple[list[str], list[str]]:
+        # StageA's inputs
+        return self.stages[0].inputs()
+
+    def outputs(self) -> tuple[list[str], list[str]]:
+        # StageC's outputs
+        return self.stages[2].outputs()
+
+    def decompose(self) -> list[ProcessingStage]:
+        return self.stages
+```
+
+## Configuration with `with_()`
+
+`CompositeStage` use a different `with_()` signature that takes a dictionary:
+
+```python
+from nemo_curator.stages.resources import Resources
+
+
+composite_stage = MyCompositeStage(param1, param2)
+
+# Add a with operation
+stage_config = {"StageA": {"resources": Resources(cpus=5.0)}}
+updated_composite_stage = composite_stage.with_(stage_config)
+```
+
+## Important Rules
+
+- Decomposed stages cannot be `CompositeStage`s themselves
+- `inputs()` returns first stage's inputs
+- `outputs()` returns last stage's outputs
+- All stages in `decompose()` must have unique names for `with_()` to work
diff --git a/.cursor/rules/executors.mdc b/.cursor/rules/executors.mdc
@@ -0,0 +1,98 @@
+---
+alwaysApply: true
+---
+
+# Executors
+
+Executors are the runtime engines that execute NeMo Curator pipelines. They handle distributed task orchestration, resource allocation, and worker management.
+
+## Role of Executors
+
+Executors translate the high-level pipeline definition (a sequence of `ProcessingStage` instances) into actual distributed execution:
+
+- **Orchestrate stage execution**: Run stages in sequence, passing tasks between them
+- **Distribute work**: Parallelize task processing across workers/nodes
+- **Manage resources**: Allocate CPUs, GPUs, memory according to stage requirements
+- **Handle batching**: Group tasks into batches for efficient processing
+- **Track performance**: Collect timing and throughput metrics
+- **Manage lifecycle**: Setup and teardown workers/resources
+
+## Available Executors
+
+### `XennaExecutor` (Default)
+
+Production executor using Cosmos-Xenna for distributed execution:
+
+```python
+from nemo_curator.backends.xenna import XennaExecutor
+
+executor = XennaExecutor(config={
+    "logging_interval": 60,
+    "ignore_failures": False,
+    "execution_mode": "streaming",  # or "batch"
+    "cpu_allocation_percentage": 0.95,
+    "autoscale_interval_s": 180,
+})
+```
+
+### Experimental Executors
+
+Located in `nemo_curator.backends.experimental`:
+
+- **RayDataExecutor**: Ray Data backend (supports `ignore_head_node`)
+- **RayActorPoolExecutor**: Ray Actor Pool backend (supports `ignore_head_node`)
+
+## `BaseExecutor` Interface
+
+All executors inherit from `BaseExecutor` and implement:
+
+```python
+class BaseExecutor(ABC):
+    def __init__(self, config: dict[str, Any] | None = None, ignore_head_node: bool = False):
+        """Initialize executor with configuration.
+        
+        Args:
+            config: Executor-specific configuration dictionary
+            ignore_head_node: Whether to exclude head node from execution (not supported by XennaExecutor)
+        """
+        
+    @abstractmethod
+    def execute(self, stages: list[ProcessingStage], initial_tasks: list[Task] | None = None) -> list[Task]:
+        """Execute the pipeline stages.
+        
+        Args:
+            stages: List of processing stages to execute
+            initial_tasks: Initial tasks to start pipeline (defaults to EmptyTask)
+            
+        Returns:
+            List of output tasks from final stage
+        """
+```
+
+## Stage Adapters
+
+Executors use `BaseStageAdapter` to wrap stages for execution:
+
+- Implements batching logic via `process_batch()`
+- Calls stage lifecycle methods (`setup_on_node()`, `setup()`, `teardown()`)
+- Tracks performance metrics with `StageTimer`
+- Attaches performance statistics to output tasks
+
+## Usage in Pipelines
+
+Executors are passed to `pipeline.run()`:
+
+```python
+from nemo_curator.pipeline import Pipeline
+from nemo_curator.backends.xenna import XennaExecutor
+
+
+pipeline = Pipeline(name="my_pipeline", stages=[...])
+
+# Explicit executor
+executor = XennaExecutor(config={"execution_mode": "streaming"})
+results = pipeline.run(executor=executor)
+
+# Default executor (XennaExecutor)
+results = pipeline.run()
+```
diff --git a/.cursor/rules/modality-structure.mdc b/.cursor/rules/modality-structure.mdc
@@ -0,0 +1,70 @@
+---
+alwaysApply: true
+---
+
+# Modality Structure
+
+NeMo Curator supports four data modalities, each with its own stage directory and patterns.
+
+## Directory Structure
+
+```
+nemo_curator/stages/
+├── text/ # Text/document processing
+├── image/ # Image processing
+├── audio/ # Audio/speech processing
+└── video/ # Video processing
+```
+
+Other subdirectories of `nemo_curator/stages/` are `deduplication` and `synthetic`, which contain stages that can be used by two or more modalities.
+
+## Text Processing (`stages/text/`)
+
+Common subdirectories:
+- `classifiers/`: Quality, domain, content safety classification
+- `deduplication/`: Duplicate text removal
+- `download/`: Data ingestion (Common Crawl, Wikipedia, ArXiv)
+- `embedders/`: Text embedding generation
+- `filters/`: Heuristic and model-based filtering
+- `io/`: Readers (Parquet, JSONL) and writers
+- `modifiers/`: Text transformations (cleaning, normalization)
+
+Task type: `DocumentBatch`
+
+## Image Processing (`stages/image/`)
+
+Common operations:
+- CLIP embedding generation
+- Aesthetic quality scoring
+- NSFW detection
+- Deduplication
+
+Task type: `ImageBatch`
+
+## Audio Processing (`stages/audio/`)
+
+Common operations:
+- ASR transcription (NeMo Framework)
+- Word Error Rate (WER) calculation
+- Duration analysis
+- Quality filtering
+
+Task type: `AudioBatch`
+
+## Video Processing (`stages/video/`)
+
+Common operations:
+- Scene detection (TransNetV2)
+- Clip extraction
+- GPU H.264 encoding/decoding
+- Motion and aesthetic filtering
+- Embeddings (InternVideo2, Cosmos-Embed1)
+
+Task type: `VideoTask`
+
+## Shared Components
+
+All modalities share:
+- `stages/base.py`: Base classes (`ProcessingStage`, `CompositeStage`)
+- `stages/resources.py`: Resource configuration
+- `stages/function_decorators.py`: Decorators for creating `ProcessingStage` instances from simple functions
diff --git a/.cursor/rules/pipeline-structure.mdc b/.cursor/rules/pipeline-structure.mdc
@@ -0,0 +1,57 @@
+---
+alwaysApply: true
+---
+
+# Pipeline Structure
+
+## Creating Pipelines
+
+Pipelines compose `ProcessingStage` instances into an executable workflow:
+
+```python
+from nemo_curator.pipeline import Pipeline
+
+pipeline = Pipeline(
+    name="my_pipeline",
+    description="My data processing pipeline",
+    stages=[stage1, stage2, stage3],
+)
+```
+
+## Adding Stages
+
+Stages can be added during initialization or via `add_stage()`:
+
+```python
+# Method 1: During initialization
+pipeline = Pipeline(name="my_pipeline", stages=[stage1, stage2])
+
+# Method 2: Add stages individually
+pipeline = Pipeline(name="my_pipeline")
+pipeline.add_stage(stage1)
+pipeline.add_stage(stage2)
+```
+
+## Running Pipelines
+
+```python
+pipeline.run()
+```
+
+The `run()` method accepts 2 optional parameters:
+
+- `executor`: Executor to use. If None, defaults to `XennaExecutor`
+- `initial_tasks` Initial `Task`s to start the pipeline with. Defaults to None.
+
+Before executing, the `run()` method calls `self.build()` to build an execution plan from the pipeline (e.g., decomposes composite stages).
+
+## Composite Stage Decomposition
+
+When a pipeline is built, any `CompositeStage` instances are automatically decomposed into their constituent execution stages. The decomposition info is stored in `pipeline.decomposition_info`.
+
+## Pipeline Methods
+
+- `add_stage(stage)`: Add a stage to the pipeline (returns self for chaining)
+- `build()`: Decompose composite stages into execution stages
+- `describe()`: Get detailed description of pipeline stages and requirements
+- `run(executor, initial_tasks)`: Execute the pipeline
diff --git a/.cursor/rules/processing-stage-patterns.mdc b/.cursor/rules/processing-stage-patterns.mdc
@@ -0,0 +1,128 @@
+---
+alwaysApply: true
+---
+
+# `ProcessingStage` Patterns
+
+The `ProcessingStage` class is the base class for handling all data curation steps in NeMo Curator. Each subclass of `ProcessingStage` defines an individual step to apply to the data, such as reading, transformations, filtering, and writing.
+
+## Subclass Declaration
+
+Processing stages operate on `Task` objects (or subclasses of `Task` such as `DocumentBatch` for text data). Each stage type can declare what type of `Task` it processes as input and what type it produces as output. When implementing a subclass of `ProcessingStage`, this looks like:
+
+```python
+class ExampleStage(ProcessingStage[InputTaskType, OutputTaskType]):
+```
+
+Stages can return either:
+
+- A single task (typical for transformations)
+- A list of tasks (for stages that split work, like readers)
+- None (for filtered out tasks)
+
+## Properties
+
+Any `ProcessingStage` has 3 internal properties:
+- `_name`: Name identifier for the stage (read-only, accessed via `stage._name`)
+- `_resources`: Computing resources allocated to the stage (read-only, accessed via `stage._resources`)
+- `_batch_size`: Number of tasks to process at a time (read-only, accessed via `stage._batch_size`)
+
+When implementing a subclass of `ProcessingStage`, you can customize these properties by setting these public class attributes:
+- `name`: String identifier (default: "ProcessingStage" - **strongly recommended to override**)
+- `resources`: Resources object (default: `Resources(cpus=1.0)`)
+- `batch_size`: Integer batch size (default: `1`)
+
+**Important**: These should be set as class attributes or dataclass fields, **not** as properties. The underscore versions are read-only properties managed by the base class.
+
+## `inputs()` and `outputs()` Functions
+
+The `inputs()` and `outputs()` methods declare what data a stage requires and produces:
+
+```python
+def inputs(self) -> tuple[list[str], list[str]]:
+    """Define stage input requirements.
+
+    Returns (tuple[list[str], list[str]]):
+        Tuple of (required_task_attributes, required_data_attributes) where:
+        - required_task_attributes: List of task attributes that must be present
+        - required_data_attributes: List of attributes within the data that must be present
+    """
+    return ["data"], ["text"]  # Requires "text" column in task.data
+
+def outputs(self) -> tuple[list[str], list[str]]:
+    """Define stage output requirements.
+
+    Returns (tuple[list[str], list[str]]):
+        Tuple of (output_task_attributes, output_data_attributes) where:
+        - output_task_attributes: List of task attributes this stage adds/modifies
+        - output_data_attributes: List of attributes within the data that this stage adds/modifies
+    """
+    return ["data"], ["processed_text"]  # Adds "processed_text" column
+```
+
+These functions verify that a task has the necessary top-level attributes and that `task.data` has the necessary data attributes. This enables automatic validation at runtime and logs errors for missing attributes.
+
+## `process()` Function
+
+The main method that processes a single task. Must be implemented by all concrete stages:
+
+```python
+def process(self, task: InputTaskType) -> OutputTaskType | list[OutputTaskType] | None:
+    # Transform the task...
+    return output_task
+```
+
+Can return:
+
+- **Single task**: For 1-to-1 transformations
+- **List of tasks**: For splitting/reading operations
+- **None**: To filter out the task
+
+## Optional Lifecycle Methods
+
+Beyond `process()`, stages can implement:
+
+- `setup_on_node(node_info, worker_metadata)`: Node-level initialization (e.g., download models)
+- `setup(worker_metadata)`: Worker-level initialization (e.g., load models)
+- `teardown()`: Cleanup after processing
+- `process_batch(tasks)`: Vectorized batch processing for better performance
+
+See the `ProcessingStage` implementation for full details.
+
+## Example Implementation
+
+```python
+from dataclasses import dataclass
+
+from nemo_curator.stages.base import ProcessingStage
+from nemo_curator.stages.resources import Resources
+from nemo_curator.tasks import Task
+
+
+@dataclass
+class ExampleStage(ProcessingStage[Task, Task]):
+    name: str = "ExampleStage"
+    resources: Resources = Resources(cpus=1.0)  # Default
+    batch_size: int = 1  # Default
+
+    def inputs(self) -> tuple[list[str], list[str]]:
+        return ["data"], []
+
+    def outputs(self) -> tuple[list[str], list[str]]:
+        return ["data"], []
+
+    def process(self, task: Task) -> Task | None:
+        # From our inputs() requirements, Task has the data attribute
+        task_data = task.data
+
+        # Transform the data in some way...
+
+        # Create output task
+        return Task(
+            task_id=f"{task.task_id}_{self.name}",  # Common naming pattern
+            dataset_name=task.dataset_name,
+            data=task_data,
+            _metadata=task._metadata,
+            _stage_perf=task._stage_perf,
+        )
+```
diff --git a/.cursor/rules/resources-configuration.mdc b/.cursor/rules/resources-configuration.mdc
@@ -0,0 +1,45 @@
+---
+alwaysApply: true
+---
+
+# Resources Configuration
+
+## Resources Class
+
+The `Resources` dataclass defines compute requirements for stages:
+
+```python
+from nemo_curator.stages.resources import Resources
+
+# CPU-only stage
+resources = Resources(cpus=2.0)
+
+# GPU stage (single GPU)
+resources = Resources(
+    cpus=4.0,
+    gpu_memory_gb=16.0  # Automatically calculates GPU fraction
+)
+
+# Multi-GPU stage
+resources = Resources(
+    cpus=8.0,
+    gpus=2.0  # Explicit GPU count
+)
+```
+
+## Resource Attributes
+
+- `cpus`: Number of CPU cores (default: 1.0)
+- `gpu_memory_gb`: GPU memory in GB for single-GPU stages (default: 0.0)
+- `gpus`: Number of GPUs for single- or multi-GPU stages (default: 0.0)
+
+## Important Constraints
+
+- **Cannot specify both** `gpus` and `gpu_memory_gb`
+- Use `gpu_memory_gb` for single-GPU stages (< 1 GPU)
+- Use `gpus` for multi-GPU stages (>= 1 GPU)
+- `gpu_memory_gb` automatically calculates required GPU fraction based on available GPU memory
+
+## Properties
+
+- `requires_gpu`: Returns True if any GPU resources are requested
diff --git a/.cursor/rules/task-patterns.mdc b/.cursor/rules/task-patterns.mdc
@@ -0,0 +1,52 @@
+---
+alwaysApply: true
+---
+
+# Task Patterns
+
+## Task Base Class
+
+Tasks are the fundamental unit of data processed through stages and pipelines. All tasks must:
+
+- Inherit from `Task[T]` where `T` is the data type (e.g., `pd.DataFrame`)
+- Define the `task_id`, `dataset_name`, and `data` attributes
+- Implement the abstract `num_items` property
+- Implement the abstract `validate()` method
+
+## Common Task Types
+
+- **DocumentBatch**: For text document processing (`data: pa.Table | pd.DataFrame`)
+- **VideoTask**: For video processing (`data: nemo_curator.tasks.video.Video`)
+- **ImageBatch**: For image processing (`data: list[nemo_curator.tasks.image.ImageObject]`)
+- **AudioBatch**: For audio processing (`data: dict | list[dict]`)
+- **FileGroupTask**: Represents a list of file names (`data: list[str]`)
+- **_EmptyTask**: A singleton dummy task (`data: None`) used as input for stages that **generate** data rather than transform it. Commonly used for:
+  - **File discovery stages** (e.g., `FilePartitioningStage` that scans directories and produces `FileGroupTask`s)
+  - **Reader stages** at the start of a pipeline (e.g., stages that list files to read)
+  - **Data generation stages** that don't need input data
+
+## Task Attributes
+
+Tasks automatically include:
+
+- `task_id`: Unique identifier for the task
+- `dataset_name`: Name of the dataset
+- `data`: The actual data payload (type `T`)
+- `_stage_perf`: List of performance statistics per stage
+- `_metadata`: Dictionary for arbitrary metadata
+- `_uuid`: Auto-generated UUID
+
+## Example Task Creation
+
+```python
+import pandas as pd
+
+from nemo_curator.tasks import DocumentBatch
+
+
+task = DocumentBatch(
+    task_id="batch_001",
+    dataset_name="my_dataset",
+    data=pd.DataFrame({"text": ["doc1", "doc2"]})
+)
+```
PATCH

echo "Gold patch applied."
