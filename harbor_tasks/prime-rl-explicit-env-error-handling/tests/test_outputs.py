"""
Task: prime-rl-explicit-env-error-handling
Repo: prime-rl @ 05165f6c09009c1b2ed3e4c93997152f8cfb6e29
PR:   1448

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

REPO = "/workspace/prime-rl"

# Add repo to path for imports
sys.path.insert(0, REPO)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    modified_files = [
        "src/prime_rl/orchestrator/orchestrator.py",
        "src/prime_rl/orchestrator/trajectories.py",
        "tests/unit/orchestrator/test_trajectories.py",
    ]
    for file_path in modified_files:
        full_path = Path(REPO) / file_path
        src = full_path.read_text()
        try:
            ast.parse(src)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {file_path}: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interleave_rollout_returns_none_for_empty_trajectory():
    """interleave_rollout returns None when trajectory is empty."""
    code = """
import sys
sys.path.insert(0, '/workspace/prime-rl')

# Setup logger to avoid initialization issues
import prime_rl.utils.logger as logger_module
logger_module.setup_logger("DEBUG")

from prime_rl.orchestrator.trajectories import interleave_rollout

# Create a mock state with empty trajectory
mock_state = {
    "example_id": "test-123",
    "trajectory": [],
    "error": None,
    "reward": 0.0,
    "advantage": None,
    "stop_condition": None,
    "metrics": {},
}

result = interleave_rollout(mock_state)
if result is not None:
    print(f"FAIL: Expected None for empty trajectory, got {result}")
    sys.exit(1)
print("PASS: interleave_rollout returns None for empty trajectory")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_branch_rollout_returns_none_for_empty_trajectory():
    """branch_rollout returns None when trajectory is empty."""
    code = """
import sys
sys.path.insert(0, '/workspace/prime-rl')

# Setup logger to avoid initialization issues
import prime_rl.utils.logger as logger_module
logger_module.setup_logger("DEBUG")

from prime_rl.orchestrator.trajectories import branch_rollout

# Create a mock state with empty trajectory
mock_state = {
    "example_id": "test-456",
    "trajectory": [],
    "error": None,
    "reward": 0.0,
    "advantage": None,
    "stop_condition": None,
    "metrics": {},
}

result = branch_rollout(mock_state)
if result is not None:
    print(f"FAIL: Expected None for empty trajectory, got {result}")
    sys.exit(1)
print("PASS: branch_rollout returns None for empty trajectory")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_interleave_rollout_zeros_completion_mask_on_error():
    """interleave_rollout zeros completion_mask when state has error."""
    code = """
import sys
sys.path.insert(0, '/workspace/prime-rl')

# Setup logger to avoid initialization issues
import prime_rl.utils.logger as logger_module
logger_module.setup_logger("DEBUG")

from prime_rl.orchestrator.trajectories import interleave_rollout

# Create a mock state with error and non-empty trajectory
mock_state = {
    "example_id": "test-error",
    "trajectory": [
        {
            "tokens": {
                "prompt_ids": [1, 2, 3],
                "prompt_mask": [True, True, True],
                "completion_ids": [4, 5, 6],
                "completion_mask": [True, True, True],
                "completion_logprobs": [-0.1, -0.2, -0.3],
            },
            "messages": [],
            "extras": {},
        }
    ],
    "error": ValueError("Test error"),
    "reward": 0.0,
    "advantage": None,
    "stop_condition": None,
    "metrics": {},
}

result = interleave_rollout(mock_state)
if result is None:
    print("FAIL: Expected result for non-empty trajectory")
    sys.exit(1)

rollout = result[0]
# When error is set, completion_mask should be all False (zeroed out)
if not all(m is False for m in rollout.completion_mask):
    print(f"FAIL: Expected all False completion_mask on error, got {rollout.completion_mask}")
    sys.exit(1)

print("PASS: interleave_rollout zeros completion_mask on error")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_branch_rollout_zeros_completion_mask_on_error():
    """branch_rollout zeros completion_mask when state has error."""
    code = """
import sys
sys.path.insert(0, '/workspace/prime-rl')

# Setup logger to avoid initialization issues
import prime_rl.utils.logger as logger_module
logger_module.setup_logger("DEBUG")

from prime_rl.orchestrator.trajectories import branch_rollout

# Create a mock state with error and non-empty trajectory
mock_state = {
    "example_id": "test-branch-error",
    "trajectory": [
        {
            "tokens": {
                "prompt_ids": [1, 2, 3],
                "prompt_mask": [True, True, True],
                "completion_ids": [4, 5, 6],
                "completion_mask": [True, True, True],
                "completion_logprobs": [-0.1, -0.2, -0.3],
            },
            "messages": [],
            "extras": {},
        },
        {
            "tokens": {
                "prompt_ids": [1, 2, 3, 4, 5, 6],
                "prompt_mask": [True, True, True, False, False, False],
                "completion_ids": [7, 8],
                "completion_mask": [True, True],
                "completion_logprobs": [-0.4, -0.5],
            },
            "messages": [],
            "extras": {},
        },
    ],
    "error": RuntimeError("Infrastructure failure"),
    "reward": 0.0,
    "advantage": None,
    "stop_condition": None,
    "metrics": {},
}

result = branch_rollout(mock_state)
if result is None:
    print("FAIL: Expected result for non-empty trajectory")
    sys.exit(1)

# When error is set, all rollouts should have completion_mask all False
for i, rollout in enumerate(result):
    if not all(m is False for m in rollout.completion_mask):
        print(f"FAIL: Expected all False completion_mask for rollout {i}, got {rollout.completion_mask}")
        sys.exit(1)

print("PASS: branch_rollout zeros completion_mask on error")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_orchestrator_imports_no_get_is_truncated():
    """orchestrator.py no longer imports get_is_truncated from utils.vf."""
    orchestrator_path = Path(REPO) / "src/prime_rl/orchestrator/orchestrator.py"
    content = orchestrator_path.read_text()

    # The import line should NOT contain get_is_truncated
    import_section = content[content.find("from prime_rl.utils.vf"):content.find("\n\n", content.find("from prime_rl.utils.vf"))]
    assert "get_is_truncated" not in import_section, \
        "orchestrator.py should not import get_is_truncated"


# [pr_diff] fail_to_pass
def test_trajectories_return_type_annotation():
    """interleave_rollout and branch_rollout have correct return type annotations."""
    trajectories_path = Path(REPO) / "src/prime_rl/orchestrator/trajectories.py"
    content = trajectories_path.read_text()

    # Check that both functions have the Union/Optional return type with None
    assert "def interleave_rollout(state: vf.State) -> list[TrainingSample] | None:" in content, \
        "interleave_rollout should have return type list[TrainingSample] | None"
    assert "def branch_rollout(state: vf.State) -> list[TrainingSample] | None:" in content, \
        "branch_rollout should have return type list[TrainingSample] | None"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_upstream_trajectory_tests_pass():
    """Upstream trajectory unit tests still pass."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "tests/unit/orchestrator/test_trajectories.py", "-x", "-v"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, \
        f"Upstream trajectory tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [static] pass_to_pass
def test_interleave_rollout_normal_case_works():
    """interleave_rollout works normally when no error and non-empty trajectory."""
    code = """
import sys
sys.path.insert(0, '/workspace/prime-rl')

# Setup logger to avoid initialization issues
import prime_rl.utils.logger as logger_module
logger_module.setup_logger("DEBUG")

from prime_rl.orchestrator.trajectories import interleave_rollout

# Create a mock state with NO error and non-empty trajectory
mock_state = {
    "example_id": "test-normal",
    "trajectory": [
        {
            "tokens": {
                "prompt_ids": [1, 2, 3],
                "prompt_mask": [True, True, True],
                "completion_ids": [4, 5, 6],
                "completion_mask": [1, 1, 1],
                "completion_logprobs": [-0.1, -0.2, -0.3],
            },
            "messages": [],
            "extras": {},
        }
    ],
    "error": None,
    "reward": 1.0,
    "advantage": None,
    "stop_condition": None,
    "metrics": {},
}

result = interleave_rollout(mock_state)
if result is None:
    print("FAIL: Expected result for non-empty trajectory")
    sys.exit(1)

rollout = result[0]
# When no error, completion_mask should preserve original values (converted to bool)
if rollout.completion_mask != [True, True, True]:
    print(f"FAIL: Expected preserved completion_mask, got {rollout.completion_mask}")
    sys.exit(1)

print("PASS: interleave_rollout works normally for valid input")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [static] pass_to_pass
def test_branch_rollout_normal_case_works():
    """branch_rollout works normally when no error and non-empty trajectory."""
    code = """
import sys
sys.path.insert(0, '/workspace/prime-rl')

# Setup logger to avoid initialization issues
import prime_rl.utils.logger as logger_module
logger_module.setup_logger("DEBUG")

from prime_rl.orchestrator.trajectories import branch_rollout

# Create a mock state with NO error and non-empty trajectory (2 steps)
mock_state = {
    "example_id": "test-branch-normal",
    "trajectory": [
        {
            "tokens": {
                "prompt_ids": [1, 2, 3],
                "prompt_mask": [True, True, True],
                "completion_ids": [4, 5],
                "completion_mask": [1, 0],
                "completion_logprobs": [-0.1, -0.2],
            },
            "messages": [],
            "extras": {},
        },
        {
            "tokens": {
                "prompt_ids": [1, 2, 3, 4, 5],
                "prompt_mask": [True, True, True, False, False],
                "completion_ids": [6, 7],
                "completion_mask": [0, 1],
                "completion_logprobs": [-0.3, -0.4],
            },
            "messages": [],
            "extras": {},
        },
    ],
    "error": None,
    "reward": 1.0,
    "advantage": None,
    "stop_condition": None,
    "metrics": {},
}

result = branch_rollout(mock_state)
if result is None:
    print("FAIL: Expected result for non-empty trajectory")
    sys.exit(1)

if len(result) != 2:
    print(f"FAIL: Expected 2 rollouts, got {len(result)}")
    sys.exit(1)

# When no error, completion_mask should preserve original values
if result[0].completion_mask != [True, False]:
    print(f"FAIL: Expected preserved mask for step 0, got {result[0].completion_mask}")
    sys.exit(1)

if result[1].completion_mask != [False, True]:
    print(f"FAIL: Expected preserved mask for step 1, got {result[1].completion_mask}")
    sys.exit(1)

print("PASS: branch_rollout works normally for valid input")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [static] pass_to_pass
def test_orchestrator_has_error_handling():
    """orchestrator.py safely handles None return from make_train_example."""
    orchestrator_path = Path(REPO) / "src/prime_rl/orchestrator/orchestrator.py"
    content = orchestrator_path.read_text()

    # Check that there's a None check before iterating over train_example
    assert "if train_example is not None:" in content, \
        "orchestrator should check if train_example is not None before iterating"


# [static] pass_to_pass
def test_orchestrator_uses_rollout_is_truncated():
    """orchestrator.py uses rollout['is_truncated'] directly."""
    orchestrator_path = Path(REPO) / "src/prime_rl/orchestrator/orchestrator.py"
    content = orchestrator_path.read_text()

    # Check that the code uses rollout["is_truncated"] directly
    assert 'rollout["is_truncated"]' in content or "rollout['is_truncated']" in content, \
        "orchestrator should use rollout['is_truncated'] directly instead of get_is_truncated(rollout)"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "src/prime_rl/orchestrator/trajectories.py", "src/prime_rl/orchestrator/orchestrator.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "src/prime_rl/orchestrator/trajectories.py", "src/prime_rl/orchestrator/orchestrator.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint_all_src():
    """Repo's ruff linter passes on all src files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "src/prime_rl/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint on all src failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_import_syntax_check():
    """All Python files in modified modules have valid syntax (pass_to_pass)."""
    modified_files = [
        "src/prime_rl/orchestrator/trajectories.py",
        "src/prime_rl/orchestrator/orchestrator.py",
        "tests/unit/orchestrator/test_trajectories.py",
    ]
    for file_path in modified_files:
        r = subprocess.run(
            ["python", "-m", "py_compile", file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Syntax error in {file_path}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_orchestrator_unit_tests_pass():
    """All orchestrator unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3",
            "-m",
            "pytest",
            "tests/unit/orchestrator/",
            "--ignore=tests/unit/orchestrator/test_buffer.py",
            "--ignore=tests/unit/orchestrator/test_vf.py",
            "-v",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, \
        f"Orchestrator unit tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_train_runs_unit_tests_pass():
    """Train runs unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "tests/unit/train/test_runs.py", "-v"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, \
        f"Train runs tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_train_world_unit_tests_pass():
    """Train world unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "tests/unit/train/test_world.py", "-v"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, \
        f"Train world tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"



# [repo_tests] pass_to_pass - Additional CI checks from repo
def test_repo_batch_unit_tests_pass():
    """Batch preparation unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "tests/unit/orchestrator/test_batch.py", "-v"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, \
        f"Batch tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_all_orchestrator_tests_pass():
    """All working orchestrator unit tests pass - batch and trajectory (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3",
            "-m",
            "pytest",
            "tests/unit/orchestrator/test_batch.py",
            "tests/unit/orchestrator/test_trajectories.py",
            "-v",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, \
        f"Orchestrator tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_pytest_version():
    """Pytest is available and working (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "--version"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, \
        f"Pytest version check failed:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_imports_work():
    """Core orchestrator modules can be imported (pass_to_pass)."""
    code = """
import sys
sys.path.insert(0, '/workspace/prime-rl')

# Setup logger to avoid initialization issues
import prime_rl.utils.logger as logger_module
logger_module.setup_logger("DEBUG")

# Test imports
from prime_rl.orchestrator.trajectories import interleave_rollout, branch_rollout, TrainingSample
from prime_rl.trainer.batch import prepare_batch

print("PASS: All core imports work")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Import test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"
