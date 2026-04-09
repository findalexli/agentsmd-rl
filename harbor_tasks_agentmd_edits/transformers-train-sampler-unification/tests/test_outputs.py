"""
Task: transformers-train-sampler-unification
Repo: transformers @ 8efd81513f51cd343d086e0e8f69190caa49dbcf
PR:   huggingface/transformers#43138

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    for rel in [
        "src/transformers/training_args.py",
        "src/transformers/trainer.py",
    ]:
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(Path(REPO) / rel)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"{rel} has syntax errors: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_training_args_default_strategy():
    """TrainingArguments.train_sampling_strategy must default to 'random'."""
    r = subprocess.run(
        [
            "python3", "-c",
            "import json\n"
            "from transformers import TrainingArguments\n"
            "args = TrainingArguments(output_dir='/tmp/eval_test')\n"
            "print(json.dumps({'strategy': args.train_sampling_strategy}))\n",
        ],
        capture_output=True, text=True, cwd=REPO, timeout=60,
    )
    assert r.returncode == 0, f"Failed to create TrainingArguments: {r.stderr[:500]}"
    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert data["strategy"] == "random", f"Expected default 'random', got: {data['strategy']}"


# [pr_diff] fail_to_pass
def test_training_args_sequential_strategy():
    """TrainingArguments must accept train_sampling_strategy='sequential'."""
    r = subprocess.run(
        [
            "python3", "-c",
            "import json\n"
            "from transformers import TrainingArguments\n"
            "args = TrainingArguments(output_dir='/tmp/eval_test', train_sampling_strategy='sequential')\n"
            "print(json.dumps({'strategy': args.train_sampling_strategy}))\n",
        ],
        capture_output=True, text=True, cwd=REPO, timeout=60,
    )
    assert r.returncode == 0, f"Failed: {r.stderr[:500]}"
    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert data["strategy"] == "sequential", f"Expected 'sequential', got: {data['strategy']}"


# [pr_diff] fail_to_pass
def test_trainer_sequential_sampler():
    """Trainer._get_train_sampler returns SequentialSampler for strategy='sequential'."""
    r = subprocess.run(
        [
            "python3", "-c",
            "import json, torch\n"
            "from torch.utils.data import TensorDataset\n"
            "from transformers import Trainer, TrainingArguments\n"
            "ds = TensorDataset(torch.zeros(10, 5))\n"
            "args = TrainingArguments(output_dir='/tmp/eval_test', train_sampling_strategy='sequential')\n"
            "trainer = Trainer(model=torch.nn.Linear(5, 2), args=args, train_dataset=ds)\n"
            "sampler = trainer._get_train_sampler()\n"
            "print(json.dumps({'type': type(sampler).__name__}))\n",
        ],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    assert r.returncode == 0, f"Failed: {r.stderr[:500]}"
    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert data["type"] == "SequentialSampler", (
        f"Expected SequentialSampler, got: {data['type']}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_asr_docs_use_new_strategy():
    """English ASR docs must use train_sampling_strategy instead of group_by_length."""
    doc = Path(REPO) / "docs" / "source" / "en" / "tasks" / "asr.md"
    content = doc.read_text()
    assert "train_sampling_strategy" in content, (
        "asr.md should reference train_sampling_strategy"
    )
    assert "group_by_length=True" not in content, (
        "asr.md should not use deprecated group_by_length=True"
    )


# [pr_diff] fail_to_pass
def test_speech_readme_uses_new_strategy():
    """Speech recognition README must use --train_sampling_strategy flag."""
    readme = Path(REPO) / "examples" / "pytorch" / "speech-recognition" / "README.md"
    content = readme.read_text()
    assert "--train_sampling_strategy" in content, (
        "README.md should use --train_sampling_strategy flag"
    )
    assert "--group_by_length" not in content, (
        "README.md should not use deprecated --group_by_length flag"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:8 @ 8efd815
def test_ruff_style_check():
    """Modified Python files must pass ruff style checks (AGENTS.md: make style)."""
    import shutil

    import pytest

    if not shutil.which("ruff"):
        pytest.skip("ruff not installed")
    for rel in [
        "src/transformers/training_args.py",
        "src/transformers/trainer.py",
    ]:
        r = subprocess.run(
            ["ruff", "check", rel],
            capture_output=True, text=True, cwd=REPO, timeout=30,
        )
        assert r.returncode == 0, f"ruff check failed on {rel}:\n{r.stdout[:500]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's own CI/CD tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — training_args tests
def test_repo_training_args_tests():
    """Repo's TrainingArguments tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/trainer/test_training_args.py",
            "-v", "--tb=short"
        ],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    assert r.returncode == 0, f"Training args tests failed:\n{r.stdout[-800:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — trainer_utils tests (includes sampler tests)
def test_repo_trainer_utils_tests():
    """Repo's trainer utility tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/trainer/test_trainer_utils.py",
            "-v", "--tb=short"
        ],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    assert r.returncode == 0, f"Trainer utils tests failed:\n{r.stdout[-800:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — ruff format check on modified files
def test_repo_ruff_format_check():
    """Modified Python files pass ruff format check (pass_to_pass)."""
    import shutil

    import pytest

    if not shutil.which("ruff"):
        pytest.skip("ruff not installed")
    for rel in [
        "src/transformers/training_args.py",
        "src/transformers/trainer.py",
    ]:
        r = subprocess.run(
            ["ruff", "format", "--check", rel],
            capture_output=True, text=True, cwd=REPO, timeout=30,
        )
        assert r.returncode == 0, f"ruff format check failed on {rel}:\n{r.stderr[:500]}"
