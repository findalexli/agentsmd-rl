#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rapidfireai

# Idempotency guard
if grep -qF "RapidFire AI is an experiment execution framework for LLM fine-tuning and post-t" "CLAUDE.md" && grep -qF "The automl module provides search algorithms for hyperparameter tuning and confi" "rapidfireai/automl/CLAUDE.md" && grep -qF "The backend module contains the core orchestration logic for RapidFire's chunk-b" "rapidfireai/backend/CLAUDE.md" && grep -qF "The db module provides the persistence layer for RapidFire using SQLite. It stor" "rapidfireai/db/CLAUDE.md" && grep -qF "The dispatcher is a Flask-based REST API that provides the communication layer b" "rapidfireai/dispatcher/CLAUDE.md" && grep -qF "The ml module contains the training execution logic that wraps HuggingFace Trans" "rapidfireai/ml/CLAUDE.md" && grep -qF "The utils module contains shared utilities used across RapidFire components, inc" "rapidfireai/utils/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,354 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## Project Overview
+
+RapidFire AI is an experiment execution framework for LLM fine-tuning and post-training that enables hyperparallelized training, dynamic real-time experiment control (IC Ops), and automatic multi-GPU orchestration. The system uses chunk-based scheduling to allow concurrent training of multiple configurations even on a single GPU.
+
+## Key Commands
+
+### Development Setup
+
+```bash
+# Create and activate virtual environment
+python3 -m venv .venv
+source .venv/bin/activate
+
+# Install dependencies from source
+pip install -r requirements.txt
+
+# Install Node.js 22.x and build frontend
+cd rapidfireai/frontend
+node ./yarn/releases/yarn-4.9.1.cjs install
+node ./yarn/releases/yarn-4.9.1.cjs build
+cd ../..
+
+# Start all services in development mode
+chmod +x ./rapidfireai/start_dev.sh
+./rapidfireai/start_dev.sh start
+
+# Stop services
+./rapidfireai/start_dev.sh stop
+```
+
+### Running from Installed Package
+
+```bash
+# Initialize RapidFire (installs dependencies, copies tutorials)
+rapidfireai init
+
+# Start RapidFire servers (dispatcher, mlflow, frontend)
+rapidfireai start
+
+# Stop all servers
+rapidfireai stop
+
+# System diagnostics (GPU, CUDA, Python env)
+rapidfireai doctor
+
+# Check version
+rapidfireai --version
+```
+
+### Testing
+
+```bash
+# Run all tests
+pytest
+
+# Run specific test file
+pytest tests/test_chunks.py
+
+# Run with verbose output
+pytest -v
+```
+
+### Code Quality
+
+```bash
+# Format code with ruff (line-length: 120)
+ruff format .
+
+# Run linter
+ruff check .
+
+# Fix auto-fixable issues
+ruff check --fix .
+```
+
+### Building and Releasing
+
+```bash
+# Build PyPI package (requires frontend build first)
+rm -rf dist/ *.egg-info/ .eggs/ && python -m build
+
+# Bump version (creates commit and tag)
+./bump_version.sh patch  # 0.10.1 → 0.10.2
+./bump_version.sh minor  # 0.10.1 → 0.11.0
+./bump_version.sh major  # 0.10.1 → 1.0.0
+
+# Push version tag to trigger TestPyPI deployment
+git push origin test0.10.2
+```
+
+### Port Management
+
+```bash
+# Kill services on specific ports if conflicts occur
+lsof -t -i:8080 | xargs kill -9  # dispatcher
+lsof -t -i:5002 | xargs kill -9  # mlflow
+lsof -t -i:3000 | xargs kill -9  # frontend
+```
+
+## Architecture
+
+RapidFire AI uses a microservices-inspired distributed architecture:
+
+### Core Components
+
+1. **Experiment** (`experiment.py`): Top-level API for users. Manages experiment lifecycle, creates database tables, sets up logging and signal handlers. Entry point for `run_fit()` and `get_results()`.
+
+2. **Controller** (`backend/controller.py`): Orchestrates the entire training lifecycle. Runs in the user's process. Responsible for:
+   - Creating models from parameter configurations
+   - Initializing and managing Workers
+   - Running the Scheduler to assign chunks to workers
+   - Handling Interactive Control Operations (IC Ops)
+   - Monitoring training progress
+
+3. **Scheduler** (`backend/scheduler.py`): Pure scheduling logic that assigns runs to available workers for specific chunks. Uses round-robin and fairness algorithms to ensure optimal GPU utilization. Tracks which runs have completed which chunks.
+
+4. **Worker** (`backend/worker.py`): Separate GPU processes that execute actual training. Each worker:
+   - Polls database for assigned tasks
+   - Loads model checkpoints from shared memory or disk
+   - Trains on assigned data chunks
+   - Saves checkpoints back to shared memory/disk
+   - Reports progress to MLflow
+
+5. **Dispatcher** (`dispatcher/dispatcher.py`): Flask-based REST API for UI communication. Provides endpoints for:
+   - Viewing experiment status
+   - Interactive Control Operations (stop, resume, clone, delete runs)
+   - Real-time run metrics
+
+6. **Database** (`db/rf_db.py`): SQLite-based persistence layer with async operations. Stores:
+   - Experiment metadata
+   - Run configurations and status
+   - Task scheduling state
+   - Checkpoint locations
+
+7. **Frontend** (`frontend/`): React-based dashboard (MLflow fork) with IC Ops panel. Displays live experiment tracking and enables dynamic control.
+
+### Data Flow
+
+1. User creates `Experiment` and calls `run_fit()` with configs and datasets
+2. Controller creates runs in database and spawns Worker processes
+3. Controller runs Scheduler loop to assign (run_id, chunk_id) to available workers
+4. Workers poll database, load models, train on chunks, save checkpoints
+5. Workers report metrics to MLflow and update database task status
+6. Scheduler continues until all runs complete all chunks (epochs)
+7. User can invoke IC Ops through UI to stop/resume/clone runs mid-training
+
+### Shared Memory System
+
+RapidFire uses shared memory (`utils/shm_manager.py`) to avoid disk I/O bottlenecks:
+- Model checkpoints stored in shared memory between chunks (configurable via `USE_SHARED_MEMORY`)
+- Registry tracks which models are in memory
+- Process locks prevent concurrent access issues
+- Fallback to disk for larger models
+
+### Interactive Control (IC Ops)
+
+Unique feature enabling real-time experiment control:
+- **Stop**: Pause a run, saves checkpoint
+- **Resume**: Restart a stopped run from checkpoint
+- **Clone**: Create new run from existing, optionally warm-start from parent's weights
+- **Delete**: Remove unwanted runs
+
+Implemented via database state changes that Controller/Workers poll.
+
+## Directory Structure
+
+```
+rapidfireai/
+├── automl/           # Grid search, random search, AutoML algorithms
+├── backend/          # Controller, Scheduler, Worker, Chunks
+├── db/               # SQLite database interface
+├── dispatcher/       # Flask REST API for UI
+├── frontend/         # React dashboard (MLflow fork with IC Ops)
+├── ml/               # Trainer classes, checkpoint utils, callbacks
+├── utils/            # Logging, MLflow manager, shared memory, serialization
+├── experiment.py     # Main Experiment class (user-facing API)
+├── cli.py            # CLI commands (rapidfireai start/stop/init/doctor)
+├── start.sh          # Production server startup script
+├── start_dev.sh      # Development mode startup script
+└── version.py        # Version number
+```
+
+## Key Concepts
+
+### Chunk-Based Training
+
+Instead of training one model at a time for full epochs, RapidFire splits datasets into chunks and interleaves training:
+- Dataset divided into N chunks (user configurable)
+- Multiple runs train on different chunks concurrently
+- Scheduler ensures fair distribution across GPUs
+- Enables side-by-side comparison of hyperparameters with minimal latency
+
+### Run Configuration
+
+Runs are created from parameter configurations:
+- Single dict: creates one run
+- AutoML algorithms (GridSearch, RandomSearch): create multiple runs
+- Each run gets unique ID, tracked in database
+- Supports warm starting from parent runs (clone-modify)
+
+### Task System
+
+Database tracks tasks for coordination:
+- **ExperimentTask**: High-level experiment state
+- **ControllerTask**: Controller operations (create_models, schedule, etc.)
+- **WorkerTask**: Worker operations (fit, validate, etc.)
+- Status: PENDING → IN_PROGRESS → COMPLETED/FAILED
+
+## MLflow Integration
+
+RapidFire wraps MLflow for experiment tracking:
+- Each RapidFire Experiment maps to an MLflow experiment
+- Runs tracked with metrics, parameters, artifacts
+- Checkpoints saved as MLflow artifacts
+- UI extends MLflow with IC Ops panel
+- Access MLflow directly at `http://localhost:5002`
+
+## Development Notes
+
+### Python Version
+
+Requires Python 3.12.x (specified in pyproject.toml and README).
+
+### Frontend Development
+
+The frontend is a fork of MLflow. For frontend-specific guidance, see `rapidfireai/frontend/CLAUDE.md`.
+
+To run frontend in development mode with hot reload:
+```bash
+cd rapidfireai/frontend
+node ./yarn/releases/yarn-4.9.1.cjs start  # Runs on localhost:3000
+```
+
+### Database Schema
+
+Defined in `db/*.sql` files. Tables include:
+- experiments: Experiment metadata and paths
+- runs: Run configurations, status, metrics
+- tasks: Task queue for controller-worker coordination
+- checkpoints: Checkpoint locations and metadata
+
+### Environment Variables
+
+- `RF_EXPERIMENT_PATH`: Base path for experiments (default: `./rapidfire_experiments`)
+- `RF_TUTORIAL_PATH`: Path for tutorial notebooks (default: `./tutorial_notebooks`)
+- `MLFLOW_URL`: MLflow tracking server URL (default: `http://localhost:5002`)
+- `USE_SHARED_MEMORY`: Enable shared memory for checkpoints (default: True)
+
+### Logging
+
+Multi-logger system using loguru:
+- `experiment`: Experiment-level logs
+- `controller`: Controller operations
+- `worker_{N}`: Per-worker training logs
+- `user`: User-facing messages
+- `interactive-control`: IC Ops operations
+
+Logs written to experiment directory.
+
+### Testing Notebooks
+
+Tutorial notebooks in `tutorial_notebooks/` demonstrate usage:
+- Require HuggingFace token for model downloads
+- Run via `jupyter notebook` or IDE with proper kernel
+- Cannot run directly from CLI due to multiprocessing restrictions
+
+## Common Patterns
+
+### Creating an Experiment
+
+```python
+from rapidfireai import Experiment
+
+exp = Experiment("my_experiment")
+exp.run_fit(
+    param_config=config_dict_or_automl,
+    create_model_fn=my_model_factory,
+    train_dataset=train_data,
+    eval_dataset=eval_data,
+    num_chunks=8,
+    seed=42
+)
+results_df = exp.get_results()
+```
+
+### Defining Model Factory
+
+```python
+def create_model_fn(config):
+    # config contains hyperparameters for this run
+    model = YourModel(**config)
+    return model, optimizer, loss_fn, trainer_config
+```
+
+### AutoML Usage
+
+```python
+from rapidfireai.automl import GridSearch
+
+param_config = GridSearch({
+    'learning_rate': [1e-4, 1e-5, 1e-6],
+    'batch_size': [8, 16],
+    'epochs': [3]
+})
+```
+
+## Git Workflow
+
+Current branch: `feat/enable-colab`
+Main branch: `main`
+
+Use standard PR workflow to merge features into main.
+
+## Dependencies
+
+Core dependencies (see pyproject.toml for full list):
+- torch >= 2.8.0
+- transformers >= 4.55.2
+- peft >= 0.17.0
+- trl == 0.21.0
+- mlflow >= 3.2.0
+- flask >= 3.1.1
+
+Dev dependencies:
+- pytest >= 8.4.1
+- black >= 21.0
+- ruff (via ruff.toml)
+- mypy >= 0.800
+
+## Troubleshooting
+
+### GPU Issues
+
+Run `rapidfireai doctor` to diagnose:
+- CUDA installation
+- GPU availability
+- Driver version compatibility
+
+### Port Conflicts
+
+Common ports:
+- 3000: Frontend dashboard
+- 5002: MLflow tracking server
+- 8080: Dispatcher API
+
+Use port killing commands above if conflicts occur.
+
+### Multiprocessing Issues
+
+RapidFire uses `spawn` method for multiprocessing. Notebooks must be run through IDE or Jupyter, not CLI.
diff --git a/rapidfireai/automl/CLAUDE.md b/rapidfireai/automl/CLAUDE.md
@@ -0,0 +1,314 @@
+# CLAUDE.md - AutoML
+
+This file provides guidance for working with the AutoML search algorithms in RapidFire AI.
+
+## Overview
+
+The automl module provides search algorithms for hyperparameter tuning and configuration exploration. Instead of manually creating runs one-by-one, users can specify search spaces and let RapidFire generate multiple configurations automatically.
+
+## Files
+
+### base.py
+**Purpose**: Abstract base class for all AutoML algorithms
+
+**Key Responsibilities**:
+- Defines common interface for AutoML algorithms
+- Validates trainer types (SFT, DPO, GRPO)
+- Normalizes config inputs (list vs single config)
+- Enforces that all configs are `RFModelConfig` instances
+
+**Key Methods**:
+- `get_runs(seed)`: Abstract method that subclasses implement to generate run configurations
+- `_validate_configs()`: Ensures all configs are RFModelConfig instances
+- `_normalize_configs()`: Converts various input formats to list of configs
+
+**Usage Pattern**:
+```python
+class MySearchAlgorithm(AutoMLAlgorithm):
+    def get_runs(self, seed):
+        # Generate list of config dicts
+        return [config_dict_1, config_dict_2, ...]
+```
+
+### grid_search.py
+**Purpose**: Exhaustive grid search over hyperparameter combinations
+
+**Key Responsibilities**:
+- Generates all possible combinations from parameter grid
+- Uses itertools.product for Cartesian product
+- Supports nested parameter spaces via `RFModelConfig`
+
+**Key Methods**:
+- `__init__(configs, trainer_type, num_runs)`: Takes list of `RFModelConfig` with parameter lists
+- `get_runs(seed)`: Generates all combinations (seed unused for deterministic search)
+
+**Usage Example**:
+```python
+from rapidfireai.automl import GridSearch, RFModelConfig
+
+config = RFModelConfig(
+    training_args={
+        'learning_rate': [1e-4, 1e-5, 1e-6],
+        'per_device_train_batch_size': [8, 16],
+        'num_train_epochs': [3],
+    },
+    peft_params={
+        'r': [8, 16],
+        'lora_alpha': [32],
+    }
+)
+
+grid_search = GridSearch(configs=[config], trainer_type="SFT")
+# Generates 3 * 2 * 1 * 2 * 1 = 12 runs
+```
+
+**Notes**:
+- Number of runs = product of all parameter list lengths
+- Can explode quickly with many parameters
+- Deterministic (same configs every time)
+
+### random_search.py
+**Purpose**: Random sampling from hyperparameter distributions
+
+**Key Responsibilities**:
+- Randomly samples from parameter distributions
+- Supports discrete (list) and continuous (distribution) parameters
+- Uses seed for reproducibility
+- Limits number of samples via `num_runs`
+
+**Key Methods**:
+- `__init__(configs, trainer_type, num_runs)`: Takes configs with distributions and sample count
+- `get_runs(seed)`: Generates `num_runs` random samples using seed
+- `_sample_from_config()`: Samples single config from distributions
+
+**Usage Example**:
+```python
+from rapidfireai.automl import RandomSearch, RFModelConfig, distributions
+
+config = RFModelConfig(
+    training_args={
+        'learning_rate': distributions.loguniform(1e-6, 1e-3),
+        'per_device_train_batch_size': [8, 16, 32],  # discrete
+        'num_train_epochs': [3],
+    }
+)
+
+random_search = RandomSearch(configs=[config], trainer_type="SFT", num_runs=10)
+# Generates 10 randomly sampled runs
+```
+
+**Distribution Types** (from `datatypes.py`):
+- `uniform(low, high)`: Uniform distribution
+- `loguniform(low, high)`: Log-uniform (good for learning rates)
+- `randint(low, high)`: Random integer
+- Lists: Uniform random choice from list
+
+### model_config.py
+**Purpose**: Configuration container for model and training parameters
+
+**Key Responsibilities**:
+- Wraps all parameters needed to create a trainer
+- Supports trainer_type, training_args, peft_params, additional_kwargs
+- Used by AutoML algorithms to define search spaces
+- Validates parameter structure
+
+**Key Attributes**:
+- `trainer_type`: "SFT", "DPO", or "GRPO"
+- `training_args`: Dict of HuggingFace TrainingArguments
+- `peft_params`: Dict of PEFT/LoRA config (optional)
+- `additional_kwargs`: Extra kwargs for trainer (e.g., compute_metrics, formatting_func)
+
+**Usage**:
+```python
+config = RFModelConfig(
+    trainer_type="SFT",
+    training_args={
+        'learning_rate': 1e-5,
+        'num_train_epochs': 3,
+    },
+    peft_params={
+        'r': 8,
+        'lora_alpha': 32,
+        'target_modules': ['q_proj', 'v_proj'],
+    },
+    additional_kwargs={
+        'compute_metrics': my_metrics_fn,
+    }
+)
+```
+
+### datatypes.py
+**Purpose**: Type definitions and distribution classes for parameter sampling
+
+**Key Classes**:
+- `List`: Wrapper for list of values (discrete choice)
+- `Distribution`: Base class for continuous distributions
+- `uniform`, `loguniform`, `randint`: Specific distribution implementations
+
+**Usage**:
+```python
+from rapidfireai.automl.datatypes import uniform, loguniform
+
+lr = loguniform(1e-6, 1e-3)  # Log-uniform between 1e-6 and 1e-3
+batch_size = List([8, 16, 32])  # Discrete choice
+```
+
+## Key Concepts
+
+### Parameter Space Definition
+Two ways to specify parameter ranges:
+
+1. **Grid Search**: Lists of discrete values
+```python
+'learning_rate': [1e-4, 1e-5, 1e-6]  # Try all three
+```
+
+2. **Random Search**: Distributions or lists
+```python
+'learning_rate': loguniform(1e-6, 1e-3)  # Sample from distribution
+'batch_size': [8, 16, 32]  # Random choice from list
+```
+
+### config_leaf Format
+The output of `get_runs()` is a list of `config_leaf` dicts:
+```python
+config_leaf = {
+    'trainer_type': 'SFT',
+    'training_args': {
+        'learning_rate': 1e-5,
+        'per_device_train_batch_size': 8,
+        # ... other args
+    },
+    'peft_params': {
+        'r': 8,
+        'lora_alpha': 32,
+        # ... other peft args
+    },
+    'additional_kwargs': {
+        'compute_metrics': fn,
+    }
+}
+```
+
+This dict is stored in the database as `config_leaf` column and passed to `create_trainer_instance()`.
+
+### Seed Handling
+- Seed passed to `get_runs(seed)` by Controller
+- Used for reproducibility in RandomSearch
+- GridSearch ignores seed (deterministic)
+- Same seed = same random samples
+
+## Common Patterns
+
+### Using with Experiment
+```python
+from rapidfireai import Experiment
+from rapidfireai.automl import GridSearch, RFModelConfig
+
+config = RFModelConfig(...)
+grid_search = GridSearch(configs=[config], trainer_type="SFT")
+
+exp = Experiment("my_experiment")
+exp.run_fit(
+    param_config=grid_search,  # Pass AutoML algorithm
+    create_model_fn=my_model_fn,
+    train_dataset=train_data,
+    eval_dataset=eval_data,
+    num_chunks=8,
+    seed=42
+)
+```
+
+### Multiple Config Spaces
+```python
+# Search over two different model architectures
+config1 = RFModelConfig(...)  # Model A params
+config2 = RFModelConfig(...)  # Model B params
+
+grid_search = GridSearch(configs=[config1, config2], trainer_type="SFT")
+# Will search over both config spaces
+```
+
+### Hybrid Search
+```python
+# Some params grid, some random
+config = RFModelConfig(
+    training_args={
+        'learning_rate': loguniform(1e-6, 1e-3),  # Random
+        'num_train_epochs': [1, 3, 5],  # Grid (if using RandomSearch, random choice)
+    }
+)
+
+random_search = RandomSearch(configs=[config], num_runs=20)
+```
+
+## Adding New Search Algorithms
+
+1. **Create new file** (e.g., `bayesian_optimization.py`)
+
+2. **Subclass AutoMLAlgorithm**:
+```python
+from rapidfireai.automl.base import AutoMLAlgorithm
+
+class BayesianOptimization(AutoMLAlgorithm):
+    def __init__(self, configs, trainer_type="SFT", num_runs=10):
+        super().__init__(configs, trainer_type, num_runs)
+        # Additional initialization
+
+    def get_runs(self, seed):
+        # Implement search logic
+        configs = []
+        for i in range(self.num_runs):
+            # Sample config based on previous results
+            config = self._sample_config()
+            configs.append(config)
+        return configs
+```
+
+3. **Update `__init__.py`**:
+```python
+from .bayesian_optimization import BayesianOptimization
+
+__all__ = ['AutoMLAlgorithm', 'GridSearch', 'RandomSearch', 'BayesianOptimization', ...]
+```
+
+4. **Test**:
+```python
+bo = BayesianOptimization(configs=[config], num_runs=10)
+runs = bo.get_runs(seed=42)
+assert len(runs) == 10
+```
+
+## Integration with Controller
+
+1. User passes AutoML algorithm to `Experiment.run_fit(param_config=grid_search)`
+2. Controller detects it's an AutoML instance (not plain dict)
+3. Controller calls `get_runs(seed)` to generate configs
+4. Controller creates runs in DB for each config
+5. Workers train all configs concurrently (chunk-based)
+
+Flow:
+```
+User → Experiment.run_fit(param_config=AutoMLAlgorithm)
+     → Controller._create_models(param_config, ...)
+     → get_runs(seed) → [config1, config2, ...]
+     → db.create_run() for each config
+     → Scheduler assigns to workers
+```
+
+## Testing
+
+Manual testing:
+```python
+from rapidfireai.automl import GridSearch, RFModelConfig
+
+config = RFModelConfig(
+    training_args={'learning_rate': [1e-4, 1e-5]},
+)
+grid = GridSearch(configs=[config])
+runs = grid.get_runs(seed=42)
+print(len(runs))  # Should be 2
+print(runs[0])    # First config
+```
+
+Integration testing via tutorial notebooks with AutoML examples.
diff --git a/rapidfireai/backend/CLAUDE.md b/rapidfireai/backend/CLAUDE.md
@@ -0,0 +1,170 @@
+# CLAUDE.md - Backend
+
+This file provides guidance for working with the backend components of RapidFire AI.
+
+## Overview
+
+The backend module contains the core orchestration logic for RapidFire's chunk-based concurrent training system. It coordinates between the user's process (Controller), scheduling logic (Scheduler), actual training execution (Worker), and dataset chunking (DatasetChunks).
+
+## Files
+
+### controller.py
+**Purpose**: Central orchestrator running in the user's process
+
+**Key Responsibilities**:
+- Creates runs from parameter configurations (single configs, AutoML algorithms, IC Ops clones)
+- Spawns and manages Worker processes (one per GPU)
+- Runs the main scheduling loop that assigns (run_id, chunk_id) pairs to available workers
+- Handles Interactive Control Operations (stop, resume, clone-modify, delete)
+- Monitors training progress and coordinates epoch transitions
+- Manages shared memory for model checkpoints
+- Logs to MLflow and database
+
+**Key Methods**:
+- `run_fit()`: Main entry point, coordinates entire training lifecycle
+- `_create_models()`: Creates run entries in DB from param configs
+- `_schedule_and_monitor()`: Main loop that calls Scheduler and dispatches tasks to workers
+- `_handle_ic_ops()`: Polls DB for IC Ops requests and executes them
+- `_handle_clone_modify()`, `_handle_stop()`, `_handle_resume()`, `_handle_delete()`: IC Ops handlers
+
+**Patterns**:
+- Uses multiprocessing with 'spawn' method (set in `__init__`)
+- Polls database for task status and IC Ops requests
+- Coordinates with Workers via database task table
+- Uses SharedMemoryManager for checkpoint storage
+
+### scheduler.py
+**Purpose**: Pure scheduling algorithm that assigns runs to workers
+
+**Key Responsibilities**:
+- Maintains state of which workers are busy and which runs have completed which chunks
+- Implements round-robin scheduling for fairness
+- Ensures runs don't execute on multiple workers simultaneously
+- Tracks progress (chunks completed per run)
+- Handles run addition/removal (for IC Ops)
+
+**Key Methods**:
+- `schedule()`: Returns next (run_id, worker_id, chunk_id) assignment or None if all done
+- `add_run()`: Add new run to scheduler (for resume/clone IC Ops)
+- `remove_run()`: Remove run from scheduler (for stop/delete IC Ops)
+- `reset_run()`: Reset run progress at epoch boundaries
+- `set_completed_task()`: Mark a worker's task as completed
+
+**Return Values from `schedule()`**:
+- `{run_id: X, worker_id: Y, chunk_id: Z, is_last_chunk: bool}` - Valid assignment
+- `{run_id: None, ...}` - All runs completed all chunks (termination)
+- `{run_id: -1, ...}` - All workers busy or no available runs (wait)
+
+**Design Notes**:
+- Zero-indexed workers and chunks, one-indexed run_ids
+- Stateless pure scheduling logic (state passed in constructor)
+- No I/O or side effects, just assignment logic
+
+### worker.py
+**Purpose**: Separate GPU process that executes actual training
+
+**Key Responsibilities**:
+- Polls database for assigned tasks (run_id, chunk_id pairs)
+- Loads model from shared memory or disk checkpoint
+- Trains on the assigned data chunk using appropriate Trainer (SFT/DPO/GRPO)
+- Saves checkpoint back to shared memory/disk after chunk
+- Reports metrics to MLflow and updates database task status
+- Handles graceful shutdown on signals
+
+**Key Methods**:
+- `run()`: Main worker loop - polls for tasks, executes them, reports completion
+- `run_fit()`: Executes training for one (run_id, chunk_id) pair
+- `load_datasets()`: Loads train/eval datasets from disk (serialized by Controller)
+
+**Lifecycle**:
+1. Worker spawned by Controller with (worker_id, shared memory objects, shutdown_event)
+2. Worker enters main loop in `run()` method
+3. Polls database for tasks with status=SCHEDULED and worker_id=self.worker_id
+4. On task found: loads model, trains chunk, saves checkpoint, marks task COMPLETED
+5. Repeats until shutdown_event is set
+
+**Patterns**:
+- Each Worker has exclusive access to one GPU (via CUDA_VISIBLE_DEVICES)
+- Uses SharedMemoryManager to load/save checkpoints
+- Creates trainer instance per chunk (via `ml/trainer.py`)
+- Redirects stdout/stderr during training to avoid pollution
+
+### chunks.py
+**Purpose**: Utility class for splitting datasets into chunks
+
+**Key Responsibilities**:
+- Divides dataset into N chunks with even distribution
+- Handles batch size alignment (chunks align with batch boundaries)
+- Supports offset for resuming training mid-epoch
+- Validates inputs (chunk count, batch size, offset)
+
+**Key Methods**:
+- `__init__()`: Creates chunk boundaries based on dataset size, num_chunks, batch_size
+- `get_chunk_indices()`: Returns (start_idx, end_idx) for a given chunk_id
+- `_create_base_chunk_indices()`: Distributes batches evenly across chunks
+- `_apply_offset()`: Applies modulo offset for resume functionality
+
+**Usage Pattern**:
+```python
+chunker = DatasetChunks(dataset_size=1000, n_chunks=4, batch_size=8)
+start, end = chunker.get_chunk_indices(chunk_id=0)
+chunk_data = dataset[start:end]
+```
+
+**Design Notes**:
+- Chunks distribute batches, not individual examples
+- Last chunk may be smaller if batches don't divide evenly
+- Offset wraps around with modulo for mid-epoch resume
+- Raises ValueError for invalid inputs (too many chunks, bad offsets, etc.)
+
+## Key Interactions
+
+1. **Controller → Scheduler**: Controller calls `scheduler.schedule()` to get next assignment
+2. **Controller → Worker**: Controller creates WorkerTask in DB, Worker polls and executes
+3. **Controller → SharedMemory**: Controller saves initial models to SHM
+4. **Worker → SharedMemory**: Worker loads models from SHM, trains, saves back to SHM
+5. **Worker → Database**: Worker updates task status (IN_PROGRESS → COMPLETED)
+6. **Controller → Database**: Controller polls for IC Ops requests, updates run status
+
+## State Management
+
+**Run Status Flow**:
+- NEW → ONGOING → COMPLETED/FAILED
+- ONGOING → STOPPED (IC Ops stop)
+- STOPPED → ONGOING (IC Ops resume)
+- Any → KILLED (IC Ops delete)
+
+**Task Status Flow**:
+- SCHEDULED → IN_PROGRESS → COMPLETED/FAILED
+
+**Scheduler State**:
+- `worker_running_current_run`: Maps worker_id to current run_id (-1 if idle)
+- `run_visited_num_chunks`: Maps run_id to number of chunks completed
+
+## Testing
+
+Run tests with:
+```bash
+pytest tests/test_chunks.py
+```
+
+## Common Patterns
+
+### Adding IC Ops Support
+1. Add handler method in Controller (e.g., `_handle_new_op()`)
+2. Update `_handle_ic_ops()` to check for new op type in DB
+3. Update Scheduler if state changes needed (e.g., add_run/remove_run)
+4. Add dispatcher endpoint to trigger IC Op
+5. Update database schema if needed (tables.sql)
+
+### Debugging Scheduling Issues
+- Add logging in `scheduler.schedule()` to see assignment decisions
+- Check `worker_running_current_run` and `run_visited_num_chunks` state
+- Verify task status transitions in database
+- Check Worker logs for task execution timing
+
+### Performance Tuning
+- Adjust `num_chunks` to balance concurrency vs checkpoint overhead
+- Monitor shared memory usage with `SharedMemoryManager` logging
+- Check scheduling fairness with chunk completion timestamps
+- Profile Worker task execution time vs scheduling loop latency
diff --git a/rapidfireai/db/CLAUDE.md b/rapidfireai/db/CLAUDE.md
@@ -0,0 +1,249 @@
+# CLAUDE.md - Database
+
+This file provides guidance for working with the database layer of RapidFire AI.
+
+## Overview
+
+The db module provides the persistence layer for RapidFire using SQLite. It stores experiment metadata, run configurations, task scheduling state, and checkpoint locations. The design emphasizes async operations and clean separation between the database interface and domain logic.
+
+## Files
+
+### rf_db.py
+**Purpose**: High-level database API with domain-specific operations
+
+**Key Responsibilities**:
+- Implements all CRUD operations for experiments, runs, tasks, and IC Ops
+- Handles serialization/deserialization of complex objects (using `encode_payload`/`decode_db_payload`)
+- Manages experiment lifecycle (create, activate, reset, cleanup)
+- Provides query methods for Controller, Worker, and Dispatcher
+- Enforces business logic constraints (e.g., can't IC Ops on KILLED runs)
+
+**Key Methods - Experiments**:
+- `create_experiment()`: Create new experiment entry
+- `get_running_experiment()`: Get currently active experiment
+- `set_experiment_status()`: Update experiment status
+- `reset_all_tables()`: Truncate tables (cleanup)
+- `reset_experiment_states()`: Mark in-progress tasks as failed (crash recovery)
+
+**Key Methods - Runs**:
+- `create_run()`: Create run with config, status, source
+- `get_run()`: Get run by ID
+- `get_all_runs()`: Get all runs with metrics
+- `get_runs_by_status()`: Filter runs by status(es)
+- `set_run_status()`: Update run status
+- `set_run_ended_by()`: Mark how run ended (completed/failed/killed)
+- `update_run_metrics()`: Update training metrics
+
+**Key Methods - Tasks**:
+- `create_worker_task()`: Create task for worker to execute
+- `get_next_worker_task()`: Poll for next task (used by Worker)
+- `set_worker_task_status()`: Update task status
+- `get_controller_task()`: Get current controller task
+- `set_controller_task()`: Update controller task
+
+**Key Methods - Interactive Control**:
+- `request_clone_modify()`: Create IC Ops request for clone
+- `request_stop()`: Request run stop
+- `request_resume()`: Request run resume
+- `request_delete()`: Request run deletion
+- `get_ic_ops_request()`: Poll for IC Ops requests (used by Controller)
+- `mark_ic_ops_completed()`: Mark IC Op as processed
+
+**Serialization**:
+- Complex objects (configs, datasets, models) stored as BLOBs
+- Uses `encode_payload()` from utils/serialize.py before storing
+- Uses `decode_db_payload()` when reading back
+- Handles torch tensors, datasets, and arbitrary Python objects via dill
+
+**Patterns**:
+- All methods use `db.execute()` with parameterized queries (SQL injection safe)
+- Commit=True by default for most operations
+- Returns dicts or lists of dicts (not raw tuples)
+- Raises DBException on errors with context
+
+### db_interface.py
+**Purpose**: Low-level SQLite connection wrapper
+
+**Key Responsibilities**:
+- Manages SQLite connection lifecycle
+- Provides generic `execute()` method for queries
+- Handles connection pooling and thread safety
+- Converts query results to dicts
+
+**Key Methods**:
+- `execute()`: Execute parameterized query, return results as list of dicts
+- `close()`: Close database connection
+
+**Design Notes**:
+- Uses sqlite3 row_factory for dict results
+- Single connection per RfDb instance
+- Thread-safe via SQLite's default settings
+
+### tables.sql
+**Purpose**: Database schema definition
+
+**Tables**:
+
+**experiments**:
+- `experiment_id` (PK): Unique experiment identifier
+- `experiment_name`: User-provided name
+- `status`: ExperimentStatus enum (NEW, RUNNING, COMPLETED, FAILED)
+- `experiments_path`: Base path for experiment artifacts
+- `created_at`, `updated_at`: Timestamps
+
+**runs**:
+- `run_id` (PK): Unique run identifier
+- `experiment_id` (FK): Parent experiment
+- `run_name`: Generated name (e.g., "run_1")
+- `mlflow_run_id`: MLflow tracking ID
+- `status`: RunStatus enum (NEW, ONGOING, COMPLETED, FAILED, STOPPED, KILLED)
+- `source`: RunSource enum (USER, CLONE_MODIFY)
+- `ended_by`: RunEndedBy enum (COMPLETED, FAILED, KILLED, STOPPED)
+- `parent_run_id`: For cloned runs
+- `warm_start`: Boolean flag for clone-modify
+- `config_leaf`: Serialized run configuration (BLOB)
+- `seed`: Random seed for reproducibility
+- `num_chunks`: Number of data chunks
+- `current_chunk`, `current_epoch`: Progress tracking
+- `metrics`: JSON string of training metrics
+- `created_at`, `updated_at`: Timestamps
+
+**worker_task**:
+- `task_id` (PK): Unique task identifier
+- `run_id` (FK): Run to execute
+- `worker_id`: GPU worker assignment
+- `chunk_id`: Data chunk to train on
+- `epoch`: Current epoch number
+- `status`: TaskStatus enum (SCHEDULED, IN_PROGRESS, COMPLETED, FAILED)
+- `created_at`, `updated_at`: Timestamps
+
+**controller_progress**:
+- Tracks controller state (single row table)
+- `task`: ControllerTask enum
+- `status`: TaskStatus enum
+
+**worker_progress**:
+- Tracks per-worker state
+- `worker_id` (PK): Worker identifier
+- `task`: WorkerTask enum
+- `status`: TaskStatus enum
+
+**interactive_control**:
+- `ic_id` (PK): IC Ops request identifier
+- `run_id` (FK): Target run
+- `operation`: IC Ops type (CLONE_MODIFY, STOP, RESUME, DELETE)
+- `status`: TaskStatus enum
+- `config_leaf`: New config for clone-modify (BLOB)
+- `warm_start`: Boolean for clone-modify
+- `created_at`, `updated_at`: Timestamps
+
+## Key Concepts
+
+### Status Enums
+Defined in `utils/constants.py`:
+- **ExperimentStatus**: NEW, RUNNING, COMPLETED, FAILED
+- **RunStatus**: NEW, ONGOING, COMPLETED, FAILED, STOPPED, KILLED
+- **RunSource**: USER, CLONE_MODIFY
+- **RunEndedBy**: COMPLETED, FAILED, KILLED, STOPPED
+- **TaskStatus**: PENDING, SCHEDULED, IN_PROGRESS, COMPLETED, FAILED
+
+### Transaction Model
+- Most operations are auto-commit (commit=True)
+- No explicit transaction management (SQLite handles implicitly)
+- Crash recovery via `reset_experiment_states()` on startup
+
+### Query Patterns
+```python
+# Parameterized query (safe)
+query = "SELECT * FROM runs WHERE run_id = ?"
+result = self.db.execute(query, (run_id,))
+
+# With commit
+query = "UPDATE runs SET status = ? WHERE run_id = ?"
+self.db.execute(query, (new_status, run_id), commit=True)
+```
+
+## Common Operations
+
+### Creating a Run
+```python
+run_id = db.create_run(
+    experiment_id=1,
+    run_name="run_1",
+    mlflow_run_id="abc123",
+    config_leaf=encode_payload(config_dict),
+    source=RunSource.USER,
+    seed=42,
+    num_chunks=8
+)
+```
+
+### Polling for Tasks (Worker)
+```python
+task = db.get_next_worker_task(worker_id=0)
+if task:
+    db.set_worker_task_status(task['task_id'], TaskStatus.IN_PROGRESS)
+    # ... do work ...
+    db.set_worker_task_status(task['task_id'], TaskStatus.COMPLETED)
+```
+
+### IC Ops Flow (Controller)
+```python
+# User triggers stop via UI → Dispatcher → Database
+db.request_stop(run_id=5)
+
+# Controller polls and processes
+ic_ops = db.get_ic_ops_request()
+for op in ic_ops:
+    if op['operation'] == 'STOP':
+        # ... handle stop ...
+        db.mark_ic_ops_completed(op['ic_id'])
+```
+
+### Cleanup Between Experiments
+```python
+db.reset_all_tables(experiments_table=False)  # Keep experiments table
+db.set_experiment_status(exp_id, ExperimentStatus.COMPLETED)
+```
+
+## Testing Database Changes
+
+1. Modify `tables.sql` if adding/changing tables
+2. Delete existing `rapidfire.db` file to force recreation
+3. Run `db.create_tables()` to apply schema
+4. Test with `pytest` or manual verification
+5. Ensure backward compatibility with existing experiments
+
+## Performance Considerations
+
+- SQLite write contention: Workers only write task status updates
+- Most writes are from Controller (runs, IC Ops, metrics)
+- No indexes beyond PRIMARY KEYs (small data volume)
+- BLOB storage for configs is fine (not queried, only retrieved by PK)
+
+## Common Patterns
+
+### Adding New Table
+1. Add CREATE TABLE to `tables.sql`
+2. Add CRUD methods to `rf_db.py`
+3. Add any enums to `utils/constants.py`
+4. Update `reset_all_tables()` if needed for cleanup
+5. Test with fresh database
+
+### Debugging Database Issues
+```python
+# Check database file location
+import os
+print(os.path.abspath("rapidfire.db"))
+
+# Inspect directly with sqlite3 CLI
+# sqlite3 rapidfire.db
+# .schema
+# SELECT * FROM runs;
+# SELECT * FROM worker_task WHERE status = 'IN_PROGRESS';
+```
+
+### Migration Strategy
+- Currently no migrations (schema assumed stable)
+- Breaking changes require users to reset experiments
+- Future: Add migration system (e.g., Alembic) if needed
diff --git a/rapidfireai/dispatcher/CLAUDE.md b/rapidfireai/dispatcher/CLAUDE.md
@@ -0,0 +1,371 @@
+# CLAUDE.md - Dispatcher
+
+This file provides guidance for working with the dispatcher module of RapidFire AI.
+
+## Overview
+
+The dispatcher is a Flask-based REST API that provides the communication layer between the web UI (frontend) and the RapidFire backend. It exposes endpoints for viewing experiment status, retrieving run information, and triggering Interactive Control Operations (IC Ops).
+
+## Files
+
+### dispatcher.py
+**Purpose**: Flask application with REST endpoints for UI communication
+
+**Key Responsibilities**:
+- Serves REST API for frontend dashboard
+- Provides endpoints for run queries and experiment status
+- Handles IC Ops requests (stop, resume, clone-modify, delete)
+- Returns logs for debugging
+- Manages CORS for local development
+
+**Architecture**:
+- Flask app with CORS enabled for localhost:3000 (frontend dev server)
+- Stateless request handling (reads from database on each request)
+- Returns JSON responses
+- Error handling with try/catch and HTTP status codes
+
+**Route Categories**:
+
+**Health Check**:
+- `GET /dispatcher/health-check`: Server health status
+
+**UI Data Routes**:
+- `GET /dispatcher/get-all-runs`: Retrieve all runs for current experiment
+- `POST /dispatcher/get-run`: Get single run by ID
+- `GET /dispatcher/get-all-experiment-names`: List all experiment names
+- `GET /dispatcher/get-running-experiment`: Get currently active experiment
+
+**Interactive Control Routes**:
+- `POST /dispatcher/clone-modify-run`: Clone run with optional modifications
+- `POST /dispatcher/stop-run`: Stop active run
+- `POST /dispatcher/resume-run`: Resume stopped run
+- `POST /dispatcher/delete-run`: Delete run (mark as KILLED)
+
+**Log Routes**:
+- `POST /dispatcher/get-ic-logs`: Get IC Ops logs
+- `POST /dispatcher/get-experiment-logs`: Get experiment logs
+
+**Key Methods**:
+
+`get_all_runs()`:
+- Returns list of all runs with status, metrics, config
+- Used by dashboard to display run table
+- Includes calculated fields (progress, current_chunk, etc.)
+
+`clone_modify_run(run_id, config_leaf, warm_start)`:
+- Creates IC Ops request in database for clone
+- Controller polls and processes request
+- Returns new run_id or error
+
+`stop_run(run_id)`:
+- Validates run is in stoppable state (ONGOING)
+- Creates IC Ops request in database
+- Controller processes asynchronously
+- Returns success/error status
+
+`resume_run(run_id)`:
+- Validates run is STOPPED
+- Creates IC Ops request in database
+- Controller adds run back to scheduler
+- Returns success/error status
+
+`delete_run(run_id)`:
+- Marks run as KILLED
+- Creates IC Ops request in database
+- Controller removes from scheduler
+- Returns success/error status
+
+**Error Handling**:
+```python
+try:
+    # ... operation ...
+    return jsonify(result), 200
+except Exception as e:
+    logger.error(f"Error: {e}")
+    return jsonify({"error": str(e)}), 500
+```
+
+**CORS Configuration**:
+- Allows origins: localhost:3000, localhost
+- Required for frontend dev server (separate port from backend)
+- Production: frontend built and served from same origin
+
+### gunicorn.conf.py
+**Purpose**: Gunicorn server configuration for production deployment
+
+**Key Settings**:
+- `workers`: Number of worker processes (default: 4)
+- `bind`: Host and port (default: 0.0.0.0:8080)
+- `timeout`: Request timeout (default: 120s)
+- `loglevel`: Log verbosity (default: info)
+
+**Usage**:
+```bash
+gunicorn -c rapidfireai/dispatcher/gunicorn.conf.py rapidfireai.dispatcher.dispatcher:app
+```
+
+**Production Notes**:
+- Multiple workers for load balancing
+- Timeout prevents hanging requests
+- Access logs for monitoring
+
+## API Endpoints Reference
+
+### GET /dispatcher/health-check
+**Response**:
+```json
+"Dispatcher is up and running"
+```
+
+### GET /dispatcher/get-all-runs
+**Response**:
+```json
+[
+  {
+    "run_id": 1,
+    "run_name": "run_1",
+    "status": "ONGOING",
+    "current_chunk": 5,
+    "current_epoch": 0,
+    "metrics": "{\"loss\": 0.5, \"accuracy\": 0.9}",
+    "config_leaf": {...},
+    "source": "USER",
+    "parent_run_id": null,
+    "warm_start": false
+  },
+  ...
+]
+```
+
+### POST /dispatcher/clone-modify-run
+**Request**:
+```json
+{
+  "run_id": 1,
+  "config_leaf": {"learning_rate": 1e-4},
+  "warm_start": true
+}
+```
+**Response**:
+```json
+{
+  "message": "Clone-modify request created",
+  "new_run_id": 5
+}
+```
+
+### POST /dispatcher/stop-run
+**Request**:
+```json
+{
+  "run_id": 1
+}
+```
+**Response**:
+```json
+{
+  "message": "Stop request created successfully"
+}
+```
+
+### POST /dispatcher/resume-run
+**Request**:
+```json
+{
+  "run_id": 1
+}
+```
+**Response**:
+```json
+{
+  "message": "Resume request created successfully"
+}
+```
+
+### POST /dispatcher/delete-run
+**Request**:
+```json
+{
+  "run_id": 1
+}
+```
+**Response**:
+```json
+{
+  "message": "Delete request created successfully"
+}
+```
+
+## Integration with Frontend
+
+Frontend makes HTTP requests to dispatcher:
+```typescript
+// Example: Get all runs
+const response = await fetch('http://localhost:8080/dispatcher/get-all-runs');
+const runs = await response.json();
+
+// Example: Stop run
+await fetch('http://localhost:8080/dispatcher/stop-run', {
+  method: 'POST',
+  headers: {'Content-Type': 'application/json'},
+  body: JSON.stringify({run_id: 5})
+});
+```
+
+Frontend polls `get-all-runs` periodically to update dashboard.
+
+## Integration with Controller
+
+Dispatcher writes IC Ops requests to database:
+```python
+# Dispatcher
+db.request_stop(run_id)
+
+# Controller (polling loop)
+ic_ops = db.get_ic_ops_request()
+for op in ic_ops:
+    if op['operation'] == 'STOP':
+        self._handle_stop(op['run_id'])
+        db.mark_ic_ops_completed(op['ic_id'])
+```
+
+Asynchronous communication via database (no direct RPC).
+
+## Running Dispatcher
+
+**Development**:
+```bash
+# Via start_dev.sh (starts all services)
+./rapidfireai/start_dev.sh start
+
+# Or manually
+python -m flask --app rapidfireai.dispatcher.dispatcher:app run --port 8080
+```
+
+**Production** (via start.sh):
+```bash
+gunicorn -c rapidfireai/dispatcher/gunicorn.conf.py rapidfireai.dispatcher.dispatcher:app
+```
+
+**Testing**:
+```bash
+# Health check
+curl http://localhost:8080/dispatcher/health-check
+
+# Get all runs
+curl http://localhost:8080/dispatcher/get-all-runs
+
+# Stop run
+curl -X POST http://localhost:8080/dispatcher/stop-run \
+  -H "Content-Type: application/json" \
+  -d '{"run_id": 1}'
+```
+
+## Common Patterns
+
+### Adding New Endpoint
+
+1. **Add route in `register_routes()`**:
+```python
+self.app.add_url_rule(
+    f"{route_prefix}/my-endpoint",
+    "my_endpoint",
+    self.my_endpoint,
+    methods=["POST"]
+)
+```
+
+2. **Implement handler method**:
+```python
+def my_endpoint(self) -> tuple[Response, int]:
+    try:
+        data = request.json
+        result = self.db.some_operation(data)
+        return jsonify(result), 200
+    except Exception as e:
+        self._get_logger().error(f"Error: {e}")
+        return jsonify({"error": str(e)}), 500
+```
+
+3. **Update frontend to call endpoint**:
+```typescript
+await fetch('http://localhost:8080/dispatcher/my-endpoint', {
+  method: 'POST',
+  body: JSON.stringify(data)
+});
+```
+
+### Debugging Dispatcher Issues
+
+**Check logs**:
+```bash
+# Dispatcher logs
+cat {experiment_path}/logs/dispatcher.log
+
+# Or watch in real-time
+tail -f {experiment_path}/logs/dispatcher.log
+```
+
+**Test endpoint directly**:
+```bash
+curl -X POST http://localhost:8080/dispatcher/stop-run \
+  -H "Content-Type: application/json" \
+  -d '{"run_id": 1}' \
+  -v
+```
+
+**Check database state**:
+```bash
+sqlite3 rapidfire.db "SELECT * FROM interactive_control ORDER BY created_at DESC LIMIT 5;"
+```
+
+**CORS issues**:
+- Ensure frontend origin in `CORS_ALLOWED_ORIGINS`
+- Check browser console for CORS errors
+- Verify preflight OPTIONS requests succeed
+
+### Error Handling Best Practices
+
+```python
+def endpoint(self) -> tuple[Response, int]:
+    try:
+        # Validate input
+        data = request.json
+        if not data or 'run_id' not in data:
+            return jsonify({"error": "run_id required"}), 400
+
+        # Perform operation
+        result = self.db.some_operation(data['run_id'])
+
+        # Check result
+        if not result:
+            return jsonify({"error": "Operation failed"}), 500
+
+        return jsonify(result), 200
+    except DBException as e:
+        self._get_logger().error(f"DB error: {e}")
+        return jsonify({"error": "Database error"}), 500
+    except Exception as e:
+        self._get_logger().error(f"Unexpected error: {e}")
+        return jsonify({"error": str(e)}), 500
+```
+
+## Performance Considerations
+
+- Dispatcher is stateless (scales horizontally with Gunicorn workers)
+- Database is bottleneck for high request volume (SQLite)
+- Frontend should throttle polling (e.g., 1-2 second intervals)
+- Large run counts may slow `get-all-runs` (consider pagination)
+
+## Security Notes
+
+- No authentication (assumes local/trusted network)
+- No rate limiting (relies on frontend behavior)
+- CORS restricted to localhost (production should tighten)
+- Input validation minimal (assumes trusted clients)
+
+For production deployment, consider adding:
+- API authentication (tokens, JWT)
+- Rate limiting (Flask-Limiter)
+- Input validation (marshmallow, pydantic)
+- HTTPS (reverse proxy like nginx)
diff --git a/rapidfireai/ml/CLAUDE.md b/rapidfireai/ml/CLAUDE.md
@@ -0,0 +1,253 @@
+# CLAUDE.md - ML
+
+This file provides guidance for working with the ML training components of RapidFire AI.
+
+## Overview
+
+The ml module contains the training execution logic that wraps HuggingFace Transformers and TRL trainers. It handles trainer instantiation, checkpoint management, callbacks, and integration with RapidFire's chunk-based training system.
+
+## Files
+
+### trainer.py
+**Purpose**: Creates and configures TRL trainer instances (SFT, DPO, GRPO)
+
+**Key Responsibilities**:
+- Instantiates appropriate trainer type based on config (SFTTrainer, DPOTrainer, GRPOTrainer)
+- Loads model from checkpoint (shared memory or disk)
+- Configures training arguments (batch size, learning rate, gradient accumulation, etc.)
+- Sets up callbacks (MLflow logging, generation metrics, log level control)
+- Handles PEFT (LoRA) configuration if specified
+- Manages reference model for DPO training
+- Restores trainer state (optimizer, scheduler) for resumed runs
+
+**Key Functions**:
+- `create_trainer_instance()`: Main entry point, returns configured trainer
+- `_configure_training_args()`: Merges user args with RapidFire overrides
+- `_create_trainer_config_object()`: Creates SFTConfig/DPOConfig/GRPOConfig
+- `_setup_reference_model()`: Loads reference model for DPO
+- `_prepare_trainer_kwargs()`: Builds kwargs dict for trainer constructor
+- `_setup_callbacks()`: Initializes callbacks (MLflow, generation metrics, log level)
+- `_create_trainer()`: Actually instantiates the trainer object
+- `_restore_trainer_state()`: Restores optimizer/scheduler state for resumed runs
+
+**Trainer Types**:
+- **SFT** (Supervised Fine-Tuning): Standard next-token prediction
+- **DPO** (Direct Preference Optimization): Preference-based training with reference model
+- **GRPO** (Group Relative Policy Optimization): Advanced RL-based training
+
+**Training Args Overrides**:
+RapidFire overrides certain args to ensure chunk-based training works:
+- `output_dir`: Set to experiment-specific path
+- `logging_dir`: Set to experiment-specific tensorboard path
+- `save_strategy`: "no" (checkpoints managed by RapidFire)
+- `evaluation_strategy`: "no" or "epoch" (custom eval via callbacks)
+- `max_steps`: Calculated based on chunk size
+- `logging_steps`: Set to chunk-sized batches
+
+**PEFT Integration**:
+If `config_leaf['peft_params']` is provided:
+- Wraps model with PEFT adapter (LoRA)
+- Loads/saves adapter weights separately from base model
+- Uses `get_peft_model_state_dict()` and `set_peft_model_state_dict()`
+
+**Patterns**:
+- Expects `TrainerConfig` object with all necessary info (run_id, worker_id, config_leaf, etc.)
+- Returns tuple of (trainer, status_string)
+- Handles both fresh runs and resumed runs (chunk_id > 0)
+- Uses `USE_SHARED_MEMORY` flag to decide checkpoint loading strategy
+
+### checkpoint_utils.py
+**Purpose**: Checkpoint loading, saving, and restoration
+
+**Key Responsibilities**:
+- Save/load model checkpoints to/from shared memory
+- Save/load model checkpoints to/from disk
+- Restore trainer state (optimizer, scheduler, RNG) for resumed runs
+- Handle PEFT adapter checkpoints separately from base models
+- Move tensors between CPU and GPU for memory efficiency
+
+**Key Functions - Shared Memory**:
+- `save_model_to_shared_memory()`: Store model weights in SHM
+- `save_checkpoint_to_shared_memory()`: Store model + optimizer state in SHM
+- `load_checkpoint_from_shared_memory()`: Load model from SHM registry
+- `restore_trainer_from_shared_memory()`: Restore trainer state from SHM
+
+**Key Functions - Disk**:
+- `save_checkpoint_to_disk()`: Save checkpoint to experiment directory
+- `load_checkpoint_from_disk()`: Load checkpoint from disk
+- `restore_trainer_from_disk()`: Restore trainer state from disk checkpoint
+- `load_or_create_ref_model()`: Load reference model for DPO (always from disk)
+
+**Key Functions - Utilities**:
+- `move_tensors_to_cpu()`: Move all tensors in dict to CPU (for SHM storage)
+- `move_tensors_to_device()`: Move all tensors to specified device
+- `ensure_gradient_compatibility()`: Fix gradient dtype mismatches
+- `_get_checkpoint_path()`: Generate checkpoint filename path
+
+**Checkpoint Structure**:
+```python
+checkpoint = {
+    'model_state_dict': model.state_dict(),
+    'optimizer_state_dict': trainer.optimizer.state_dict(),
+    'scheduler_state_dict': trainer.lr_scheduler.state_dict(),
+    'rng_state': torch.get_rng_state(),
+    'cuda_rng_state': torch.cuda.get_rng_state(),
+    'epoch': current_epoch,
+    'global_step': trainer.state.global_step,
+}
+```
+
+**Shared Memory Registry**:
+- Key format: `f"{run_id}_model"`, `f"{run_id}_checkpoint"`
+- Stores model on CPU to avoid GPU memory issues
+- Uses `SharedMemoryManager` for access coordination
+
+**Disk Checkpoint Paths**:
+- Pattern: `{experiment_path}/runs/run_{run_id}/checkpoints/checkpoint_chunk_{chunk_id}.pt`
+- Saved after each chunk completion
+- Used when SHM disabled or checkpoint too large
+
+**PEFT Handling**:
+- PEFT adapters saved separately: `checkpoint['adapter_state_dict']`
+- Base model not saved (only adapters)
+- Load base model fresh, then apply saved adapter
+
+### callbacks.py
+**Purpose**: Custom Transformers callbacks for RapidFire integration
+
+**Key Responsibilities**:
+- Log training metrics to MLflow
+- Compute generation-based metrics during evaluation
+- Control log verbosity during training
+
+**Callbacks**:
+
+**GenerationMetricsCallback**:
+- Generates text during evaluation to compute quality metrics
+- Uses user-provided `compute_metrics` function
+- Logs generation metrics to MLflow (e.g., BLEU, ROUGE, custom metrics)
+- Batches generation for efficiency
+- Supports custom generation configs (temperature, top_p, max_tokens)
+
+**MLflowLoggingCallback**:
+- Logs training metrics (loss, learning rate, grad norm) to MLflow
+- Handles step offset for resumed runs (continued step numbering)
+- Filters out None values and non-numeric metrics
+- Logs at appropriate intervals based on `logging_steps`
+
+**LogLevelCallback**:
+- Temporarily reduces log verbosity during training
+- Prevents console spam from Transformers
+- Restores original log level after training
+- Uses `transformers.logging.set_verbosity()`
+
+**Usage Pattern**:
+```python
+callbacks = [
+    MLflowLoggingCallback(mlflow_manager, mlflow_run_id, completed_steps),
+    GenerationMetricsCallback(tokenizer, eval_dataset, generation_config, compute_metrics),
+    LogLevelCallback(),
+]
+trainer = SFTTrainer(..., callbacks=callbacks)
+```
+
+## Key Concepts
+
+### Chunk-Based Training
+- Each chunk is a separate training session with max_steps calculated for that chunk
+- Trainer created fresh for each chunk (avoids state leakage)
+- Checkpoint saved after chunk completion
+- Next chunk loads checkpoint and continues
+
+### Trainer State Restoration
+When resuming from checkpoint:
+1. Load model state dict
+2. Restore optimizer state dict
+3. Restore scheduler state dict
+4. Restore RNG states (CPU and CUDA)
+5. Set trainer.state.global_step to continue step numbering
+6. Metrics continue from previous chunk
+
+### PEFT (LoRA) Support
+- User specifies `peft_params` in config with LoRA config (r, alpha, dropout, target_modules)
+- Model wrapped with `get_peft_model(model, lora_config)`
+- Only adapter weights saved/loaded (base model stays frozen)
+- Reduces checkpoint size and training memory
+
+### DPO Reference Model
+- DPO requires reference model for KL divergence penalty
+- Reference model loaded from disk (never updated during training)
+- Moved to same device as main model
+- Shared across all chunks (not checkpointed)
+
+## Common Patterns
+
+### Adding New Trainer Type
+1. Import trainer class from TRL (e.g., `from trl import NewTrainer`)
+2. Add config class import (e.g., `from trl import NewConfig`)
+3. Add trainer type to `_create_trainer_config_object()`
+4. Add trainer type to `_create_trainer()` instantiation logic
+5. Handle any special args in `_prepare_trainer_kwargs()`
+6. Update AutoML base class `VALID_TRAINER_TYPES` in `automl/base.py`
+
+### Adding Custom Metrics
+User provides `compute_metrics` function in config:
+```python
+def compute_metrics(predictions, references):
+    # Custom metric computation
+    return {'custom_metric': score}
+
+config = {
+    'additional_kwargs': {
+        'compute_metrics': compute_metrics
+    }
+}
+```
+
+Integrated via `GenerationMetricsCallback`.
+
+### Debugging Training Issues
+- Check `trainer.state.log_history` for metrics
+- Inspect checkpoint files on disk (torch.load)
+- Add logging in `_restore_trainer_state()` to verify state restoration
+- Check MLflow UI for metric continuity across chunks
+- Verify `global_step` increments correctly across chunks
+
+### Memory Optimization
+- Use PEFT to reduce memory footprint
+- Enable gradient checkpointing: `training_args['gradient_checkpointing'] = True`
+- Reduce batch size or increase gradient accumulation
+- Use bfloat16 or float16: `training_args['bf16'] = True`
+- Disable shared memory if checkpoints too large: `USE_SHARED_MEMORY = False`
+
+## Integration with Backend
+
+1. **Worker calls `create_trainer_instance()`**:
+   - Passes `TrainerConfig` with run details
+   - Gets back configured trainer
+
+2. **Worker calls `trainer.train()`**:
+   - Trains for `max_steps` (one chunk worth)
+   - Callbacks log to MLflow
+
+3. **Worker saves checkpoint**:
+   - Calls `save_checkpoint_to_shared_memory()` or `save_checkpoint_to_disk()`
+   - Stores optimizer/scheduler state for next chunk
+
+4. **Next chunk loads checkpoint**:
+   - Worker calls `create_trainer_instance()` with chunk_id > 0
+   - `trainer.py` detects resumed run and calls restoration functions
+   - Training continues from exact state
+
+## Testing
+
+Manual testing:
+```python
+# Test checkpoint save/load
+from rapidfireai.ml.checkpoint_utils import save_checkpoint_to_disk, load_checkpoint_from_disk
+
+save_checkpoint_to_disk(trainer, run_id=1, chunk_id=0, epoch=0)
+model, tokenizer = load_checkpoint_from_disk(trainer_config, is_peft=False)
+```
+
+Integration testing via tutorial notebooks.
diff --git a/rapidfireai/utils/CLAUDE.md b/rapidfireai/utils/CLAUDE.md
@@ -0,0 +1,437 @@
+# CLAUDE.md - Utils
+
+This file provides guidance for working with the utility modules in RapidFire AI.
+
+## Overview
+
+The utils module contains shared utilities used across RapidFire components, including logging, MLflow integration, shared memory management, serialization, exception handling, and constants.
+
+## Google Colab Support
+
+### Colab Helper (colab_helper.py)
+
+**Purpose**: Utilities for running RapidFire in Google Colab and restricted notebook environments
+
+**Key Functions**:
+- `is_colab()`: Detect if running in Google Colab
+- `get_notebook_environment()`: Returns 'colab', 'kaggle', 'jupyter', or 'unknown'
+- `setup_cloudflare_tunnel(port, description)`: Create free Cloudflare tunnel for port forwarding
+- `setup_ngrok_tunnel(port, auth_token, description)`: Create ngrok tunnel (requires auth token)
+- `expose_rapidfire_services(method, ...)`: Expose all services using specified tunneling method
+
+**Tunneling Methods**:
+1. **'native'**: Colab's built-in port forwarding (only works when called from notebook cell)
+2. **'cloudflare'**: Free Cloudflare tunnels via cloudflared binary (no registration required)
+3. **'ngrok'**: ngrok tunnels (requires free account and auth token)
+
+**Important Architectural Note - Tunnel Routing Loop**:
+
+When using tunnels in Colab, **inter-service communication must use localhost**, not tunnel URLs. Tunnel URLs are only for external browser access.
+
+❌ **Wrong Architecture (creates routing loop)**:
+```
+Browser → Frontend Tunnel → Frontend:3000 → MLflow Tunnel → MLflow:5002
+                                                   ↑
+                                                   Fails with 502: Colab → Cloudflare → Colab loop
+```
+
+✅ **Correct Architecture**:
+```
+Browser → Frontend Tunnel → Frontend:3000 → localhost:5002 (direct)
+Browser → MLflow Tunnel → MLflow:5002 (direct access if needed)
+```
+
+**Why this matters**:
+- Cloudflare/ngrok tunnels expose local services to the internet
+- They route: External Request → Tunnel Provider → Local Machine
+- From within the same machine, tunnel URLs create a loop that fails
+- Always use `http://127.0.0.1:<port>` for services on the same host
+
+**Example in start_colab.py**:
+```python
+# Create tunnels for external access
+mlflow_url = setup_cloudflare_tunnel(RF_MLFLOW_PORT, "MLflow Tracking UI")
+
+# DON'T set RF_MLFLOW_URL env var - let frontend use localhost
+# os.environ['RF_MLFLOW_URL'] = mlflow_url  # ❌ Creates routing loop
+
+# Frontend subprocess will use default: http://127.0.0.1:5002/ ✅
+```
+
+**Colab Process Restrictions**:
+
+Google Colab restricts certain OS-level process operations:
+1. `os.setpgrp()` - Cannot create process groups (wrapped in try-except with fallback)
+2. `os.getpgid()` - Cannot query process group IDs (uses psutil fallback)
+3. `os.killpg()` - Only used when process_group_id exists (safe)
+
+See `worker_manager.py` for implementation of these workarounds.
+
+## Files
+
+### constants.py
+**Purpose**: Centralized definitions for enums, config values, and system constants
+
+**Key Constants**:
+- `MLFLOW_URL`: Default MLflow tracking server URL (http://localhost:5002)
+- `USE_SHARED_MEMORY`: Flag to enable shared memory for checkpoints (default: True)
+- `LOG_FILENAME`: Log file naming pattern
+- `DB_PATH`: SQLite database file path
+
+**Key Enums**:
+- `ExperimentStatus`: NEW, RUNNING, COMPLETED, FAILED
+- `RunStatus`: NEW, ONGOING, COMPLETED, FAILED, STOPPED, KILLED
+- `RunSource`: USER, CLONE_MODIFY
+- `RunEndedBy`: COMPLETED, FAILED, KILLED, STOPPED
+- `TaskStatus`: PENDING, SCHEDULED, IN_PROGRESS, COMPLETED, FAILED
+- `ExperimentTask`, `ControllerTask`, `WorkerTask`: Task type enums
+- `SHMObjectType`: MODEL, CHECKPOINT (for shared memory registry)
+
+**Config Classes**:
+- `DispatcherConfig`: Dispatcher server configuration
+
+**Usage**:
+```python
+from rapidfireai.utils.constants import RunStatus, MLFLOW_URL
+
+if run['status'] == RunStatus.ONGOING.value:
+    # ...
+```
+
+### logging.py
+**Purpose**: Structured logging setup using loguru
+
+**Key Classes**:
+- `RFLogger`: Main logger factory for RapidFire components
+- `TrainingLogger`: Specialized logger for training output
+
+**Key Features**:
+- Creates per-component loggers (experiment, controller, worker_N, dispatcher, etc.)
+- Logs to both console and file
+- Experiment-specific log directories
+- Color-coded log levels
+- Structured format with timestamps
+
+**Usage**:
+```python
+from rapidfireai.utils.logging import RFLogger
+
+logger = RFLogger().create_logger("controller")
+logger.info("Starting controller")
+logger.error("Failed to schedule", run_id=5)
+```
+
+**Log Locations**:
+- `{experiment_path}/logs/controller.log`
+- `{experiment_path}/logs/worker_0.log`
+- `{experiment_path}/logs/dispatcher.log`
+
+### mlflow_manager.py
+**Purpose**: Wrapper around MLflow tracking API
+
+**Key Responsibilities**:
+- Creates and retrieves MLflow experiments
+- Logs metrics, parameters, and artifacts
+- Creates MLflow runs
+- Handles MLflow server communication
+
+**Key Methods**:
+- `get_experiment(name)`: Get or create MLflow experiment
+- `create_run(experiment_id)`: Create MLflow run, return run_id
+- `log_metric(run_id, key, value, step)`: Log metric
+- `log_param(run_id, key, value)`: Log parameter
+- `log_artifact(run_id, artifact_path)`: Log artifact file
+- `end_run(run_id)`: Mark run as completed
+
+**Usage**:
+```python
+from rapidfireai.utils.mlflow_manager import MLflowManager
+
+mlflow = MLflowManager("http://localhost:5002")
+experiment = mlflow.get_experiment("my_experiment")
+run_id = mlflow.create_run(experiment.experiment_id)
+mlflow.log_metric(run_id, "loss", 0.5, step=100)
+```
+
+**Integration**:
+- Each RapidFire run maps to one MLflow run
+- Parameters logged at run creation
+- Metrics logged during training via callbacks
+- Checkpoints logged as artifacts
+
+### shm_manager.py
+**Purpose**: Shared memory management for model checkpoints
+
+**Key Responsibilities**:
+- Creates shared memory registry (dict proxy) accessible across processes
+- Stores model checkpoints in shared memory to avoid disk I/O
+- Provides lock for thread-safe access
+- Manages memory lifecycle (allocation, deallocation)
+
+**Key Classes**:
+- `SharedMemoryManager`: Main interface for shared memory operations
+
+**Key Methods**:
+- `get_shm_objects()`: Returns (registry, lock) tuple
+- `store(key, value)`: Store object in shared memory
+- `load(key)`: Load object from shared memory
+- `delete(key)`: Remove object from shared memory
+- `exists(key)`: Check if key exists
+
+**Usage**:
+```python
+from rapidfireai.utils.shm_manager import SharedMemoryManager
+
+shm = SharedMemoryManager(name="controller-shm")
+registry, lock = shm.get_shm_objects()
+
+# Store model
+with lock:
+    registry[f"{run_id}_model"] = model_state_dict
+
+# Load model
+with lock:
+    state_dict = registry.get(f"{run_id}_model")
+```
+
+**Key Concepts**:
+- Uses multiprocessing.Manager() for shared dict
+- Objects stored on CPU (tensors moved from GPU)
+- Lock prevents concurrent access issues
+- Fallback to disk if object too large or memory full
+
+### experiment_utils.py
+**Purpose**: Experiment lifecycle management utilities
+
+**Key Responsibilities**:
+- Creates experiment directories and metadata
+- Generates unique experiment names
+- Sets up signal handlers for graceful shutdown
+- Manages experiment cleanup
+
+**Key Methods**:
+- `create_experiment(given_name, experiments_path)`: Create experiment directory and DB entry
+- `setup_signal_handlers(worker_processes)`: Setup SIGINT/SIGTERM handlers
+- `cleanup_experiment()`: Kill workers, reset DB state
+
+**Usage**:
+```python
+from rapidfireai.utils.experiment_utils import ExperimentUtils
+
+utils = ExperimentUtils()
+exp_id, exp_name, logs = utils.create_experiment("my_exp", "./experiments")
+utils.setup_signal_handlers(worker_processes)
+```
+
+**Naming**:
+- If "my_exp" exists, creates "my_exp_1", "my_exp_2", etc.
+- Ensures unique experiment names across runs
+
+### worker_manager.py
+**Purpose**: Worker process lifecycle management
+
+**Key Responsibilities**:
+- Spawns Worker processes (one per GPU)
+- Manages process pool
+- Handles worker shutdown and cleanup
+- Provides shutdown signals to workers
+
+**Key Methods**:
+- `spawn_workers(experiment_id, experiment_name)`: Create worker processes
+- `shutdown_workers()`: Gracefully stop all workers
+- `terminate_workers()`: Force kill workers
+
+**Usage**:
+```python
+from rapidfireai.utils.worker_manager import WorkerManager
+
+manager = WorkerManager(num_workers=4, registry, lock)
+manager.spawn_workers(experiment_id, experiment_name)
+# ... training happens ...
+manager.shutdown_workers()
+```
+
+**Shutdown Flow**:
+1. Set shutdown_event flag
+2. Wait for workers to finish current tasks (grace period)
+3. Terminate if still running after timeout
+
+### serialize.py
+**Purpose**: Object serialization for database storage
+
+**Key Responsibilities**:
+- Serialize complex Python objects (models, datasets, configs) to bytes
+- Deserialize bytes back to Python objects
+- Handle torch tensors and other non-pickleable objects
+
+**Key Functions**:
+- `encode_payload(obj)`: Serialize object to bytes using dill
+- `decode_db_payload(data)`: Deserialize bytes to object
+
+**Usage**:
+```python
+from rapidfireai.utils.serialize import encode_payload, decode_db_payload
+
+config = {'learning_rate': 1e-5, 'batch_size': 8}
+blob = encode_payload(config)
+db.execute("INSERT INTO runs (config_leaf) VALUES (?)", (blob,))
+
+row = db.execute("SELECT config_leaf FROM runs WHERE run_id = 1")[0]
+config = decode_db_payload(row['config_leaf'])
+```
+
+**Notes**:
+- Uses dill (more powerful than pickle)
+- Handles torch.Tensors, datasets, lambdas, etc.
+- BLOB storage in SQLite
+
+### datapaths.py
+**Purpose**: Centralized path management for experiment artifacts
+
+**Key Responsibilities**:
+- Generates consistent paths for checkpoints, datasets, logs
+- Ensures directories exist
+- Handles path construction for different artifact types
+
+**Key Methods**:
+- `initialize(experiment_name, base_path)`: Set up paths for experiment
+- `checkpoint_path(run_id, chunk_id)`: Get checkpoint file path
+- `dataset_path()`: Get dataset file path
+- `log_path(logger_name)`: Get log file path
+
+**Usage**:
+```python
+from rapidfireai.utils.datapaths import DataPath
+
+DataPath.initialize("my_experiment", "/path/to/experiments")
+checkpoint_file = DataPath.checkpoint_path(run_id=5, chunk_id=2)
+# Returns: /path/to/experiments/my_experiment/runs/run_5/checkpoints/checkpoint_chunk_2.pt
+```
+
+### exceptions.py
+**Purpose**: Custom exception classes for RapidFire
+
+**Exception Classes**:
+- `ExperimentException`: Experiment-level errors
+- `ControllerException`: Controller errors
+- `WorkerException`: Worker errors
+- `DispatcherException`: Dispatcher errors
+- `DBException`: Database errors
+- `AutoMLException`: AutoML errors
+- `NoGPUsFoundException`: No GPUs available
+
+**Usage**:
+```python
+from rapidfireai.utils.exceptions import ControllerException
+
+if num_gpus == 0:
+    raise NoGPUsFoundException("No GPUs found while initializing controller.")
+```
+
+### automl_utils.py
+**Purpose**: Utilities for AutoML algorithms
+
+**Key Functions**:
+- `get_runs(param_config, seed)`: Extract runs from AutoML algorithm or plain dict
+- `get_flattened_config_leaf(config)`: Flatten RFModelConfig to dict
+
+**Usage**:
+```python
+from rapidfireai.utils.automl_utils import get_runs
+
+# Handles both AutoML instances and plain dicts
+if isinstance(param_config, AutoMLAlgorithm):
+    runs = get_runs(param_config, seed)
+else:
+    runs = [param_config]  # Single config
+```
+
+### trainer_config.py
+**Purpose**: Configuration container for trainer initialization
+
+**Key Class**:
+- `TrainerConfig`: Dataclass holding all info needed by `create_trainer_instance()`
+
+**Attributes**:
+- `run_id`: Run identifier
+- `worker_id`: GPU worker assignment
+- `config_leaf`: Run configuration dict
+- `experiment_name`: Experiment name
+- `chunk_id`: Current chunk being trained
+- `epoch`: Current epoch
+- `mlflow_run_id`: MLflow run ID
+
+**Usage**:
+```python
+from rapidfireai.utils.trainer_config import TrainerConfig
+
+config = TrainerConfig(
+    run_id=5,
+    worker_id=0,
+    config_leaf=config_dict,
+    experiment_name="my_exp",
+    chunk_id=2,
+    epoch=0,
+    mlflow_run_id="abc123"
+)
+
+trainer = create_trainer_instance(config, shm_manager)
+```
+
+### ping.py
+**Purpose**: Server health check utility
+
+**Usage**:
+```python
+python -m rapidfireai.utils.ping
+# Checks if dispatcher, mlflow, and frontend servers are running
+```
+
+## Common Patterns
+
+### Logging Setup
+```python
+from rapidfireai.utils.logging import RFLogger
+
+# In each component:
+logger = RFLogger().create_logger("component_name")
+logger.info("Message")
+```
+
+### Shared Memory Access
+```python
+from rapidfireai.utils.shm_manager import SharedMemoryManager
+
+shm = SharedMemoryManager(name="controller-shm")
+registry, lock = shm.get_shm_objects()
+
+with lock:
+    registry[key] = value  # Thread-safe
+```
+
+### Exception Handling
+```python
+from rapidfireai.utils.exceptions import ControllerException
+
+try:
+    # ... operation ...
+except Exception as e:
+    raise ControllerException(f"Error: {e}") from e
+```
+
+### Path Management
+```python
+from rapidfireai.utils.datapaths import DataPath
+
+DataPath.initialize(experiment_name, base_path)
+checkpoint = DataPath.checkpoint_path(run_id, chunk_id)
+```
+
+## Testing
+
+Unit tests for utils:
+```bash
+pytest tests/  # Currently minimal, could expand
+```
+
+Most utils tested indirectly through integration tests.
PATCH

echo "Gold patch applied."
