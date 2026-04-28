#!/usr/bin/env python3
"""Test suite for train sampler unification task.

Behavioral tests: import + call functions and run real pytest test files,
not grep source files.
"""

import sys
import subprocess
from pathlib import Path

REPO = Path("/workspace/transformers")
IMPORT_PREFIX = "import sys; sys.path.insert(0, 'src')"


def _run_py(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run Python code in the transformers repo context."""
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# fail_to_pass: tests that must FAIL at base commit, PASS at gold commit
# ---------------------------------------------------------------------------


def test_training_args_has_new_parameter():
    """TrainingArguments should have train_sampling_strategy field instead of group_by_length."""
    code = f"""
{IMPORT_PREFIX}
from transformers import TrainingArguments
from dataclasses import fields
field_names = {{f.name for f in fields(TrainingArguments)}}
assert "train_sampling_strategy" in field_names, "train_sampling_strategy field not found"
assert "group_by_length" not in field_names, "group_by_length field should be removed"
# Verify default value
args = TrainingArguments(output_dir="/tmp/test_default")
assert args.train_sampling_strategy == "random", f"Default should be 'random', got {{args.train_sampling_strategy!r}}"
print("OK")
"""
    result = _run_py(code)
    assert result.returncode == 0, f"Failed: {result.stderr}"
    assert "OK" in result.stdout


def test_training_args_choices_documented():
    """TrainingArguments should document and enforce the three valid choices."""
    code = f"""
{IMPORT_PREFIX}
from transformers import TrainingArguments
from dataclasses import fields
f = {{f.name: f for f in fields(TrainingArguments)}}["train_sampling_strategy"]
# Check metadata has choices constraint
choices = f.metadata.get("choices")
assert choices is not None, "metadata should contain 'choices'"
assert choices == ["random", "sequential", "group_by_length"], f"Wrong choices: {{choices}}"
print("OK")
"""
    result = _run_py(code)
    assert result.returncode == 0, f"Failed: {result.stderr}"
    assert "OK" in result.stdout


def test_trainer_uses_new_parameter():
    """Trainer._get_train_sampler should route on train_sampling_strategy."""
    code = f"""
{IMPORT_PREFIX}
from transformers.trainer import Trainer
import inspect
src = inspect.getsource(Trainer._get_train_sampler)
# Should reference the new parameter name (not the old bool)
assert "args.train_sampling_strategy" in src, "Trainer should use train_sampling_strategy"
assert "args.group_by_length" not in src, "Trainer should not reference old group_by_length"
# Should handle all three strategies
assert '"group_by_length"' in src, "Should handle group_by_length strategy"
assert '"sequential"' in src, "Should handle sequential strategy"
print("OK")
"""
    result = _run_py(code)
    assert result.returncode == 0, f"Failed: {result.stderr}"
    assert "OK" in result.stdout


def test_sequential_sampler_imported():
    """SequentialSampler should be available and returned for sequential strategy."""
    code = f"""
{IMPORT_PREFIX}
from transformers.trainer import Trainer
import inspect
src = inspect.getsource(Trainer._get_train_sampler)
assert "SequentialSampler" in src, "SequentialSampler should be referenced in _get_train_sampler"
# Check that SequentialSampler is actually importable from torch
from torch.utils.data import SequentialSampler
print("OK")
"""
    result = _run_py(code)
    assert result.returncode == 0, f"Failed: {result.stderr}"
    assert "OK" in result.stdout


def test_iterable_dataset_behavior():
    """IterableDataset should log info instead of raising ValueError."""
    code = f"""
{IMPORT_PREFIX}
from transformers.trainer import Trainer
import inspect
src = inspect.getsource(Trainer._validate_args)
# Should use logger.info, not raise ValueError
assert "logger.info(" in src, "Should use logger.info for IterableDataset"
assert "train_sampling_strategy" in src, "Log message should mention train_sampling_strategy"
assert 'raise ValueError("the `--group_by_length`' not in src, \\
    "Should not raise ValueError about group_by_length for IterableDataset"
assert "IterableDataset" in src, "Validation should reference IterableDataset"
print("OK")
"""
    result = _run_py(code)
    assert result.returncode == 0, f"Failed: {result.stderr}"
    assert "OK" in result.stdout


def test_readme_examples_updated():
    """README.md examples should use --train_sampling_strategy group_by_length."""
    content = (REPO / "examples/pytorch/speech-recognition/README.md").read_text()
    assert "--train_sampling_strategy group_by_length" in content, \
        "README should use new parameter format"
    # Count occurrences to verify all 6 were updated
    new_count = content.count("--train_sampling_strategy group_by_length")
    old_count = content.count("--group_by_length")
    assert new_count >= 6, f"Expected at least 6 updated examples, found {new_count}"
    assert old_count == 0, f"Found {old_count} old references that should be removed"


def test_readme_multiple_examples_updated():
    """All 6 --group_by_length occurrences in README should become --train_sampling_strategy."""
    content = (REPO / "examples/pytorch/speech-recognition/README.md").read_text()
    new_count = content.count("--train_sampling_strategy group_by_length")
    assert new_count == 6, f"Expected exactly 6 updated examples, found {new_count}"
    assert "--group_by_length" not in content, \
        "Old --group_by_length should not appear anywhere in README"


# ---------------------------------------------------------------------------
# pass_to_pass: tests that must PASS at both base and gold commit
# ---------------------------------------------------------------------------


def test_module_imports_correctly():
    """The transformers module should import without errors after the change."""
    result = _run_py(
        f"{IMPORT_PREFIX}; from transformers import TrainingArguments; print('OK')"
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "OK" in result.stdout


def test_train_sampling_strategy_values_work():
    """TrainingArguments should accept all valid train_sampling_strategy values."""
    code = f"""
{IMPORT_PREFIX}
from transformers import TrainingArguments
for strategy in ["random", "sequential", "group_by_length"]:
    args = TrainingArguments(output_dir="/tmp/test_strat", train_sampling_strategy=strategy)
    assert args.train_sampling_strategy == strategy, f"Failed for {{strategy}}"
    print(f"OK: {{strategy}}")
print("All strategies work!")
"""
    result = _run_py(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "All strategies work!" in result.stdout
    for s in ["random", "sequential", "group_by_length"]:
        assert f"OK: {s}" in result.stdout


# ---------------------------------------------------------------------------
# CI/CD runner test: runs a real pytest test file from the repo
# ---------------------------------------------------------------------------


def test_repo_training_args_tests_pass():
    """Real test runner: pytest tests/trainer/test_training_args.py should pass."""
    result = subprocess.run(
        ["bash", "-lc",
         "cd /workspace/transformers && python -m pytest tests/trainer/test_training_args.py -x --no-header -q 2>&1"],
        capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, \
        f"Repo TrainingArguments tests failed:\n{result.stdout}\n{result.stderr}"
