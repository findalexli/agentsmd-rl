"""Behavioral tests for the eval scheduling fix.

The function under test is `compute_eval_ckpt_step` in
`src/prime_rl/orchestrator/eval_utils.py`. We load the file directly with
heavy module-level imports stubbed, so we don't need torch/vllm/etc.
"""

import importlib.util
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

REPO = Path("/workspace/prime-rl")
EVAL_UTILS_PATH = REPO / "src" / "prime_rl" / "orchestrator" / "eval_utils.py"


def _load_eval_utils():
    """Load eval_utils.py with all heavy module-level imports stubbed.

    `verifiers`, `numpy`, and `pandas` are stubbed as MagicMock-backed
    pseudo-modules so attribute access (e.g. `vf.Environment` used as a type
    annotation) resolves to a MagicMock child. The `prime_rl.*` sibling
    modules are real ModuleType packages with the specific names that
    `eval_utils.py` does `from X import Y` on filled in.
    """
    # MagicMock-style stubs: attribute access auto-creates a child mock.
    for name in ["numpy", "pandas", "verifiers"]:
        if name not in sys.modules or not isinstance(sys.modules[name], MagicMock):
            sys.modules[name] = MagicMock()

    # Real package stubs for prime_rl namespace.
    pkg_names = [
        "prime_rl",
        "prime_rl.configs",
        "prime_rl.configs.orchestrator",
        "prime_rl.orchestrator",
        "prime_rl.orchestrator.vf_utils",
        "prime_rl.utils",
        "prime_rl.utils.logger",
        "prime_rl.utils.monitor",
        "prime_rl.utils.utils",
    ]
    for name in pkg_names:
        if name not in sys.modules or isinstance(sys.modules[name], MagicMock):
            mod = types.ModuleType(name)
            mod.__path__ = []
            sys.modules[name] = mod

    sys.modules["prime_rl.configs.orchestrator"].EvalSamplingConfig = MagicMock()
    sys.modules["prime_rl.orchestrator.vf_utils"].evaluate = MagicMock()
    sys.modules["prime_rl.orchestrator.vf_utils"].get_completion_len = MagicMock()
    sys.modules["prime_rl.utils.logger"].get_logger = MagicMock()
    sys.modules["prime_rl.utils.monitor"].get_monitor = MagicMock()
    sys.modules["prime_rl.utils.utils"].capitalize = MagicMock()

    # Force a fresh load each time so we observe edits to the file under test.
    sys.modules.pop("prime_rl_eval_utils_under_test", None)
    spec = importlib.util.spec_from_file_location(
        "prime_rl_eval_utils_under_test", str(EVAL_UTILS_PATH)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fn():
    mod = _load_eval_utils()
    assert hasattr(mod, "compute_eval_ckpt_step"), (
        "compute_eval_ckpt_step is not defined in src/prime_rl/orchestrator/eval_utils.py"
    )
    return mod.compute_eval_ckpt_step


# ---------------------------------------------------------------------------
# Fail-to-pass: behavioral tests for compute_eval_ckpt_step
# ---------------------------------------------------------------------------

def test_exact_hit_returns_interval_step():
    f = _fn()
    assert f(ckpt_step=25, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25


def test_jump_over_interval_returns_skipped_interval_step():
    """Production bug: ckpt_step jumps 24 -> 26, interval 25 must still fire."""
    f = _fn()
    assert f(ckpt_step=26, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25


def test_no_interval_crossed_returns_none():
    f = _fn()
    assert f(ckpt_step=23, prev_ckpt_step=22, last_eval_step=0, interval=25) is None


def test_base_model_eval_at_step_0_when_enabled():
    f = _fn()
    assert f(ckpt_step=0, prev_ckpt_step=-1, last_eval_step=-1, interval=25, eval_base_model=True) == 0


def test_base_model_eval_at_step_0_when_disabled():
    f = _fn()
    assert f(ckpt_step=0, prev_ckpt_step=-1, last_eval_step=-1, interval=25, eval_base_model=False) is None


def test_no_double_eval_at_same_interval():
    """Already evaluated at 25 -> must not re-trigger at 25."""
    f = _fn()
    assert f(ckpt_step=25, prev_ckpt_step=24, last_eval_step=25, interval=25) is None


def test_no_change_in_ckpt_step_returns_none():
    f = _fn()
    assert f(ckpt_step=25, prev_ckpt_step=25, last_eval_step=0, interval=25) is None


def test_multiple_intervals_crossed_returns_highest():
    """ckpt_step 24 -> 76 with interval 25: must fire eval at 75 (highest)."""
    f = _fn()
    assert f(ckpt_step=76, prev_ckpt_step=24, last_eval_step=0, interval=25) == 75


def test_second_interval_exact_hit():
    f = _fn()
    assert f(ckpt_step=50, prev_ckpt_step=49, last_eval_step=25, interval=25) == 50


def test_jump_across_second_interval():
    f = _fn()
    assert f(ckpt_step=51, prev_ckpt_step=48, last_eval_step=25, interval=25) == 50


def test_full_run_simulation_fires_at_every_interval():
    """End-to-end: simulate ckpt_step trajectory and verify all intervals fire exactly once."""
    f = _fn()
    ckpt_steps = [0, 0, 3, 5, 10, 15, 20, 24, 26, 30, 35, 40, 48, 51, 60, 70, 74, 76]
    interval = 25
    last_eval_step = -1
    prev_ckpt_step = -1
    fired_at = []
    for cs in ckpt_steps:
        r = f(cs, prev_ckpt_step, last_eval_step, interval)
        if r is not None:
            fired_at.append(r)
            last_eval_step = cs
        prev_ckpt_step = cs
    assert fired_at == [0, 25, 50, 75], f"got {fired_at}"


def test_interval_one_fires_every_step():
    """interval=1: every advance in ckpt_step should fire an eval at that step."""
    f = _fn()
    assert f(ckpt_step=1, prev_ckpt_step=0, last_eval_step=0, interval=1) == 1
    assert f(ckpt_step=2, prev_ckpt_step=1, last_eval_step=1, interval=1) == 2
    assert f(ckpt_step=7, prev_ckpt_step=6, last_eval_step=6, interval=1) == 7


def test_large_interval_no_fire_below_threshold():
    """With a large interval, no eval until ckpt_step crosses it."""
    f = _fn()
    for cs in range(1, 100):
        assert f(ckpt_step=cs, prev_ckpt_step=cs - 1, last_eval_step=-1, interval=100) is None
    assert f(ckpt_step=100, prev_ckpt_step=99, last_eval_step=-1, interval=100) == 100


def test_returns_int_or_none_only():
    """Type contract: return type is int | None, never a bool/float/str."""
    f = _fn()
    r1 = f(ckpt_step=25, prev_ckpt_step=24, last_eval_step=0, interval=25)
    r2 = f(ckpt_step=23, prev_ckpt_step=22, last_eval_step=0, interval=25)
    assert isinstance(r1, int) and not isinstance(r1, bool)
    assert r2 is None


# ---------------------------------------------------------------------------
# Pass-to-pass: repo-level sanity using stdlib only
# ---------------------------------------------------------------------------

def test_eval_utils_file_compiles_with_python():
    """Repo file is syntactically valid Python at every state of the task."""
    r = subprocess.run(
        [sys.executable, "-c", f"import ast; ast.parse(open('{EVAL_UTILS_PATH}').read())"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in eval_utils.py:\n{r.stderr}"


def test_orchestrator_file_compiles_with_python():
    """Sibling file the PR also touches must remain syntactically valid."""
    orch = REPO / "src" / "prime_rl" / "orchestrator" / "orchestrator.py"
    r = subprocess.run(
        [sys.executable, "-c", f"import ast; ast.parse(open('{orch}').read())"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in orchestrator.py:\n{r.stderr}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_tests_run_tests():
    """pass_to_pass | CI job 'Unit tests' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTEST_OUTPUT_DIR=/tmp/outputs uv run pytest tests/unit -m "not gpu"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")