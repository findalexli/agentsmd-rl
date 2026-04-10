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
# Gates (pass_to_pass, repo_tests) — run actual CI commands
# ---------------------------------------------------------------------------


def test_repo_unit_config():
    """Repo's unit tests for config modules pass (pass_to_pass)."""
    deps = "pytest beartype jaxtyping loguru datasets pydantic-settings typer pyyaml tomli"
    r = subprocess.run(
        f"pip install -q {deps} 2>&1 | tail -1 && "
        f"cd /workspace/prime-rl && "
        f"PYTHONPATH=/workspace/prime-rl/src python -m pytest "
        f"tests/unit/training/test_config.py tests/unit/training/orchestrator/test_config.py -v 2>&1",
        capture_output=True, text=True, shell=True, timeout=300,
    )
    assert r.returncode == 0, f"Config unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_import_training_modules():
    """Training and orchestrator modules can be imported (pass_to_pass)."""
    deps = "loguru datasets pydantic-settings typer pyyaml tomli"
    script = f"""
import sys
sys.path.insert(0, '/workspace/prime-rl/src')
import subprocess
subprocess.run(['pip', 'install', '-q', '{deps}'], capture_output=True)
from zeroband.training.config import TrainingConfig
from zeroband.training.orchestrator.config import OrchestratorConfig
print('TrainingConfig and OrchestratorConfig imported successfully')
"""
    r = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Import test failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified Python files must parse without errors (pass_to_pass)."""
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




def test_all_python_syntax():
    """All Python files in the repo must parse without errors (pass_to_pass)."""
    py_files = list(REPO.rglob("*.py"))
    failed = []
    for f in py_files:
        # Skip __pycache__ and hidden directories
        if "__pycache__" in str(f) or "/." in str(f):
            continue
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(f)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failed.append(f"{f}: {result.stderr}")
    assert not failed, f"Syntax errors found:\n" + "\n".join(failed[:10])


def test_pyproject_toml_valid():
    """pyproject.toml must be valid and parseable (pass_to_pass)."""
    import tomllib
    pyproject = REPO / "pyproject.toml"
    assert pyproject.exists(), "pyproject.toml must exist"
    content = pyproject.read_bytes()
    try:
        config = tomllib.loads(content.decode("utf-8"))
    except Exception as e:
        assert False, f"pyproject.toml is not valid TOML: {e}"
    # Check required sections exist
    assert "project" in config, "pyproject.toml must have [project] section"
    assert "dependencies" in config["project"], "pyproject.toml must have dependencies"


def test_config_files_valid():
    """All TOML config files must be valid (pass_to_pass)."""
    import tomllib
    config_dirs = [REPO / "configs"]
    failed = []
    for config_dir in config_dirs:
        if not config_dir.exists():
            continue
        for toml_file in config_dir.rglob("*.toml"):
            try:
                content = toml_file.read_bytes()
                tomllib.loads(content.decode("utf-8"))
            except Exception as e:
                failed.append(f"{toml_file}: {e}")
    assert not failed, f"Invalid TOML files:\n" + "\n".join(failed)


def test_repo_structure():
    """Repo must have expected directory structure (pass_to_pass)."""
    required_dirs = [
        "src/zeroband",
        "src/zeroband/training",
        "src/zeroband/training/orchestrator",
        "tests",
        "configs",
    ]
    for d in required_dirs:
        assert (REPO / d).is_dir(), f"Required directory {d} must exist"


def test_scripts_valid_syntax():
    """Shell scripts must have valid syntax (pass_to_pass)."""
    scripts = [REPO / "install.sh"]
    for script in scripts:
        if script.exists():
            result = subprocess.run(
                ["bash", "-n", str(script)],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"Invalid shell syntax in {script}: {result.stderr}"

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
