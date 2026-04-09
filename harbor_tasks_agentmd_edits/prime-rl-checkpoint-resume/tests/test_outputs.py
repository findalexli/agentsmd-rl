"""Tests for checkpoint resume functionality.

Task: prime-rl-checkpoint-resume
Repo: PrimeIntellect-ai/prime-rl @ 5c5560039dad1359efc2dcd7e3a939bc3d95b6fe
PR:   536

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path("/workspace/prime-rl")


def _run_python(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Python script and return the result."""
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified Python files must parse without errors."""
    files = [
        "src/zeroband/training/ckpt.py",
        "src/zeroband/training/config.py",
        "src/zeroband/training/orchestrator/ckpt.py",
        "src/zeroband/training/orchestrator/config.py",
        "src/zeroband/training/orchestrator/orchestrator.py",
        "src/zeroband/training/orchestrator/client.py",
        "src/zeroband/training/orchestrator/utils.py",
        "src/zeroband/training/train.py",
        "src/zeroband/training/weights.py",
        "src/zeroband/utils/config.py",
        "src/zeroband/utils/monitor.py",
    ]
    for f in files:
        path = REPO / f
        if path.exists():
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(path)],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"Syntax error in {f}: {result.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_trainer_checkpoint_manager_exists():
    """Trainer CheckpointManager class must exist and be importable."""
    script = """
import sys
sys.path.insert(0, '/workspace/prime-rl/src')
from zeroband.training.ckpt import CheckpointManager, Progress
assert hasattr(CheckpointManager, 'save'), "CheckpointManager should have save method"
assert hasattr(CheckpointManager, 'load'), "CheckpointManager should have load method"
print("CheckpointManager and Progress imported successfully")
"""
    result = _run_python(script)
    assert result.returncode == 0, f"Failed to import CheckpointManager: {result.stderr}"


def test_orchestrator_checkpoint_manager_exists():
    """Orchestrator CheckpointManager class must exist and be importable."""
    script = """
import sys
sys.path.insert(0, '/workspace/prime-rl/src')
from zeroband.training.orchestrator.ckpt import CheckpointManager, Progress
assert hasattr(CheckpointManager, 'save'), "Orchestrator CheckpointManager should have save"
assert hasattr(CheckpointManager, 'load'), "Orchestrator CheckpointManager should have load"
print("Orchestrator CheckpointManager and Progress imported successfully")
"""
    result = _run_python(script)
    assert result.returncode == 0, f"Failed to import orchestrator CheckpointManager: {result.stderr}"


def test_checkpoint_config_has_resume_step():
    """Trainer CheckpointConfig must have resume_step and save_async fields."""
    script = """
import sys
sys.path.insert(0, '/workspace/prime-rl/src')
from zeroband.training.config import CheckpointConfig
assert 'resume_step' in CheckpointConfig.model_fields, "Missing resume_step field"
assert 'save_async' in CheckpointConfig.model_fields, "Missing save_async field"
print("CheckpointConfig has resume_step and save_async")
"""
    result = _run_python(script)
    assert result.returncode == 0, f"CheckpointConfig check failed: {result.stderr}"


def test_weights_module_exists():
    """weights.py module must exist with save_weight_checkpoint function."""
    weights_file = REPO / "src/zeroband/training/weights.py"
    assert weights_file.exists(), "weights.py should exist"
    content = weights_file.read_text()
    assert "def save_weight_checkpoint" in content, "weights.py should have save_weight_checkpoint"
    assert "pytorch_model.bin" in content, "weights.py should use pytorch_model.bin"


def test_weight_filename_updated():
    """Orchestrator utils.py should use pytorch_model.bin not model.pt."""
    utils_file = REPO / "src/zeroband/training/orchestrator/utils.py"
    content = utils_file.read_text()
    assert "pytorch_model.bin" in content, "utils.py should reference pytorch_model.bin"
    assert content.count("model.pt") == 0, "utils.py should not reference model.pt"


def test_client_uses_pytorch_model_bin():
    """Client.py should use pytorch_model.bin."""
    client_file = REPO / "src/zeroband/training/orchestrator/client.py"
    content = client_file.read_text()
    assert "pytorch_model.bin" in content, "client.py should reference pytorch_model.bin"


def test_orchestrator_config_path_changes():
    """OrchestratorConfig should use rollout_path/weights_path, not PathConfig."""
    script = """
import sys
sys.path.insert(0, '/workspace/prime-rl/src')
from zeroband.training.orchestrator.config import OrchestratorConfig
fields = OrchestratorConfig.model_fields
assert 'rollout_path' in fields, "Should have rollout_path"
assert 'weights_path' in fields, "Should have weights_path"
assert 'clean' in fields, "Should have clean flag"
print("OrchestratorConfig has correct path fields")
"""
    result = _run_python(script)
    assert result.returncode == 0, f"OrchestratorConfig check failed: {result.stderr}"


def test_checkpoint_save_load_cycle():
    """Orchestrator CheckpointManager can save and load progress correctly."""
    script = """
import sys
import tempfile
sys.path.insert(0, '/workspace/prime-rl/src')
from pathlib import Path
from zeroband.training.orchestrator.ckpt import CheckpointManager, Progress
from zeroband.training.orchestrator.config import CheckpointConfig

with tempfile.TemporaryDirectory() as tmpdir:
    config = CheckpointConfig(path=Path(tmpdir), interval=10)
    manager = CheckpointManager(config)

    progress = Progress(step=5, epoch=1, total_tokens=1000, total_samples=100, total_problems=50)
    manager.save(progress, step=5)

    loaded = Progress()
    manager.load(loaded, step=5)

    assert loaded.step == 6, f"Step should be 6 (incremented on save), got {loaded.step}"
    assert loaded.epoch == 1, f"Epoch should be 1, got {loaded.epoch}"
    assert loaded.total_tokens == 1000, f"Total tokens should be 1000, got {loaded.total_tokens}"
    print("Checkpoint save/load cycle works correctly")
"""
    result = _run_python(script, timeout=60)
    assert result.returncode == 0, f"Checkpoint cycle test failed: {result.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — README documentation checks
# ---------------------------------------------------------------------------


def test_readme_has_checkpointing_section():
    """README.md must document the checkpointing feature."""
    readme = REPO / "README.md"
    content = readme.read_text()
    assert "### Checkpointing" in content, "README should have Checkpointing section"
    assert "resume_step" in content, "README should document resume_step"
    assert "--ckpt.resume_step" in content, "README should show resume_step CLI flag"
    assert "step_" in content, "README should document step directory structure"


def test_readme_section_renamed():
    """README.md should have 'Developer' and 'Configs' sections."""
    readme = REPO / "README.md"
    content = readme.read_text()
    assert "## Developer" in content, "README should have Developer section"
    assert "### Configs" in content, "README should have Configs subsection"
