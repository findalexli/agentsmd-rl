"""
Task: primerl-error-handling-trajectories
Repo: PrimeIntellect-ai/prime-rl @ e6277883011bed744a066cec86b86d5a82236ba3
PR:   1416

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This PR adds error handling to trajectory processing:
1. Both interleave_rollout and branch_rollout return None for empty trajectories
2. Both functions zero out completion_mask when state["error"] is set
3. Orchestrator now uses rollout["is_truncated"] from vf directly
4. New math_python config files are added
"""

import ast
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock

# Setup paths
REPO = "/workspace/prime-rl"
sys.path.insert(0, REPO + "/src")

# Initialize logger for tests
from prime_rl.utils.logger import setup_logger
setup_logger("WARNING")

def _check_source_parses(path: str) -> bool:
    """Check that a Python file parses without errors."""
    full_path = Path(REPO) / path
    if not full_path.exists():
        return False
    try:
        ast.parse(full_path.read_text())
        return True
    except SyntaxError:
        return False


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_repo_ruff_linting():
    """Repo's ruff linting passes on modified files (pass_to_pass)."""
    # Install ruff if not available
    subprocess.run(["pip", "install", "ruff", "-q"], capture_output=True, timeout=60)
    # Ruff check on modified orchestrator files with project config (F, I rules)
    modified_files = [
        "src/prime_rl/orchestrator/trajectories.py",
        "src/prime_rl/orchestrator/orchestrator.py",
        "tests/unit/orchestrator/test_trajectories.py",
    ]
    r = subprocess.run(
        ["ruff", "check"] + modified_files + ["--select", "F,I"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    files_to_check = [
        "src/prime_rl/orchestrator/trajectories.py",
        "src/prime_rl/orchestrator/orchestrator.py",
        "tests/unit/orchestrator/test_trajectories.py",
    ]
    for path in files_to_check:
        assert _check_source_parses(path), f"{path} has syntax errors"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interleave_rollout_returns_none_on_empty_trajectory():
    """interleave_rollout must return None when trajectory is empty."""
    from prime_rl.orchestrator.trajectories import interleave_rollout

    # Create a minimal mock state with empty trajectory
    mock_state = {
        "trajectory": [],
        "error": None,
        "example_id": "test_123",
    }

    result = interleave_rollout(mock_state)
    assert result is None, f"Expected None for empty trajectory, got {result}"


# [pr_diff] fail_to_pass
def test_branch_rollout_returns_none_on_empty_trajectory():
    """branch_rollout must return None when trajectory is empty."""
    from prime_rl.orchestrator.trajectories import branch_rollout

    # Create a minimal mock state with empty trajectory
    mock_state = {
        "trajectory": [],
        "error": None,
        "example_id": "test_456",
    }

    result = branch_rollout(mock_state)
    assert result is None, f"Expected None for empty trajectory, got {result}"


# [pr_diff] fail_to_pass
def test_interleave_rollout_zeros_mask_on_error():
    """interleave_rollout must zero out completion_mask when state has error."""
    from prime_rl.orchestrator.trajectories import interleave_rollout

    # Create a mock trajectory step with non-zero completion_mask
    mock_step = {
        "tokens": {
            "prompt_ids": [1, 2, 3],
            "prompt_mask": [True, True, True],
            "completion_ids": [4, 5, 6],
            "completion_mask": [1, 1, 1],  # Non-zero mask
            "completion_logprobs": [-0.1, -0.2, -0.3],
        }
    }

    # Create a state with an error
    class FakeError:
        pass

    mock_state = {
        "trajectory": [mock_step],
        "error": FakeError(),  # Error is set
        "example_id": "test_error",
    }

    result = interleave_rollout(mock_state)
    assert result is not None, "Expected non-None result for non-empty trajectory"
    assert len(result) == 1, "Expected single rollout"

    # The completion_mask should be all False due to error
    rollout = result[0]
    assert all(m is False for m in rollout.completion_mask), \
        f"completion_mask should be all False on error, got {rollout.completion_mask}"


# [pr_diff] fail_to_pass
def test_branch_rollout_zeros_mask_on_error():
    """branch_rollout must zero out completion_mask when state has error."""
    from prime_rl.orchestrator.trajectories import branch_rollout

    # Create a mock trajectory step with non-zero completion_mask
    mock_step = {
        "tokens": {
            "prompt_ids": [1, 2, 3],
            "prompt_mask": [True, True, True],
            "completion_ids": [4, 5, 6],
            "completion_mask": [1, 1, 1],  # Non-zero mask
            "completion_logprobs": [-0.1, -0.2, -0.3],
        }
    }

    # Create a state with an error
    class FakeError:
        pass

    mock_state = {
        "trajectory": [mock_step],
        "error": FakeError(),  # Error is set
        "example_id": "test_error_branch",
    }

    result = branch_rollout(mock_state)
    assert result is not None, "Expected non-None result for non-empty trajectory"
    assert len(result) == 1, "Expected single rollout"

    # The completion_mask should be all False due to error
    rollout = result[0]
    assert all(m is False for m in rollout.completion_mask), \
        f"completion_mask should be all False on error, got {rollout.completion_mask}"


# [pr_diff] fail_to_pass
def test_interleave_rollout_preserves_mask_without_error():
    """interleave_rollout preserves original completion_mask when no error."""
    from prime_rl.orchestrator.trajectories import interleave_rollout

    # Create a mock trajectory step with specific completion_mask
    original_mask = [True, False, True]
    mock_step = {
        "tokens": {
            "prompt_ids": [1, 2, 3],
            "prompt_mask": [True, True, True],
            "completion_ids": [4, 5, 6],
            "completion_mask": original_mask,
            "completion_logprobs": [-0.1, -0.2, -0.3],
        }
    }

    mock_state = {
        "trajectory": [mock_step],
        "error": None,  # No error
        "example_id": "test_no_error",
    }

    result = interleave_rollout(mock_state)
    assert result is not None
    rollout = result[0]
    assert rollout.completion_mask == list(original_mask), \
        f"completion_mask should be preserved without error, got {rollout.completion_mask}"


# [pr_diff] fail_to_pass
def test_branch_rollout_preserves_mask_without_error():
    """branch_rollout preserves original completion_mask when no error."""
    from prime_rl.orchestrator.trajectories import branch_rollout

    # Create a mock trajectory step with specific completion_mask
    original_mask = [True, False, True]
    mock_step = {
        "tokens": {
            "prompt_ids": [1, 2, 3],
            "prompt_mask": [True, True, True],
            "completion_ids": [4, 5, 6],
            "completion_mask": original_mask,
            "completion_logprobs": [-0.1, -0.2, -0.3],
        }
    }

    mock_state = {
        "trajectory": [mock_step],
        "error": None,  # No error
        "example_id": "test_no_error_branch",
    }

    result = branch_rollout(mock_state)
    assert result is not None
    rollout = result[0]
    assert rollout.completion_mask == list(original_mask), \
        f"completion_mask should be preserved without error, got {rollout.completion_mask}"


# ---------------------------------------------------------------------------
# Config-derived (pr_diff) - new config files
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_math_python_config_exists():
    """configs/math_python/math_python.toml must exist with correct structure."""
    config_path = Path(REPO) / "configs" / "math_python" / "math_python.toml"
    assert config_path.exists(), f"math_python.toml must exist at {config_path}"

    content = config_path.read_text()
    # Check for key configuration sections
    assert "[orchestrator]" in content, "Config must have [orchestrator] section"
    assert "[inference]" in content, "Config must have [inference] section"
    assert "[[orchestrator.env]]" in content, "Config must have [[orchestrator.env]] section"
    assert 'id = "math-python"' in content, "Config must have id = 'math-python'"


# [pr_diff] fail_to_pass
def test_math_python_readme_exists():
    """configs/math_python/README.md must exist with setup and usage instructions."""
    readme_path = Path(REPO) / "configs" / "math_python" / "README.md"
    assert readme_path.exists(), f"README.md must exist at {readme_path}"

    content = readme_path.read_text()
    # Check for key documentation sections
    assert "math-python" in content.lower() or "math_python" in content, \
        "README must reference math-python"
    assert "setup" in content.lower() or "install" in content.lower(), \
        "README must have setup/install instructions"
    assert "eval" in content.lower() or "rl" in content.lower(), \
        "README must have eval or RL usage instructions"


# [pr_diff] fail_to_pass
def test_changelog_updated():
    """CHANGELOG.md must include the new auto-set api_server_count note."""
    changelog_path = Path(REPO) / "CHANGELOG.md"
    assert changelog_path.exists(), "CHANGELOG.md must exist"

    content = changelog_path.read_text()
    # Check for the specific change mentioned in the PR
    assert "api_server_count" in content or "Auto-set" in content, \
        "CHANGELOG.md must document the api_server_count auto-setting change"


# [pr_diff] pass_to_pass
def test_pyproject_verifiers_updated():
    """pyproject.toml must have updated verifiers revision."""
    pyproject_path = Path(REPO) / "pyproject.toml"
    content = pyproject_path.read_text()

    # The PR updated verifiers from 0dd0645 to ca75d04
    assert "ca75d04" in content, \
        "pyproject.toml must use verifiers rev ca75d04"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_return_type_annotation_updated():
    """Both functions must have updated return type annotations to include None."""
    src_path = Path(REPO) / "src" / "prime_rl" / "orchestrator" / "trajectories.py"
    src = src_path.read_text()

    # Check that return type annotations include None
    assert "list[TrainingSample] | None" in src, \
        "Both functions must have return type list[TrainingSample] | None"


# [pr_diff] pass_to_pass
def test_orchestrator_uses_rollout_is_truncated():
    """Orchestrator must use rollout['is_truncated'] directly instead of get_is_truncated."""
    src_path = Path(REPO) / "src" / "prime_rl" / "orchestrator" / "orchestrator.py"
    src = src_path.read_text()

    # Check that it now uses rollout["is_truncated"] directly
    assert 'rollout["is_truncated"]' in src, \
        "Orchestrator must use rollout['is_truncated'] directly"

    # Check that get_is_truncated import was removed
    assert "get_is_truncated" not in src, \
        "get_is_truncated should not be imported from utils.vf"


# [pr_diff] pass_to_pass
def test_trajectory_functions_not_stub():
    """Modified functions have meaningful error handling logic, not just stubs."""
    src_path = Path(REPO) / "src" / "prime_rl" / "orchestrator" / "trajectories.py"
    src = src_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name in ("interleave_rollout", "branch_rollout"):
                # Check for has_error check
                func_src = ast.unparse(node)
                assert "has_error" in func_src, \
                    f"{node.name} must check for has_error"
                assert "error" in func_src, \
                    f"{node.name} must reference state['error']"


# [pr_diff] pass_to_pass
def test_test_fixtures_include_error_field():
    """Test fixtures must include the error field in state definitions."""
    test_path = Path(REPO) / "tests" / "unit" / "orchestrator" / "test_trajectories.py"
    test_src = test_path.read_text()

    # Check that error=None is present in fixtures
    assert "error=None" in test_src or 'error=None' in test_src, \
        "Test fixtures must include error=None field"
