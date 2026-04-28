"""Behavioral checks for curator-add-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/curator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coding-standards.mdc')
    assert "All changes to NeMo Curator's source code must be accompanied with relevant tests. Tests which require a GPU and cannot be run on a CPU-only machine must be marked with `@pytest.mark.gpu`." in text, "expected to find: " + "All changes to NeMo Curator's source code must be accompanied with relevant tests. Tests which require a GPU and cannot be run on a CPU-only machine must be marked with `@pytest.mark.gpu`."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coding-standards.mdc')
    assert 'For straightforward navigation purposes, the `tests/` directory structure matches the `nemo_curator/` directory structure.' in text, "expected to find: " + 'For straightforward navigation purposes, the `tests/` directory structure matches the `nemo_curator/` directory structure.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coding-standards.mdc')
    assert 'The project uses **Ruff** for linting and formatting with line length of 119 characters.' in text, "expected to find: " + 'The project uses **Ruff** for linting and formatting with line length of 119 characters.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/composite-stage-patterns.mdc')
    assert '- Especially useful when stages require different resources (e.g., a CPU-based stage followed by a GPU-based stage)' in text, "expected to find: " + '- Especially useful when stages require different resources (e.g., a CPU-based stage followed by a GPU-based stage)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/composite-stage-patterns.mdc')
    assert 'Use `CompositeStage` for high-level, user-facing stages that decompose into multiple low-level execution stages:' in text, "expected to find: " + 'Use `CompositeStage` for high-level, user-facing stages that decompose into multiple low-level execution stages:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/composite-stage-patterns.mdc')
    assert '`CompositeStage` use a different `with_()` signature that takes a dictionary:' in text, "expected to find: " + '`CompositeStage` use a different `with_()` signature that takes a dictionary:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/executors.mdc')
    assert 'Executors are the runtime engines that execute NeMo Curator pipelines. They handle distributed task orchestration, resource allocation, and worker management.' in text, "expected to find: " + 'Executors are the runtime engines that execute NeMo Curator pipelines. They handle distributed task orchestration, resource allocation, and worker management.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/executors.mdc')
    assert 'Executors translate the high-level pipeline definition (a sequence of `ProcessingStage` instances) into actual distributed execution:' in text, "expected to find: " + 'Executors translate the high-level pipeline definition (a sequence of `ProcessingStage` instances) into actual distributed execution:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/executors.mdc')
    assert 'def execute(self, stages: list[ProcessingStage], initial_tasks: list[Task] | None = None) -> list[Task]:' in text, "expected to find: " + 'def execute(self, stages: list[ProcessingStage], initial_tasks: list[Task] | None = None) -> list[Task]:'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/modality-structure.mdc')
    assert 'Other subdirectories of `nemo_curator/stages/` are `deduplication` and `synthetic`, which contain stages that can be used by two or more modalities.' in text, "expected to find: " + 'Other subdirectories of `nemo_curator/stages/` are `deduplication` and `synthetic`, which contain stages that can be used by two or more modalities.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/modality-structure.mdc')
    assert '- `stages/function_decorators.py`: Decorators for creating `ProcessingStage` instances from simple functions' in text, "expected to find: " + '- `stages/function_decorators.py`: Decorators for creating `ProcessingStage` instances from simple functions'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/modality-structure.mdc')
    assert 'NeMo Curator supports four data modalities, each with its own stage directory and patterns.' in text, "expected to find: " + 'NeMo Curator supports four data modalities, each with its own stage directory and patterns.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pipeline-structure.mdc')
    assert 'When a pipeline is built, any `CompositeStage` instances are automatically decomposed into their constituent execution stages. The decomposition info is stored in `pipeline.decomposition_info`.' in text, "expected to find: " + 'When a pipeline is built, any `CompositeStage` instances are automatically decomposed into their constituent execution stages. The decomposition info is stored in `pipeline.decomposition_info`.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pipeline-structure.mdc')
    assert 'Before executing, the `run()` method calls `self.build()` to build an execution plan from the pipeline (e.g., decomposes composite stages).' in text, "expected to find: " + 'Before executing, the `run()` method calls `self.build()` to build an execution plan from the pipeline (e.g., decomposes composite stages).'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pipeline-structure.mdc')
    assert '- `initial_tasks` Initial `Task`s to start the pipeline with. Defaults to None.' in text, "expected to find: " + '- `initial_tasks` Initial `Task`s to start the pipeline with. Defaults to None.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/processing-stage-patterns.mdc')
    assert 'Processing stages operate on `Task` objects (or subclasses of `Task` such as `DocumentBatch` for text data). Each stage type can declare what type of `Task` it processes as input and what type it prod' in text, "expected to find: " + 'Processing stages operate on `Task` objects (or subclasses of `Task` such as `DocumentBatch` for text data). Each stage type can declare what type of `Task` it processes as input and what type it prod'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/processing-stage-patterns.mdc')
    assert 'The `ProcessingStage` class is the base class for handling all data curation steps in NeMo Curator. Each subclass of `ProcessingStage` defines an individual step to apply to the data, such as reading,' in text, "expected to find: " + 'The `ProcessingStage` class is the base class for handling all data curation steps in NeMo Curator. Each subclass of `ProcessingStage` defines an individual step to apply to the data, such as reading,'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/processing-stage-patterns.mdc')
    assert 'These functions verify that a task has the necessary top-level attributes and that `task.data` has the necessary data attributes. This enables automatic validation at runtime and logs errors for missi' in text, "expected to find: " + 'These functions verify that a task has the necessary top-level attributes and that `task.data` has the necessary data attributes. This enables automatic validation at runtime and logs errors for missi'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/resources-configuration.mdc')
    assert '- `gpu_memory_gb` automatically calculates required GPU fraction based on available GPU memory' in text, "expected to find: " + '- `gpu_memory_gb` automatically calculates required GPU fraction based on available GPU memory'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/resources-configuration.mdc')
    assert '- `gpu_memory_gb`: GPU memory in GB for single-GPU stages (default: 0.0)' in text, "expected to find: " + '- `gpu_memory_gb`: GPU memory in GB for single-GPU stages (default: 0.0)'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/resources-configuration.mdc')
    assert '- `gpus`: Number of GPUs for single- or multi-GPU stages (default: 0.0)' in text, "expected to find: " + '- `gpus`: Number of GPUs for single- or multi-GPU stages (default: 0.0)'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/task-patterns.mdc')
    assert '- **_EmptyTask**: A singleton dummy task (`data: None`) used as input for stages that **generate** data rather than transform it. Commonly used for:' in text, "expected to find: " + '- **_EmptyTask**: A singleton dummy task (`data: None`) used as input for stages that **generate** data rather than transform it. Commonly used for:'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/task-patterns.mdc')
    assert '- **File discovery stages** (e.g., `FilePartitioningStage` that scans directories and produces `FileGroupTask`s)' in text, "expected to find: " + '- **File discovery stages** (e.g., `FilePartitioningStage` that scans directories and produces `FileGroupTask`s)'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/task-patterns.mdc')
    assert 'Tasks are the fundamental unit of data processed through stages and pipelines. All tasks must:' in text, "expected to find: " + 'Tasks are the fundamental unit of data processed through stages and pipelines. All tasks must:'[:80]

