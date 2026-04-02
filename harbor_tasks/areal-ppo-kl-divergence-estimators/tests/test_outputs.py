"""
Task: areal-ppo-kl-divergence-estimators
Repo: inclusionAI/AReaL @ a0d122930f7de028404235688c7dba3f01854954
PR:   1054

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
from pathlib import Path

import torch

REPO = "/workspace/AReaL"
TARGET = f"{REPO}/areal/trainer/ppo/actor.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeScope:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


class _FakeStatsTracker:
    """Captures stat() calls for assertion."""

    def __init__(self):
        self.calls = []

    def scope(self, name):
        return _FakeScope()

    def denominator(self, **kw):
        pass

    def stat(self, **kw):
        self.calls.append(dict(kw))


def _extract_and_call(logprobs, old_logp):
    """Extract the function from source, call it, return (tracker, calls)."""
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


def _get_kl_tensors(tracker):
    """Extract the three KL tensors from captured stat calls."""
    all_kw = {}
    for c in tracker.calls:
        all_kw.update(c)
    direct = next((v for k, v in all_kw.items() if "direct" in k and isinstance(v, torch.Tensor)), None)
    taylor = next((v for k, v in all_kw.items() if "taylor" in k and isinstance(v, torch.Tensor)), None)
    dual = next((v for k, v in all_kw.items() if "dual" in k and isinstance(v, torch.Tensor)), None)
    return direct, taylor, dual


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """actor.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_kl_estimators_computed():
    """All three KL estimators (direct, taylor, dual) are computed and logged via stats_tracker."""
    logprobs = torch.tensor([-1.0, -2.0, -3.0])
    old_logp = torch.tensor([-1.5, -2.5, -3.5])
    tracker = _extract_and_call(logprobs, old_logp)
    direct, taylor, dual = _get_kl_tensors(tracker)

    assert direct is not None, "KL direct estimator not logged"
    assert taylor is not None, "KL taylor estimator not logged"
    assert dual is not None, "KL dual estimator not logged"

    # Verify math correctness
    log_ratio = (logprobs.float() - old_logp.float()).detach()
    assert torch.allclose(direct.float(), -log_ratio, atol=1e-5)
    assert torch.allclose(taylor.float(), log_ratio ** 2 / 2.0, atol=1e-5)
    assert torch.allclose(dual.float(), log_ratio.exp() - 1 - log_ratio, atol=1e-5)


# [pr_diff] fail_to_pass
def test_kl_estimators_diverse_inputs():
    """KL estimators are correct across diverse inputs including edge cases."""
    test_cases = [
        # identical policies → all estimators ≈ 0
        (torch.tensor([-1.0, -2.0, -3.0]), torch.tensor([-1.0, -2.0, -3.0])),
        # large positive log-ratio
        (torch.tensor([-0.1, -0.2]), torch.tensor([-5.0, -10.0])),
        # large negative log-ratio
        (torch.tensor([-5.0, -10.0]), torch.tensor([-0.1, -0.2])),
        # single token
        (torch.tensor([-0.5]), torch.tensor([-1.5])),
    ]

    for logprobs, old_logp in test_cases:
        tracker = _extract_and_call(logprobs, old_logp)
        direct, taylor, dual = _get_kl_tensors(tracker)

        assert direct is not None and taylor is not None and dual is not None

        log_ratio = (logprobs.float() - old_logp.float()).detach()
        assert torch.allclose(direct.float(), -log_ratio, atol=1e-5)
        assert torch.allclose(taylor.float(), log_ratio ** 2 / 2.0, atol=1e-5)
        assert torch.allclose(dual.float(), log_ratio.exp() - 1 - log_ratio, atol=1e-5)

        # Mathematical property: taylor and dual are always non-negative
        assert (taylor.float() >= -1e-6).all(), "Taylor estimator must be non-negative"
        assert (dual.float() >= -1e-6).all(), "Dual estimator must be non-negative"

        # Identical policies → all ≈ 0
        if torch.equal(logprobs, old_logp):
            assert (direct.float().abs() < 1e-5).all()
            assert (taylor.float().abs() < 1e-5).all()
            assert (dual.float().abs() < 1e-5).all()


# [pr_diff] fail_to_pass
def test_kl_estimators_detached():
    """KL estimator tensors must be detached (no gradient tracking)."""
    # Use requires_grad=True so that omitting .detach() would propagate grad tracking
    logprobs = torch.tensor([-1.0, -2.0], requires_grad=True)
    old_logp = torch.tensor([-1.5, -2.5])
    tracker = _extract_and_call(logprobs, old_logp)
    direct, taylor, dual = _get_kl_tensors(tracker)

    assert direct is not None and not direct.requires_grad, "direct must be detached"
    assert taylor is not None and not taylor.requires_grad, "taylor must be detached"
    assert dual is not None and not dual.requires_grad, "dual must be detached"


# [pr_diff] fail_to_pass
def test_kl_stats_use_denominator():
    """KL stats registered with denominator kwarg for proper per-token averaging."""
    logprobs = torch.tensor([-1.0, -2.0, -3.0])
    old_logp = torch.tensor([-1.5, -2.5, -3.5])
    tracker = _extract_and_call(logprobs, old_logp)

    # Find stat calls containing KL keys
    kl_calls = [
        c for c in tracker.calls
        if any(("direct" in k or "taylor" in k or "dual" in k) for k in c.keys())
    ]
    assert len(kl_calls) >= 1, "No stat calls with KL keys found"
    assert all("denominator" in c for c in kl_calls), "KL stat calls must include denominator"


# [pr_diff] pass_to_pass
def test_logprobs_none_no_kl():
    """When logprobs is None, no KL stats are logged and no crash occurs."""
    old_logp = torch.tensor([-1.5, -2.5, -3.5])
    tracker = _extract_and_call(None, old_logp)
    _, _, _ = _get_kl_tensors(tracker)

    all_kw = {}
    for c in tracker.calls:
        all_kw.update(c)
    has_kl = any(
        ("direct" in k or "taylor" in k or "dual" in k) and isinstance(v, torch.Tensor)
        for k, v in all_kw.items()
    )
    assert not has_kl, "KL stats should not be logged when logprobs is None"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_function_signature_preserved():
    """_log_proximal_approximation_stats and _log_version_staleness_stats must exist with expected args."""
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
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:25 @ a0d122930f7de028404235688c7dba3f01854954
def test_no_wildcard_imports():
    """No wildcard imports in actor.py (AGENTS.md rule)."""
    source = Path(TARGET).read_text()
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        assert not (stripped.startswith("from ") and "import *" in stripped), \
            f"Wildcard import found: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:90 @ a0d122930f7de028404235688c7dba3f01854954
def test_no_gpu_cpu_sync():
    """No .item()/.tolist()/.numpy() calls in _log_proximal_approximation_stats (AGENTS.md rule)."""
    # AST-only because: function depends on module-level stats_tracker and distributed imports
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_log_proximal_approximation_stats":
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    assert child.func.attr not in ("item", "tolist", "numpy"), \
                        f"GPU-CPU sync call .{child.func.attr}() found in hot path"
            break


# [agent_config] pass_to_pass — AGENTS.md:84 @ a0d122930f7de028404235688c7dba3f01854954
def test_no_print_in_function():
    """No print() calls in _log_proximal_approximation_stats (AGENTS.md: never print)."""
    # AST-only because: function depends on module-level stats_tracker and distributed imports
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_log_proximal_approximation_stats":
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    assert child.func.id != "print", \
                        "print() found in _log_proximal_approximation_stats — use stats_tracker instead"
            break
