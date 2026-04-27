"""
Task: prime-rl-eval-failed-rollouts-metric
Repo: PrimeIntellect-ai/prime-rl @ 18594ab2f5c43bdf80424731e5e268d67311056e
PR:   2123

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import asyncio
import importlib
import os
import re
import subprocess
import sys
import types
from pathlib import Path
from textwrap import dedent
from unittest.mock import AsyncMock, MagicMock

REPO = "/workspace"
EVAL_UTILS_PATH = f"{REPO}/src/prime_rl/orchestrator/eval_utils.py"
VF_UTILS_PATH = f"{REPO}/src/prime_rl/orchestrator/vf_utils.py"


# ---------------------------------------------------------------------------
# Helpers — subprocess execution for behavioral tests
# ---------------------------------------------------------------------------

def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess in the repo directory."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
            env={**os.environ, "PYTHONPATH": f"{REPO}/src"},
        )
    finally:
        script.unlink(missing_ok=True)


# Mock preamble for subprocess scripts — stubs out GPU/verifiers dependencies
_MOCK_PREAMBLE = dedent('''\
import sys, types, asyncio, importlib
from unittest.mock import AsyncMock, MagicMock

vf_mock = types.ModuleType("verifiers")
vf_mock.Environment = type("Env", (), {})
vf_mock.ClientConfig = type("CC", (), {})
vf_mock.RolloutOutput = dict
vf_mock.RolloutInput = lambda **kw: kw
sys.modules["verifiers"] = vf_mock
for m in ["verifiers.serve", "verifiers.utils", "verifiers.utils.serve_utils"]:
    sys.modules[m] = types.ModuleType(m)
sys.modules["verifiers.serve"].EnvClient = MagicMock
sys.modules["verifiers.serve"].ZMQEnvClient = MagicMock
sys.modules["verifiers.serve"].ZMQEnvServer = MagicMock
sys.modules["verifiers.utils.serve_utils"].get_free_port = lambda: 12345

for mod_name in ["prime_rl", "prime_rl.configs", "prime_rl.utils", "prime_rl.orchestrator"]:
    mod = types.ModuleType(mod_name)
    mod.__path__ = [f"/workspace/src/{mod_name.replace('.', '/')}"]
    sys.modules[mod_name] = mod
sys.modules["prime_rl.configs.orchestrator"] = types.ModuleType("prime_rl.configs.orchestrator")
sys.modules["prime_rl.configs.orchestrator"].EvalSamplingConfig = MagicMock

mock_logger = MagicMock()
logger_mod = types.ModuleType("prime_rl.utils.logger")
logger_mod.get_logger = lambda: mock_logger
logger_mod.InterceptHandler = MagicMock
logger_mod.ProgressTracker = MagicMock(return_value=MagicMock())
sys.modules["prime_rl.utils.logger"] = logger_mod

mock_monitor = MagicMock()
monitor_mod = types.ModuleType("prime_rl.utils.monitor")
monitor_mod.get_monitor = lambda: mock_monitor
sys.modules["prime_rl.utils.monitor"] = monitor_mod

utils_mod = types.ModuleType("prime_rl.utils.utils")
utils_mod.capitalize = lambda s: s.capitalize()
sys.modules["prime_rl.utils.utils"] = utils_mod

mock_evaluate = AsyncMock()
vf_utils_mod = types.ModuleType("prime_rl.orchestrator.vf_utils")
vf_utils_mod.evaluate = mock_evaluate
vf_utils_mod.get_completion_len = lambda x: x.get("_clen", 50)
sys.modules["prime_rl.orchestrator.vf_utils"] = vf_utils_mod
''')


# ---------------------------------------------------------------------------
# Helpers — in-process mock setup (for tests needing direct mock references)
# ---------------------------------------------------------------------------

def _setup_mocks():
    """Set up minimal mocks for the prime_rl import chain.

    Returns (mock_logger, mock_monitor, mock_evaluate) for test assertions.
    """
    # Mock verifiers (GPU-dependent async orchestration framework)
    vf_mock = types.ModuleType("verifiers")
    vf_mock.Environment = type("Env", (), {})
    vf_mock.ClientConfig = type("CC", (), {})
    vf_mock.RolloutOutput = dict
    vf_mock.RolloutInput = lambda **kw: kw
    sys.modules["verifiers"] = vf_mock
    for m in ["verifiers.serve", "verifiers.utils", "verifiers.utils.serve_utils"]:
        sys.modules[m] = types.ModuleType(m)
    sys.modules["verifiers.serve"].EnvClient = MagicMock
    sys.modules["verifiers.serve"].ZMQEnvClient = MagicMock
    sys.modules["verifiers.serve"].ZMQEnvServer = MagicMock
    sys.modules["verifiers.utils.serve_utils"].get_free_port = lambda: 12345

    # Packages need __path__ so importlib can locate real .py files on disk
    for mod_name in [
        "prime_rl", "prime_rl.configs", "prime_rl.utils", "prime_rl.orchestrator",
    ]:
        mod = types.ModuleType(mod_name)
        mod.__path__ = [f"/workspace/src/{mod_name.replace('.', '/')}"]
        sys.modules[mod_name] = mod
    # Non-package module (no __path__)
    sys.modules["prime_rl.configs.orchestrator"] = types.ModuleType("prime_rl.configs.orchestrator")
    sys.modules["prime_rl.configs.orchestrator"].EvalSamplingConfig = MagicMock

    mock_logger = MagicMock()
    logger_mod = types.ModuleType("prime_rl.utils.logger")
    logger_mod.get_logger = lambda: mock_logger
    logger_mod.InterceptHandler = MagicMock
    logger_mod.ProgressTracker = MagicMock(return_value=MagicMock())
    sys.modules["prime_rl.utils.logger"] = logger_mod

    mock_monitor = MagicMock()
    monitor_mod = types.ModuleType("prime_rl.utils.monitor")
    monitor_mod.get_monitor = lambda: mock_monitor
    sys.modules["prime_rl.utils.monitor"] = monitor_mod

    utils_mod = types.ModuleType("prime_rl.utils.utils")
    utils_mod.capitalize = lambda s: s.capitalize()
    sys.modules["prime_rl.utils.utils"] = utils_mod

    mock_evaluate = AsyncMock()
    vf_utils_mod = types.ModuleType("prime_rl.orchestrator.vf_utils")
    vf_utils_mod.evaluate = mock_evaluate
    vf_utils_mod.get_completion_len = lambda x: x.get("_clen", 50)
    sys.modules["prime_rl.orchestrator.vf_utils"] = vf_utils_mod

    if "/workspace/src" not in sys.path:
        sys.path.insert(0, "/workspace/src")

    return mock_logger, mock_monitor, mock_evaluate


def _fresh_import(module_name):
    """Force-reimport a module to pick up fresh mocks."""
    if module_name in sys.modules:
        del sys.modules[module_name]
    return importlib.import_module(module_name)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [EVAL_UTILS_PATH, VF_UTILS_PATH]:
        source = Path(path).read_text()
        compile(source, path, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_failed_rollouts_normal_metrics():
    """evaluate_env tracks failed_rollouts in metrics when some rollouts fail.

    Scenario: 10 inputs requested, 7 outputs returned -> 3 failed.
    On base: metrics dict has no failure key -> FAIL.
    On fix: metrics dict includes failed_rollouts=3 -> PASS.
    """
    r = _run_py(_MOCK_PREAMBLE + dedent('''\

        eval_utils = importlib.import_module("prime_rl.orchestrator.eval_utils")

        mock_env = MagicMock()
        mock_env._get_eval_inputs.return_value = [{"id": i} for i in range(10)]

        outputs = [
            {
                "example_id": i % 5, "reward": 0.5, "completion": "x",
                "is_truncated": False, "error": None, "_clen": 50,
                "trajectory": [{"tokens": {"prompt_ids": list(range(10)),
                                           "completion_ids": list(range(50))},
                                "response": {}}],
            }
            for i in range(7)
        ]
        mock_evaluate.return_value = outputs
        mock_monitor.reset_mock()

        asyncio.run(eval_utils.evaluate_env(
            env=mock_env, env_name="test_env", model_name="m",
            sampling_args={}, num_examples=5, rollouts_per_example=2,
            max_retries=0, ckpt_step=100, step=50, get_client=AsyncMock(),
        ))

        assert mock_monitor.log.called, "monitor.log was not called"
        metrics = mock_monitor.log.call_args_list[0][0][0]
        fail_keys = {k: v for k, v in metrics.items() if "fail" in k.lower()}
        assert fail_keys, f"No failure metric found in logged metrics: {list(metrics.keys())}"
        assert any(v == 3 for v in fail_keys.values()), \\
            f"Expected failure count of 3, got: {fail_keys}"
        print("PASS")
    '''))
    assert r.returncode == 0, f"Subprocess failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_failed_rollouts_all_fail():
    """When all rollouts fail, failure count is still logged to monitor.

    Scenario: 8 inputs requested, 0 outputs returned -> 8 failed.
    On base: all-fail branch returns without calling monitor.log -> FAIL.
    On fix: monitor.log called with failure count=8 -> PASS.
    """
    r = _run_py(_MOCK_PREAMBLE + dedent('''\

        mock_evaluate.return_value = []

        eval_utils = importlib.import_module("prime_rl.orchestrator.eval_utils")

        mock_env = MagicMock()
        mock_env._get_eval_inputs.return_value = [{"id": i} for i in range(8)]
        mock_monitor.reset_mock()

        asyncio.run(eval_utils.evaluate_env(
            env=mock_env, env_name="math", model_name="m",
            sampling_args={}, num_examples=4, rollouts_per_example=2,
            max_retries=0, ckpt_step=200, step=100, get_client=AsyncMock(),
        ))

        assert mock_monitor.log.called, \\
            "monitor.log not called in all-fail case (buggy: returns without logging)"
        metrics = mock_monitor.log.call_args[0][0]
        fail_keys = {k: v for k, v in metrics.items() if "fail" in k.lower()}
        assert fail_keys, f"No failure metric in all-fail metrics: {list(metrics.keys())}"
        assert any(v == 8 for v in fail_keys.values()), \\
            f"Expected failure count of 8, got: {fail_keys}"
        print("PASS")
    '''))
    assert r.returncode == 0, f"Subprocess failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — additional behavioral tests via importlib
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_failed_groups_aggregate_warning():
    """generate() logs aggregate warning when some groups fail.

    Scenario: 5 groups, 2 raise exceptions -> summary warning with count.
    On base: no summary warning (only individual Group failed messages) -> FAIL.
    On fix: summary warning mentioning 2 failed groups -> PASS.
    """
    mock_logger, mock_monitor, mock_evaluate = _setup_mocks()

    # Need fresh vf_utils import (not the mock we put in sys.modules for eval_utils)
    # Remove the mock vf_utils so we can import the real one
    del sys.modules["prime_rl.orchestrator.vf_utils"]
    vf_utils = _fresh_import("prime_rl.orchestrator.vf_utils")

    mock_env = MagicMock()
    mock_env.run_group = AsyncMock(side_effect=[
        [{"reward": 0.5, "example_id": 0}],
        [{"reward": 0.5, "example_id": 1}],
        [{"reward": 0.5, "example_id": 2}],
        RuntimeError("simulated failure A"),
        RuntimeError("simulated failure B"),
    ])

    mock_logger.reset_mock()
    examples = [{"id": i} for i in range(5)]
    result = asyncio.run(vf_utils.generate(
        env=mock_env, model_name="test", examples=examples,
        rollouts_per_example=1, sampling_args={},
        get_client=AsyncMock(return_value=MagicMock()),
    ))

    assert len(result) == 3, f"Expected 3 outputs, got {len(result)}"

    # Look for a SUMMARY warning (not individual "Group failed:" messages)
    summary_warnings = []
    for w in mock_logger.warning.call_args_list:
        msg = str(w.args[0]) if w.args else ""
        if "Group failed:" not in msg:
            summary_warnings.append(msg)

    assert summary_warnings, \
        "No summary warning about failed groups (only individual failure messages). " + \
        f"All warnings: {[str(w) for w in mock_logger.warning.call_args_list]}"
    assert any("2" in w for w in summary_warnings), \
        f"Summary warning doesn't mention failure count (2). Summaries: {summary_warnings}"


# [pr_diff] fail_to_pass
def test_failed_rollouts_varied_counts():
    """evaluate_env correctly computes failure count across different input sizes.

    Scenario: 20 inputs requested, 15 returned -> 5 failed.
    Validates the fix generalizes beyond the specific counts in other tests.
    """
    mock_logger, mock_monitor, mock_evaluate = _setup_mocks()

    eval_utils = _fresh_import("prime_rl.orchestrator.eval_utils")

    mock_env = MagicMock()
    mock_env._get_eval_inputs.return_value = [{"id": i} for i in range(20)]

    outputs = [
        {
            "example_id": i % 10, "reward": 0.8, "completion": "y",
            "is_truncated": False, "error": None, "_clen": 40,
            "trajectory": [{"tokens": {"prompt_ids": list(range(10)),
                                       "completion_ids": list(range(40))},
                            "response": {}}],
        }
        for i in range(15)
    ]
    mock_evaluate.return_value = outputs
    mock_monitor.reset_mock()

    asyncio.run(eval_utils.evaluate_env(
        env=mock_env, env_name="code_env", model_name="m",
        sampling_args={}, num_examples=10, rollouts_per_example=2,
        max_retries=0, ckpt_step=300, step=150, get_client=AsyncMock(),
    ))

    assert mock_monitor.log.called
    metrics = mock_monitor.log.call_args_list[0][0][0]
    fail_keys = {k: v for k, v in metrics.items() if "fail" in k.lower()}
    assert fail_keys, f"No failure metric found: {list(metrics.keys())}"
    assert any(v == 5 for v in fail_keys.values()), \
        f"Expected failure count of 5, got: {fail_keys}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_compute_eval_ckpt_step_regression():
    """compute_eval_ckpt_step pure function regression — known I/O pairs."""
    mock_logger, mock_monitor, mock_evaluate = _setup_mocks()

    eu = _fresh_import("prime_rl.orchestrator.eval_utils")
    f = eu.compute_eval_ckpt_step

    # Standard interval-aligned triggers
    assert f(ckpt_step=25, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
    assert f(ckpt_step=26, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
    # Not yet at interval
    assert f(ckpt_step=23, prev_ckpt_step=22, last_eval_step=0, interval=25) is None
    # Base model eval
    assert f(ckpt_step=0, prev_ckpt_step=-1, last_eval_step=-1, interval=25, eval_base_model=True) == 0
    # No re-eval of same step
    assert f(ckpt_step=25, prev_ckpt_step=25, last_eval_step=0, interval=25) is None
    # Jump over multiple intervals
    assert f(ckpt_step=76, prev_ckpt_step=24, last_eval_step=0, interval=25) == 75


# [static] pass_to_pass
def test_evaluate_env_not_stub():
    """evaluate_env has real logic — monitoring and metrics, not just pass/return."""
    source = Path(EVAL_UTILS_PATH).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "evaluate_env":
            assert len(node.body) > 5, \
                f"evaluate_env has only {len(node.body)} statements — looks like a stub"
            func_src = "\n".join(source.split("\n")[node.lineno - 1:node.end_lineno]).lower()
            assert "monitor" in func_src or "log" in func_src, "No monitoring/logging logic"
            assert "reward" in func_src or "metric" in func_src, "No metrics logic"
            break
    else:
        raise AssertionError("evaluate_env function not found")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ 18594ab
def test_no_bare_except():
    """No bare except blocks — must specify exception type (AGENTS.md:5)."""
    for filepath in [EVAL_UTILS_PATH, VF_UTILS_PATH]:
        source = Path(filepath).read_text()
        tree = ast.parse(source)
        fname = Path(filepath).name

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    if handler.type is None:
                        raise AssertionError(
                            f"{fname}: bare except at line {node.lineno} — "
                            "must specify exception type (AGENTS.md:5)"
                        )


# [agent_config] pass_to_pass — AGENTS.md:7 @ 18594ab
def test_no_process_comments():
    """No process-explanatory comments referencing old code (AGENTS.md:7)."""
    bad_patterns = [
        r"(?i)#.*used to.*but now",
        r"(?i)#.*old code",
        r"(?i)#.*previously.*now",
        r"(?i)#.*changed from",
        r"(?i)#.*was originally",
        r"(?i)#.*refactored from",
    ]

    for filepath in [EVAL_UTILS_PATH, VF_UTILS_PATH]:
        source = Path(filepath).read_text()
        fname = Path(filepath).name
        for pattern in bad_patterns:
            matches = re.findall(pattern, source)
            if matches:
                raise AssertionError(
                    f"{fname}: process-explanatory comment: {matches[0]} (AGENTS.md:7)"
                )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — ensure repo's own checks pass
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_repo_ruff_check():
    """Ruff lint check passes on orchestrator module (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "src/prime_rl/orchestrator/", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_ruff_format():
    """Ruff format check passes on orchestrator module (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "src/prime_rl/orchestrator/", "--config=pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_py_syntax():
    """All Python files in orchestrator module have valid syntax (pass_to_pass)."""
    orchestrator_dir = Path(REPO) / "src" / "prime_rl" / "orchestrator"
    for py_file in orchestrator_dir.glob("*.py"):
        source = py_file.read_text()
        try:
            compile(source, str(py_file), "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {py_file.name}: {e}")
