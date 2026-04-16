#!/usr/bin/env python3
"""Test suite for train sampler unification task.

Tests verify:
1. Code behavior: train_sampling_strategy parameter works correctly
2. Config updates: README.md examples updated to use new parameter
"""

import sys
import subprocess
from pathlib import Path

# Repository paths
REPO = Path("/workspace/transformers")
TRAINING_ARGS = REPO / "src/transformers/training_args.py"
TRAINER = REPO / "src/transformers/trainer.py"
README = REPO / "examples/pytorch/speech-recognition/README.md"


def test_training_args_has_new_parameter():
    """TrainingArguments should have train_sampling_strategy field instead of group_by_length."""
    content = TRAINING_ARGS.read_text()

    # Should have the new parameter
    assert "train_sampling_strategy: str = field(" in content, \
        "train_sampling_strategy field not found in TrainingArguments"
    assert 'default="random"' in content, \
        "train_sampling_strategy should default to 'random'"

    # Should NOT have the old parameter
    assert "group_by_length: bool" not in content, \
        "Old group_by_length field should be removed"


def test_training_args_choices_documented():
    """TrainingArguments should document the three valid choices for train_sampling_strategy."""
    content = TRAINING_ARGS.read_text()

    # Should document the valid choices
    assert '"random"' in content, "random option should be documented"
    assert '"sequential"' in content, "sequential option should be documented"
    assert '"group_by_length"' in content, "group_by_length option should be documented"


def test_trainer_uses_new_parameter():
    """Trainer should use train_sampling_strategy instead of group_by_length."""
    content = TRAINER.read_text()

    # Should use the new parameter name
    assert 'args.train_sampling_strategy == "group_by_length"' in content, \
        "Trainer should check train_sampling_strategy for group_by_length"
    assert 'args.train_sampling_strategy == "sequential"' in content, \
        "Trainer should check train_sampling_strategy for sequential"

    # Should NOT use the old parameter name
    assert "args.group_by_length" not in content, \
        "Trainer should not reference old group_by_length parameter"


def test_sequential_sampler_imported():
    """SequentialSampler should be available for the new sampling option."""
    content = TRAINER.read_text()

    # Check that SequentialSampler is returned in the new branch
    assert "return SequentialSampler(train_dataset)" in content, \
        "Trainer should return SequentialSampler for sequential strategy"


def test_iterable_dataset_behavior():
    """IterableDataset should log info message instead of raising ValueError."""
    content = TRAINER.read_text()

    # Should log info, not raise error
    assert "logger.info(" in content, "Should use logger.info for IterableDataset"
    assert "The `train_sampling_strategy=" in content, \
        "Should log message about sampling strategy being ignored"

    # Should NOT raise ValueError for IterableDataset
    assert 'raise ValueError("the `--group_by_length`' not in content, \
        "Should not raise ValueError for IterableDataset with group_by_length"


def test_readme_examples_updated():
    """README.md examples should use --train_sampling_strategy instead of --group_by_length."""
    content = README.read_text()

    # Should have the new parameter in examples
    assert "--train_sampling_strategy group_by_length" in content, \
        "README examples should use --train_sampling_strategy group_by_length"

    # Should NOT have the old parameter in examples
    assert "--group_by_length" not in content, \
        "README examples should not use --group_by_length"


def test_readme_multiple_examples_updated():
    """All 6 occurrences in README should be updated (all CTC and seq2seq examples)."""
    content = README.read_text()

    # Count occurrences
    new_count = content.count("--train_sampling_strategy group_by_length")
    old_count = content.count("--group_by_length")

    # All 6 examples should be updated
    assert new_count >= 6, f"Expected at least 6 updated examples, found {new_count}"
    assert old_count == 0, f"Found {old_count} old --group_by_length references that should be removed"


def test_module_imports_correctly():
    """The transformers module should import without errors after the change."""
    result = subprocess.run(
        [sys.executable, "-c", "from transformers import TrainingArguments; print('OK')"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "OK" in result.stdout, "Import should succeed"


def test_train_sampling_strategy_values_work():
    """TrainingArguments should accept all valid train_sampling_strategy values."""
    test_script = '''
import sys
sys.path.insert(0, "src")
from transformers import TrainingArguments

# Test each valid value
for strategy in ["random", "sequential", "group_by_length"]:
    args = TrainingArguments(
        output_dir="/tmp/test",
        train_sampling_strategy=strategy
    )
    assert args.train_sampling_strategy == strategy, f"Failed for {strategy}"
    print(f"OK: {strategy}")

print("All strategies work!")
'''
    result = subprocess.run(
        [sys.executable, "-c", test_script],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "All strategies work!" in result.stdout, "All strategies should be accepted"
