"""
Task: prime-rl-eval-rollout-crash-resilience
Repo: PrimeIntellect-ai/prime-rl @ 60f01a04681df563044cf3cb7c64ec480b608451
PR:   2086

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import asyncio
import importlib
import re
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

REPO = "/workspace"


# ---------------------------------------------------------------------------
# Helpers — mock setup for verifiers ZMQ infrastructure (unavailable in test)
# ---------------------------------------------------------------------------

def _clean_modules():
    """Remove prime_rl and verifiers from sys.modules for fresh import."""
    for mod in list(sys.modules.keys()):
        if mod.startswith(("prime_rl", "verifiers")):
            del sys.modules[mod]


def _make_pkg(name, path=None):
    """Create a mock module that Python treats as a package (has __path__)."""
    mod = types.ModuleType(name)
    mod.__path__ = [path] if path else []
    return mod


def _setup_verifier_mocks():
    """Install minimal mocks for verifiers library."""
    _clean_modules()

    vf_mock = _make_pkg("verifiers")
    vf_mock.Environment = type("Env", (), {})
    vf_mock.ClientConfig = type("CC", (), {})
    vf_mock.RolloutOutput = dict
    sys.modules["verifiers"] = vf_mock

    workers_mock = types.ModuleType("verifiers.workers")
    workers_mock.ZMQEnvClient = MagicMock
    workers_mock.ZMQEnvServer = MagicMock
    sys.modules["verifiers.workers"] = workers_mock

    envs_mock = _make_pkg("verifiers.envs")
    sys.modules["verifiers.envs"] = envs_mock
    envs_env_mock = types.ModuleType("verifiers.envs.environment")
    envs_env_mock.EnvClient = MagicMock
    sys.modules["verifiers.envs.environment"] = envs_env_mock

    utils_mock = _make_pkg("verifiers.utils")
    sys.modules["verifiers.utils"] = utils_mock
    wu_mock = types.ModuleType("verifiers.utils.worker_utils")
    wu_mock.get_free_port_pair = lambda: 12345
    sys.modules["verifiers.utils.worker_utils"] = wu_mock


def _setup_prime_rl_mocks():
    """Install minimal mocks for prime_rl utility modules."""
    SRC = "/workspace/src"
    sys.modules["prime_rl"] = _make_pkg("prime_rl", f"{SRC}/prime_rl")
    sys.modules["prime_rl.utils"] = _make_pkg("prime_rl.utils", f"{SRC}/prime_rl/utils")

    mock_logger = MagicMock()
    logger_mod = types.ModuleType("prime_rl.utils.logger")
    logger_mod.get_logger = lambda: mock_logger
    logger_mod.InterceptHandler = MagicMock
    logger_mod.ProgressTracker = MagicMock
    sys.modules["prime_rl.utils.logger"] = logger_mod
    return mock_logger


def _import_vf_utils():
    """Fresh import of vf_utils with mocked dependencies."""
    _setup_verifier_mocks()
    mock_logger = _setup_prime_rl_mocks()
    if "/workspace/src" not in sys.path:
        sys.path.insert(0, "/workspace/src")
    return importlib.import_module("prime_rl.orchestrator.vf_utils"), mock_logger


def _import_eval_utils():
    """Fresh import of eval_utils with mocked dependencies."""
    _setup_verifier_mocks()
    mock_logger = _setup_prime_rl_mocks()

    SRC = "/workspace/src"
    sys.modules["prime_rl.configs"] = _make_pkg("prime_rl.configs", f"{SRC}/prime_rl/configs")
    sys.modules["prime_rl.configs.orchestrator"] = types.ModuleType("prime_rl.configs.orchestrator")
    sys.modules["prime_rl.orchestrator"] = _make_pkg("prime_rl.orchestrator", f"{SRC}/prime_rl/orchestrator")
    sys.modules["prime_rl.configs.orchestrator"].EvalSamplingConfig = MagicMock

    monitor_mod = types.ModuleType("prime_rl.utils.monitor")
    monitor_mod.get_monitor = lambda: MagicMock()
    sys.modules["prime_rl.utils.monitor"] = monitor_mod

    utils_mod = types.ModuleType("prime_rl.utils.utils")
    utils_mod.capitalize = lambda s: s.capitalize()
    sys.modules["prime_rl.utils.utils"] = utils_mod

    mock_evaluate = AsyncMock(return_value=[])
    vf_utils_mod = types.ModuleType("prime_rl.orchestrator.vf_utils")
    vf_utils_mod.evaluate = mock_evaluate
    vf_utils_mod.get_completion_len = lambda x: 0
    sys.modules["prime_rl.orchestrator.vf_utils"] = vf_utils_mod

    if "/workspace/src" not in sys.path:
        sys.path.insert(0, "/workspace/src")
    eval_utils = importlib.import_module("prime_rl.orchestrator.eval_utils")
    return eval_utils, mock_evaluate, mock_logger


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_ruff_lint_full():
    """Ruff lint check passes on full src directory (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )

    r = subprocess.run(
        ["ruff", "check", "--config=/workspace/pyproject.toml", "/workspace/src/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint check on full src failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_full():
    """Ruff format check passes on full src directory (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )

    r = subprocess.run(
        ["ruff", "format", "--check", "--config=/workspace/pyproject.toml", "/workspace/src/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check on full src failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_py_compile_modified():
    """Modified files compile without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "src/prime_rl/orchestrator/vf_utils.py", "src/prime_rl/orchestrator/eval_utils.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_py_compile_orchestrator_unit_tests():
    """Orchestrator unit test files compile without errors (pass_to_pass).

    Validates that all unit tests for the orchestrator module are valid Python,
    ensuring CI can run them. Covers: test_advantage.py, test_batch.py,
    test_buffer.py, test_scheduler.py, test_trajectories.py, test_filters.py.
    """
    test_files = [
        "tests/unit/orchestrator/test_advantage.py",
        "tests/unit/orchestrator/test_batch.py",
        "tests/unit/orchestrator/test_buffer.py",
        "tests/unit/orchestrator/test_scheduler.py",
        "tests/unit/orchestrator/test_trajectories.py",
        "tests/unit/orchestrator/test_filters.py",
    ]
    r = subprocess.run(
        ["python", "-m", "py_compile"] + test_files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile on orchestrator unit tests failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_no_ipython_debug():
    """No IPython debugger (IPython.embed) calls in modified files (pass_to_pass)."""
    for name in ["eval_utils.py", "vf_utils.py"]:
        path = Path(f"{REPO}/src/prime_rl/orchestrator/{name}")
        source = path.read_text()
        assert "IPython.embed" not in source, f"{name}: contains IPython.embed() call"
        assert "import IPython" not in source, f"{name}: imports IPython"


# [repo_tests] pass_to_pass
def test_repo_no_print_debug():
    """No print() debug statements in modified files (pass_to_pass)."""
    for name in ["eval_utils.py", "vf_utils.py"]:
        path = Path(f"{REPO}/src/prime_rl/orchestrator/{name}")
        source = path.read_text()
        # Allow print in specific contexts (e.g., already present)
        # Just check for obvious debug patterns like print("DEBUG or print("TODO
        assert 'print("debug"' not in source.lower(), f"{name}: contains debug print"
        assert "print('debug" not in source.lower(), f"{name}: contains debug print"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """eval_utils.py and vf_utils.py must parse without syntax errors."""
    for name in ["eval_utils.py", "vf_utils.py"]:
        path = Path(f"{REPO}/src/prime_rl/orchestrator/{name}")
        compile(path.read_text(), str(path), "exec")


# [static] pass_to_pass
def test_function_signature_generate():
    """generate() function signature is preserved (AST structural check)."""
    source = Path(f"{REPO}/src/prime_rl/orchestrator/vf_utils.py").read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "generate":
            # Check it has the expected parameters
            args = node.args
            arg_names = {a.arg for a in args.args + args.kwonlyargs}
            required = {"env", "model_name", "examples", "rollouts_per_example", "sampling_args"}
            assert required.issubset(arg_names), f"generate() missing required args: {required - arg_names}"
            return
    raise AssertionError("generate() function not found in vf_utils.py")


# [static] pass_to_pass
def test_function_signature_evaluate_env():
    """evaluate_env() function signature is preserved (AST structural check)."""
    source = Path(f"{REPO}/src/prime_rl/orchestrator/eval_utils.py").read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "evaluate_env":
            args = node.args
            arg_names = {a.arg for a in args.args + args.kwonlyargs}
            required = {"env", "env_name", "model_name", "sampling_args", "num_examples"}
            assert required.issubset(arg_names), f"evaluate_env() missing required args: {required - arg_names}"
            return
    raise AssertionError("evaluate_env() function not found in eval_utils.py")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_generate_catches_group_exceptions():
    """generate() catches per-group exceptions and returns successful results."""
    vf_utils, _ = _import_vf_utils()

    call_count = 0

    async def mock_run_group(
        env, client, model_name, example, rollouts_per_example,
        max_retries, state_columns, sampling_args,
    ):
        nonlocal call_count
        call_count += 1
        if example.get("fail"):
            raise RuntimeError("Simulated group failure")
        return [{"example_id": example["id"], "reward": 1.0}]

    vf_utils.run_group = mock_run_group

    examples = [{"id": 0}, {"id": 1}, {"id": 2}, {"fail": True, "id": 3}]

    async def get_client():
        return MagicMock()

    results = asyncio.run(vf_utils.generate(
        env=MagicMock(), model_name="m", examples=examples,
        rollouts_per_example=1, sampling_args={},
        get_client=get_client,
    ))

    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    result_ids = {r["example_id"] for r in results}
    assert result_ids == {0, 1, 2}, f"Expected {{0,1,2}}, got {result_ids}"
    assert call_count == 4, f"Expected 4 run_group calls, got {call_count}"


# [pr_diff] fail_to_pass
def test_generate_all_groups_fail():
    """generate() attempts all groups even when all fail, returns []."""
    vf_utils, _ = _import_vf_utils()

    call_count = 0

    async def mock_run_group(
        env, client, model_name, example, rollouts_per_example,
        max_retries, state_columns, sampling_args,
    ):
        nonlocal call_count
        call_count += 1
        raise RuntimeError("All fail")

    vf_utils.run_group = mock_run_group

    async def get_client():
        return MagicMock()

    num_examples = 5
    results = asyncio.run(vf_utils.generate(
        env=MagicMock(), model_name="m",
        examples=[{"id": i} for i in range(num_examples)],
        rollouts_per_example=1, sampling_args={},
        get_client=get_client,
    ))

    assert results == [], f"Expected empty list, got {results}"
    assert call_count == num_examples, \
        f"Expected {num_examples} run_group calls, got {call_count} (stub detected)"


# [pr_diff] fail_to_pass
def test_generate_logs_group_failures():
    """generate() logs a warning for each failed group (errors must not pass silently)."""
    vf_utils, mock_logger = _import_vf_utils()

    async def mock_run_group(
        env, client, model_name, example, rollouts_per_example,
        max_retries, state_columns, sampling_args,
    ):
        if example.get("fail"):
            raise ValueError(f"Failure for {example['id']}")
        return [{"example_id": example["id"]}]

    vf_utils.run_group = mock_run_group

    examples = [{"id": 0}, {"fail": True, "id": 1}, {"id": 2}, {"fail": True, "id": 3}]

    async def get_client():
        return MagicMock()

    asyncio.run(vf_utils.generate(
        env=MagicMock(), model_name="m", examples=examples,
        rollouts_per_example=1, sampling_args={},
        get_client=get_client,
    ))

    warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
    assert len(warning_calls) >= 2, \
        f"Expected at least 2 warning logs for 2 failures, got {len(warning_calls)}: {warning_calls}"


# [pr_diff] fail_to_pass
def test_evaluate_env_empty_outputs():
    """evaluate_env() returns early with warning when all rollouts fail."""
    eval_utils, mock_evaluate, mock_logger = _import_eval_utils()

    # evaluate_env must handle empty outputs gracefully (not crash)
    crashed = False
    crash_msg = ""
    try:
        asyncio.run(eval_utils.evaluate_env(
            env=MagicMock(), env_name="test_env", model_name="m",
            sampling_args={}, num_examples=5, rollouts_per_example=2,
            max_retries=0, ckpt_step=100, step=50, get_client=AsyncMock(),
        ))
    except Exception as exc:
        crashed = True
        crash_msg = str(exc)

    assert not crashed, \
        f"evaluate_env() crashed on empty outputs instead of returning early: {crash_msg}"

    # Anti-stub: verify evaluate() was actually called
    assert mock_evaluate.called, "evaluate() was never called — evaluate_env is a stub"

    # Verify a warning was logged about empty/failed rollouts
    warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
    has_warning = any(
        kw in w.lower()
        for w in warning_calls
        for kw in ("fail", "skip", "empty", "no ")
    )
    assert has_warning, f"No warning about failed/empty rollouts. Warnings: {warning_calls}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_compute_eval_ckpt_step():
    """compute_eval_ckpt_step pure function still works correctly."""
    _setup_verifier_mocks()
    _setup_prime_rl_mocks()

    SRC = "/workspace/src"
    sys.modules["prime_rl.configs"] = _make_pkg("prime_rl.configs", f"{SRC}/prime_rl/configs")
    sys.modules["prime_rl.configs.orchestrator"] = MagicMock()
    sys.modules["prime_rl.utils.monitor"] = MagicMock()
    sys.modules["prime_rl.utils.utils"] = MagicMock()
    sys.modules["prime_rl.orchestrator"] = _make_pkg("prime_rl.orchestrator", f"{SRC}/prime_rl/orchestrator")
    sys.modules["prime_rl.orchestrator.vf_utils"] = MagicMock()

    if "/workspace/src" not in sys.path:
        sys.path.insert(0, "/workspace/src")
    eu = importlib.import_module("prime_rl.orchestrator.eval_utils")

    f = eu.compute_eval_ckpt_step
    assert f(ckpt_step=25, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
    assert f(ckpt_step=26, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
    assert f(ckpt_step=23, prev_ckpt_step=22, last_eval_step=0, interval=25) is None
    assert f(ckpt_step=0, prev_ckpt_step=-1, last_eval_step=-1, interval=25, eval_base_model=True) == 0
    assert f(ckpt_step=25, prev_ckpt_step=25, last_eval_step=0, interval=25) is None
    assert f(ckpt_step=76, prev_ckpt_step=24, last_eval_step=0, interval=25) == 75


# [repo_tests] pass_to_pass
def test_repo_unit_test_eval_scheduling():
    """Unit tests for eval_scheduling from repo CI pass (pass_to_pass).

    This test runs the same assertions as tests/unit/orchestrator/test_eval_scheduling.py
    with mocked dependencies to avoid needing the full dependency stack (verifiers, etc.).
    """
    # Setup mocks like test_compute_eval_ckpt_step does
    _setup_verifier_mocks()
    _setup_prime_rl_mocks()

    SRC = "/workspace/src"
    sys.modules["prime_rl.configs"] = _make_pkg("prime_rl.configs", f"{SRC}/prime_rl/configs")
    sys.modules["prime_rl.configs.orchestrator"] = MagicMock()
    sys.modules["prime_rl.utils.monitor"] = MagicMock()
    sys.modules["prime_rl.utils.utils"] = MagicMock()
    sys.modules["prime_rl.orchestrator"] = _make_pkg("prime_rl.orchestrator", f"{SRC}/prime_rl/orchestrator")
    sys.modules["prime_rl.orchestrator.vf_utils"] = MagicMock()

    if "/workspace/src" not in sys.path:
        sys.path.insert(0, "/workspace/src")

    eu = importlib.import_module("prime_rl.orchestrator.eval_utils")
    f = eu.compute_eval_ckpt_step

    # Test cases from tests/unit/orchestrator/test_eval_scheduling.py
    # test_exact_hit
    assert f(ckpt_step=25, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
    # test_jump_over_interval
    assert f(ckpt_step=26, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
    # test_no_interval_crossed
    assert f(ckpt_step=23, prev_ckpt_step=22, last_eval_step=0, interval=25) is None
    # test_base_model_eval_at_step_0
    assert f(ckpt_step=0, prev_ckpt_step=-1, last_eval_step=-1, interval=25, eval_base_model=True) == 0
    # test_base_model_eval_disabled
    assert f(ckpt_step=0, prev_ckpt_step=-1, last_eval_step=-1, interval=25, eval_base_model=False) is None
    # test_no_double_eval
    assert f(ckpt_step=25, prev_ckpt_step=24, last_eval_step=25, interval=25) is None
    # test_no_change_in_ckpt_step
    assert f(ckpt_step=25, prev_ckpt_step=25, last_eval_step=0, interval=25) is None
    # test_multiple_intervals_crossed
    assert f(ckpt_step=76, prev_ckpt_step=24, last_eval_step=0, interval=25) == 75
    # test_second_interval
    assert f(ckpt_step=50, prev_ckpt_step=49, last_eval_step=25, interval=25) == 50
    # test_jump_across_second_interval
    assert f(ckpt_step=51, prev_ckpt_step=48, last_eval_step=25, interval=25) == 50
    # test_production_scenario_step25_skipped
    assert f(ckpt_step=26, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
    # test_production_scenario_step50_exact
    assert f(ckpt_step=50, prev_ckpt_step=49, last_eval_step=26, interval=25) == 50
    # test_simulate_full_run
    ckpt_steps = [0, 0, 3, 5, 10, 15, 20, 24, 26, 30, 35, 40, 48, 51, 60, 70, 74, 76]
    interval = 25
    last_eval_step = -1
    prev_ckpt_step = -1
    eval_triggered_at = []
    for ckpt_step in ckpt_steps:
        result = f(ckpt_step, prev_ckpt_step, last_eval_step, interval)
        if result is not None:
            eval_triggered_at.append(result)
            last_eval_step = ckpt_step
        prev_ckpt_step = ckpt_step
    assert eval_triggered_at == [0, 25, 50, 75]


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — structural regression
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_evaluate_calls_generate():
    """evaluate() still calls generate() (AST structural regression)."""
    source = Path(f"{REPO}/src/prime_rl/orchestrator/vf_utils.py").read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "evaluate":
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    func = child.func
                    if (isinstance(func, ast.Name) and func.id == "generate") or \
                       (isinstance(func, ast.Attribute) and func.attr == "generate"):
                        return  # PASS
            raise AssertionError("evaluate() doesn't call generate()")
    raise AssertionError("evaluate() function not found in vf_utils.py")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass — AGENTS.md:5 @ 60f01a04681df563044cf3cb7c64ec480b608451
def test_no_bare_except():
    """Exception handlers must use specific types, and fault tolerance must be implemented."""
    has_except_handler = False
    for name in ["eval_utils.py", "vf_utils.py"]:
        path = Path(f"{REPO}/src/prime_rl/orchestrator/{name}")
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    has_except_handler = True
                    assert handler.type is not None, \
                        f"{name}: bare except at line {node.lineno} — AGENTS.md:5"
    # Verify fault tolerance is implemented via exception handling
    assert has_except_handler, \
        "No except handlers found in modified files — fault tolerance not implemented"


# [agent_config] pass_to_pass — AGENTS.md:7 @ 60f01a04681df563044cf3cb7c64ec480b608451
def test_no_process_comments():
    """No process-explanatory comments referencing old code."""
    patterns = [
        r"(?i)#.*used to.*but now", r"(?i)#.*old code",
        r"(?i)#.*previously.*now", r"(?i)#.*changed from",
        r"(?i)#.*was originally", r"(?i)#.*refactored from",
    ]
    for name in ["eval_utils.py", "vf_utils.py"]:
        path = Path(f"{REPO}/src/prime_rl/orchestrator/{name}")
        source = path.read_text()
        for pattern in patterns:
            matches = re.findall(pattern, source)
            assert not matches, \
                f"{name}: process-explanatory comment: {matches[0]} — AGENTS.md:7"
