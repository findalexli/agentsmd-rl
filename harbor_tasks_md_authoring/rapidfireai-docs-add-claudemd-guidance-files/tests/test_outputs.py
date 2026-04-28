"""Behavioral checks for rapidfireai-docs-add-claudemd-guidance-files (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rapidfireai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'RapidFire AI is an experiment execution framework for LLM fine-tuning and post-training that enables hyperparallelized training, dynamic real-time experiment control (IC Ops), and automatic multi-GPU ' in text, "expected to find: " + 'RapidFire AI is an experiment execution framework for LLM fine-tuning and post-training that enables hyperparallelized training, dynamic real-time experiment control (IC Ops), and automatic multi-GPU '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. **Scheduler** (`backend/scheduler.py`): Pure scheduling logic that assigns runs to available workers for specific chunks. Uses round-robin and fairness algorithms to ensure optimal GPU utilization.' in text, "expected to find: " + '3. **Scheduler** (`backend/scheduler.py`): Pure scheduling logic that assigns runs to available workers for specific chunks. Uses round-robin and fairness algorithms to ensure optimal GPU utilization.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Experiment** (`experiment.py`): Top-level API for users. Manages experiment lifecycle, creates database tables, sets up logging and signal handlers. Entry point for `run_fit()` and `get_results()' in text, "expected to find: " + '1. **Experiment** (`experiment.py`): Top-level API for users. Manages experiment lifecycle, creates database tables, sets up logging and signal handlers. Entry point for `run_fit()` and `get_results()'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/automl/CLAUDE.md')
    assert 'The automl module provides search algorithms for hyperparameter tuning and configuration exploration. Instead of manually creating runs one-by-one, users can specify search spaces and let RapidFire ge' in text, "expected to find: " + 'The automl module provides search algorithms for hyperparameter tuning and configuration exploration. Instead of manually creating runs one-by-one, users can specify search spaces and let RapidFire ge'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/automl/CLAUDE.md')
    assert 'This dict is stored in the database as `config_leaf` column and passed to `create_trainer_instance()`.' in text, "expected to find: " + 'This dict is stored in the database as `config_leaf` column and passed to `create_trainer_instance()`.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/automl/CLAUDE.md')
    assert '- `__init__(configs, trainer_type, num_runs)`: Takes list of `RFModelConfig` with parameter lists' in text, "expected to find: " + '- `__init__(configs, trainer_type, num_runs)`: Takes list of `RFModelConfig` with parameter lists'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/backend/CLAUDE.md')
    assert "The backend module contains the core orchestration logic for RapidFire's chunk-based concurrent training system. It coordinates between the user's process (Controller), scheduling logic (Scheduler), a" in text, "expected to find: " + "The backend module contains the core orchestration logic for RapidFire's chunk-based concurrent training system. It coordinates between the user's process (Controller), scheduling logic (Scheduler), a"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/backend/CLAUDE.md')
    assert '- `_handle_clone_modify()`, `_handle_stop()`, `_handle_resume()`, `_handle_delete()`: IC Ops handlers' in text, "expected to find: " + '- `_handle_clone_modify()`, `_handle_stop()`, `_handle_resume()`, `_handle_delete()`: IC Ops handlers'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/backend/CLAUDE.md')
    assert '- Creates runs from parameter configurations (single configs, AutoML algorithms, IC Ops clones)' in text, "expected to find: " + '- Creates runs from parameter configurations (single configs, AutoML algorithms, IC Ops clones)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/db/CLAUDE.md')
    assert 'The db module provides the persistence layer for RapidFire using SQLite. It stores experiment metadata, run configurations, task scheduling state, and checkpoint locations. The design emphasizes async' in text, "expected to find: " + 'The db module provides the persistence layer for RapidFire using SQLite. It stores experiment metadata, run configurations, task scheduling state, and checkpoint locations. The design emphasizes async'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/db/CLAUDE.md')
    assert '- Handles serialization/deserialization of complex objects (using `encode_payload`/`decode_db_payload`)' in text, "expected to find: " + '- Handles serialization/deserialization of complex objects (using `encode_payload`/`decode_db_payload`)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/db/CLAUDE.md')
    assert 'This file provides guidance for working with the database layer of RapidFire AI.' in text, "expected to find: " + 'This file provides guidance for working with the database layer of RapidFire AI.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/dispatcher/CLAUDE.md')
    assert 'The dispatcher is a Flask-based REST API that provides the communication layer between the web UI (frontend) and the RapidFire backend. It exposes endpoints for viewing experiment status, retrieving r' in text, "expected to find: " + 'The dispatcher is a Flask-based REST API that provides the communication layer between the web UI (frontend) and the RapidFire backend. It exposes endpoints for viewing experiment status, retrieving r'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/dispatcher/CLAUDE.md')
    assert 'sqlite3 rapidfire.db "SELECT * FROM interactive_control ORDER BY created_at DESC LIMIT 5;"' in text, "expected to find: " + 'sqlite3 rapidfire.db "SELECT * FROM interactive_control ORDER BY created_at DESC LIMIT 5;"'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/dispatcher/CLAUDE.md')
    assert 'gunicorn -c rapidfireai/dispatcher/gunicorn.conf.py rapidfireai.dispatcher.dispatcher:app' in text, "expected to find: " + 'gunicorn -c rapidfireai/dispatcher/gunicorn.conf.py rapidfireai.dispatcher.dispatcher:app'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/ml/CLAUDE.md')
    assert 'The ml module contains the training execution logic that wraps HuggingFace Transformers and TRL trainers. It handles trainer instantiation, checkpoint management, callbacks, and integration with Rapid' in text, "expected to find: " + 'The ml module contains the training execution logic that wraps HuggingFace Transformers and TRL trainers. It handles trainer instantiation, checkpoint management, callbacks, and integration with Rapid'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/ml/CLAUDE.md')
    assert '- Expects `TrainerConfig` object with all necessary info (run_id, worker_id, config_leaf, etc.)' in text, "expected to find: " + '- Expects `TrainerConfig` object with all necessary info (run_id, worker_id, config_leaf, etc.)'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/ml/CLAUDE.md')
    assert 'from rapidfireai.ml.checkpoint_utils import save_checkpoint_to_disk, load_checkpoint_from_disk' in text, "expected to find: " + 'from rapidfireai.ml.checkpoint_utils import save_checkpoint_to_disk, load_checkpoint_from_disk'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/utils/CLAUDE.md')
    assert 'The utils module contains shared utilities used across RapidFire components, including logging, MLflow integration, shared memory management, serialization, exception handling, and constants.' in text, "expected to find: " + 'The utils module contains shared utilities used across RapidFire components, including logging, MLflow integration, shared memory management, serialization, exception handling, and constants.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/utils/CLAUDE.md')
    assert 'When using tunnels in Colab, **inter-service communication must use localhost**, not tunnel URLs. Tunnel URLs are only for external browser access.' in text, "expected to find: " + 'When using tunnels in Colab, **inter-service communication must use localhost**, not tunnel URLs. Tunnel URLs are only for external browser access.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('rapidfireai/utils/CLAUDE.md')
    assert '**Purpose**: Utilities for running RapidFire in Google Colab and restricted notebook environments' in text, "expected to find: " + '**Purpose**: Utilities for running RapidFire in Google Colab and restricted notebook environments'[:80]

