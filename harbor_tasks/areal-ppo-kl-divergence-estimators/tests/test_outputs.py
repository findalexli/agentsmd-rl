"""
Task: areal-ppo-kl-divergence-estimators
Repo: inclusionAI/AReaL @ a0d122930f7de028404235688c7dba3f01854954
PR:   1054

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

import torch

REPO = "/workspace/AReaL"
TARGET = f"{REPO}/areal/trainer/ppo/actor.py"

# ---------------------------------------------------------------------------
# Shared eval helpers — prepended to every subprocess test via _run_py()
# ---------------------------------------------------------------------------

_EVAL_HELPERS = """import ast, textwrap
from pathlib import Path
import torch

TARGET = "/workspace/AReaL/areal/trainer/ppo/actor.py"


class _FakeScope:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


class _FakeStatsTracker:
    def __init__(self):
        self.calls = []

    def scope(self, name):
        return _FakeScope()

    def denominator(self, **kw):
        pass

    def stat(self, **kw):
        self.calls.append(dict(kw))


def extract_and_call(logprobs, old_logp):
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_log_proximal_approximation_stats":
            func_node = node
            break
    assert func_node is not None, "_log_proximal_approximation_stats not found"

    lines = source.splitlines(keepends=True)
    func_src = textwrap.dedent("".join(lines[func_node.lineno - 1 : func_node.end_lineno]))

    tracker = _FakeStatsTracker()
    ns = {
        "torch": torch,
        "stats_tracker": tracker,
        "PROX_LOGP_METHOD_LOGLINEAR": "loglinear",
        "PROX_LOGP_METHOD_METRICS": "metrics",
        "PROX_LOGP_METHOD_RECOMPUTE": "recompute",
        "PROX_APPROX_METHOD_LOGLINEAR": "loglinear",
        "compute_prox_logp_approximations": lambda **kw: {},
        "_log_approximation_metrics_for_method": lambda **kw: None,
        "__builtins__": __builtins__,
    }
    exec(compile(func_src, "<test>", "exec"), ns)
    fn = ns["_log_proximal_approximation_stats"]

    mask = torch.ones(old_logp.shape[0], dtype=torch.bool)
    fn(
        prox_logp_method="none",
        prox_logp_gt=None,
        old_logp=old_logp,
        logprobs=logprobs,
        versions=None,
        current_version=None,
        compute_logp_mask=mask,
    )
    return tracker


def get_kl_tensors(tracker):
    all_kw = {}
    for c in tracker.calls:
        all_kw.update(c)
    direct = next((v for k, v in all_kw.items() if "direct" in k and isinstance(v, torch.Tensor)), None)
    taylor = next((v for k, v in all_kw.items() if "taylor" in k and isinstance(v, torch.Tensor)), None)
    dual = next((v for k, v in all_kw.items() if "dual" in k and isinstance(v, torch.Tensor)), None)
    return direct, taylor, dual
"""


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code with eval helpers as a subprocess in the repo dir."""
    return subprocess.run(
        ["python3", "-c", _EVAL_HELPERS + "\n" + code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


# ---------------------------------------------------------------------------
# pass_to_pass / static — syntax check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """actor.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_kl_estimators_computed():
    """All three KL estimators (direct, taylor, dual) computed correctly and logged."""
    r = _run_py("""
logprobs = torch.tensor([-1.0, -2.0, -3.0])
old_logp = torch.tensor([-1.5, -2.5, -3.5])
tracker = extract_and_call(logprobs, old_logp)
direct, taylor, dual = get_kl_tensors(tracker)

assert direct is not None, "KL direct estimator not logged"
assert taylor is not None, "KL taylor estimator not logged"
assert dual is not None, "KL dual estimator not logged"

log_ratio = (logprobs.float() - old_logp.float()).detach()
assert torch.allclose(direct.float(), -log_ratio, atol=1e-5), \
    f"direct mismatch: {direct} vs {-log_ratio}"
assert torch.allclose(taylor.float(), log_ratio**2 / 2.0, atol=1e-5), "taylor mismatch"
assert torch.allclose(dual.float(), log_ratio.exp() - 1 - log_ratio, atol=1e-5), "dual mismatch"
print("PASS")
""")
    assert r.returncode == 0, f"KL estimator test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_kl_estimators_diverse_inputs():
    """KL estimators correct across diverse inputs (identical, large ratios, single token)."""
    r = _run_py("""
test_cases = [
    ([-1.0, -2.0, -3.0], [-1.0, -2.0, -3.0]),  # identical policies
    ([-0.1, -0.2], [-5.0, -10.0]),               # large positive log-ratio
    ([-5.0, -10.0], [-0.1, -0.2]),               # large negative log-ratio
    ([-0.5], [-1.5]),                             # single token
]

for lp_vals, olp_vals in test_cases:
    logprobs = torch.tensor(lp_vals)
    old_logp = torch.tensor(olp_vals)
    tracker = extract_and_call(logprobs, old_logp)
    direct, taylor, dual = get_kl_tensors(tracker)

    assert direct is not None and taylor is not None and dual is not None

    log_ratio = (logprobs.float() - old_logp.float()).detach()
    assert torch.allclose(direct.float(), -log_ratio, atol=1e-5)
    assert torch.allclose(taylor.float(), log_ratio**2 / 2.0, atol=1e-5)
    assert torch.allclose(dual.float(), log_ratio.exp() - 1 - log_ratio, atol=1e-5)

    # taylor and dual must be non-negative
    assert (taylor.float() >= -1e-6).all(), "Taylor must be non-negative"
    assert (dual.float() >= -1e-6).all(), "Dual must be non-negative"

    # Identical policies -> all approximately 0
    if lp_vals == olp_vals:
        assert (direct.float().abs() < 1e-5).all()
        assert (taylor.float().abs() < 1e-5).all()
        assert (dual.float().abs() < 1e-5).all()
print("PASS")
""")
    assert r.returncode == 0, f"Diverse inputs test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_kl_estimators_detached():
    """KL estimator tensors are detached (no gradient tracking)."""
    r = _run_py("""
# requires_grad=True ensures missing .detach() would propagate gradient tracking
logprobs = torch.tensor([-1.0, -2.0], requires_grad=True)
old_logp = torch.tensor([-1.5, -2.5])
tracker = extract_and_call(logprobs, old_logp)
direct, taylor, dual = get_kl_tensors(tracker)

assert direct is not None and not direct.requires_grad, "direct must be detached"
assert taylor is not None and not taylor.requires_grad, "taylor must be detached"
assert dual is not None and not dual.requires_grad, "dual must be detached"
print("PASS")
""")
    assert r.returncode == 0, f"Detached test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_kl_stats_use_denominator():
    """KL stats registered with denominator kwarg for per-token averaging."""
    r = _run_py("""
logprobs = torch.tensor([-1.0, -2.0, -3.0])
old_logp = torch.tensor([-1.5, -2.5, -3.5])
tracker = extract_and_call(logprobs, old_logp)

kl_calls = [
    c for c in tracker.calls
    if any(("direct" in k or "taylor" in k or "dual" in k) for k in c.keys())
]
assert len(kl_calls) >= 1, "No stat calls with KL keys found"
assert all("denominator" in c for c in kl_calls), "KL stat calls must include denominator"
print("PASS")
""")
    assert r.returncode == 0, f"Denominator test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# pass_to_pass (pr_diff) — edge case
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_logprobs_none_no_kl():
    """No KL stats logged and no crash when logprobs is None."""
    r = _run_py("""
old_logp = torch.tensor([-1.5, -2.5, -3.5])
tracker = extract_and_call(None, old_logp)

all_kw = {}
for c in tracker.calls:
    all_kw.update(c)
has_kl = any(
    ("direct" in k or "taylor" in k or "dual" in k) and isinstance(v, torch.Tensor)
    for k, v in all_kw.items()
)
assert not has_kl, "KL stats should not be logged when logprobs is None"
print("PASS")
""")
    assert r.returncode == 0, f"logprobs=None test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# pass_to_pass (static) — regression
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_function_signature_preserved():
    """_log_proximal_approximation_stats and _log_version_staleness_stats preserved."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    found_log_prox = False
    found_log_version = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "_log_proximal_approximation_stats":
                found_log_prox = True
                args = [a.arg for a in node.args.args]
                assert "logprobs" in args, "logprobs arg missing"
                assert "old_logp" in args, "old_logp arg missing"
            if node.name == "_log_version_staleness_stats":
                found_log_version = True
    assert found_log_prox, "_log_proximal_approximation_stats not found"
    assert found_log_version, "_log_version_staleness_stats not found"


# ---------------------------------------------------------------------------
# agent_config (pass_to_pass) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass -- AGENTS.md:25 @ a0d122930f7de028404235688c7dba3f01854954
def test_no_wildcard_imports():
    """No wildcard imports in actor.py (AGENTS.md rule)."""
    source = Path(TARGET).read_text()
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        assert not (stripped.startswith("from ") and "import *" in stripped), \
            f"Wildcard import found: {stripped}"


# [agent_config] pass_to_pass -- AGENTS.md:90 @ a0d122930f7de028404235688c7dba3f01854954
def test_no_gpu_cpu_sync():
    """No .item()/.tolist()/.numpy() in _log_proximal_approximation_stats (AGENTS.md rule)."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_log_proximal_approximation_stats":
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    assert child.func.attr not in ("item", "tolist", "numpy"), \
                        f"GPU-CPU sync call .{child.func.attr}() found in hot path"
            break


# [agent_config] pass_to_pass -- AGENTS.md:84 @ a0d122930f7de028404235688c7dba3f01854954
def test_no_print_in_function():
    """No print() calls in _log_proximal_approximation_stats (AGENTS.md: never print)."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_log_proximal_approximation_stats":
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    assert child.func.id != "print", \
                        "print() found in _log_proximal_approximation_stats -- use stats_tracker instead"
            break


# ---------------------------------------------------------------------------
# pass_to_pass (repo_tests) — CI/CD checks from repo (run actual commands)
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass — ruff critical syntax errors on actor.py
def test_repo_ruff_syntax():
    """Repo's Python syntax and critical errors check passes (ruff --select=E9,F63,F7,F82)."""
    # First try to install ruff
    subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60
    )
    # Try via python module
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", "--select=E9,F63,F7,F82", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    if r.returncode == 0:
        return
    # Fallback: try ruff directly
    r = subprocess.run(
        ["ruff", "check", "--select=E9,F63,F7,F82", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Ruff syntax check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — ruff format check on actor.py
def test_repo_ruff_format():
    """actor.py passes ruff format check (pass_to_pass)."""
    # First try to install ruff
    subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True, text=True, timeout=60
    )
    # Try via python module
    r = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    if r.returncode == 0:
        return
    # Fallback: try ruff directly
    r = subprocess.run(
        ["ruff", "format", "--check", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — py_compile for actor.py
def test_repo_py_compile():
    """actor.py compiles without syntax errors via py_compile (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — ruff critical errors on full areal module
def test_repo_ruff_critical_areal():
    """Repo's areal module has no critical syntax errors (ruff E9,F63,F7,F82) (pass_to_pass)."""
    # First try to install ruff
    subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True, text=True, timeout=60
    )
    # Run ruff on full areal module for critical errors only
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", "--select=E9,F63,F7,F82", f"{REPO}/areal/"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if r.returncode == 0:
        return
    # Fallback: try ruff directly
    r = subprocess.run(
        ["ruff", "check", "--select=E9,F63,F7,F82", f"{REPO}/areal/"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Ruff critical check failed on areal/:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — py_compile for critical PPO files
def test_repo_all_py_syntax():
    """Critical PPO Python files compile without syntax errors (pass_to_pass)."""
    import py_compile
    import os
    # Test critical files related to the PR changes
    critical_files = [
        f"{REPO}/areal/trainer/ppo/actor.py",
        f"{REPO}/areal/trainer/ppo/stats.py",
    ]
    for path in critical_files:
        if os.path.exists(path):
            try:
                py_compile.compile(path, doraise=True)
            except Exception as e:
                raise AssertionError(f"Syntax error in {path}: {e}")
