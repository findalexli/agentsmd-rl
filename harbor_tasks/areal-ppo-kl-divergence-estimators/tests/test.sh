#!/usr/bin/env bash
set +e

SCORE=0
BEHAV_PASS=0
REPO="/workspace/AReaL"
FILE="$REPO/areal/trainer/ppo/actor.py"

mkdir -p /logs/verifier

echo "=== AReaL PPO KL Divergence Estimators ==="
echo ""

# ---------- GATE: syntax check ----------
# [pr_diff] (gate): Python syntax must be valid
echo "--- GATE: Python syntax check ---"
if python3 -c "import py_compile; py_compile.compile('$FILE', doraise=True)" 2>&1; then
    echo "  PASS: syntax OK"
else
    echo "  FAIL: syntax error — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo ""

# ---------- BEHAVIORAL 1: Core KL estimator math (fail-to-pass) ----------

# [pr_diff] (0.35): KL estimators computed correctly when logprobs is not None
echo "--- BEHAVIORAL 1: KL estimator math + stats_tracker integration (0.35) ---"
BEHAV1=$(python3 << 'PYEOF'
import sys, torch, ast, textwrap

TARGET = "/workspace/AReaL/areal/trainer/ppo/actor.py"
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_log_proximal_approximation_stats":
        func_node = node
        break

if func_node is None:
    print("0.0")
    sys.exit(0)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1 : func_node.end_lineno]))

# Build minimal namespace with stat() that captures kwargs AND denominator
captured_stats = {}
captured_denominators = {}

class FakeScope:
    def __enter__(self): return self
    def __exit__(self, *a): pass

class FakeStatsTracker:
    def scope(self, name): return FakeScope()
    def denominator(self, **kw): pass
    def stat(self, **kw):
        # Capture both the tensor and the denominator kwarg
        for k, v in kw.items():
            if k != "denominator":
                captured_stats[k] = v
            if k == "denominator":
                captured_denominators[k] = v

tracker = FakeStatsTracker()

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

# Call with logprobs not None
logprobs = torch.tensor([-1.0, -2.0, -3.0])
old_logp = torch.tensor([-1.5, -2.5, -3.5])
mask = torch.tensor([True, True, True])

captured_stats.clear()
fn(
    prox_logp_method="none",
    prox_logp_gt=None,
    old_logp=old_logp,
    logprobs=logprobs,
    versions=None,
    current_version=None,
    compute_logp_mask=mask,
)

# Verify all three KL estimators were logged
has_direct = any("direct" in k and isinstance(v, torch.Tensor) for k, v in captured_stats.items())
has_taylor = any("taylor" in k and isinstance(v, torch.Tensor) for k, v in captured_stats.items())
has_dual = any("dual" in k and isinstance(v, torch.Tensor) for k, v in captured_stats.items())

if not (has_direct and has_taylor and has_dual):
    print("0.0")
    sys.exit(0)

# Find the tensors by their keys (flexible naming)
direct_t = next(v for k, v in captured_stats.items() if "direct" in k and isinstance(v, torch.Tensor))
taylor_t = next(v for k, v in captured_stats.items() if "taylor" in k and isinstance(v, torch.Tensor))
dual_t = next(v for k, v in captured_stats.items() if "dual" in k and isinstance(v, torch.Tensor))

# Verify math correctness against ground-truth KL estimator formulas
log_ratio = (logprobs.float() - old_logp.float()).detach()
expected_direct = -log_ratio
expected_taylor = log_ratio ** 2 / 2.0
expected_dual = log_ratio.exp() - 1 - log_ratio

ok = True
ok = ok and torch.allclose(direct_t.float(), expected_direct, atol=1e-5)
ok = ok and torch.allclose(taylor_t.float(), expected_taylor, atol=1e-5)
ok = ok and torch.allclose(dual_t.float(), expected_dual, atol=1e-5)

# Verify tensors are detached (not tracking gradients)
ok = ok and not direct_t.requires_grad
ok = ok and not taylor_t.requires_grad
ok = ok and not dual_t.requires_grad

print("1.0" if ok else "0.0")
PYEOF
)
echo "  Score: $BEHAV1"
if [ "$(echo "$BEHAV1" | tr -d '[:space:]')" = "1.0" ]; then BEHAV_PASS=1; fi
SCORE=$(python3 -c "print($SCORE + 0.35 * float('${BEHAV1:-0.0}'))")
echo ""

# ---------- BEHAVIORAL 2: Diverse inputs + mathematical properties ----------

# [pr_diff] (0.25): KL estimators correct with diverse inputs (edge cases)
echo "--- BEHAVIORAL 2: KL formulas with diverse inputs (0.25) ---"
BEHAV2=$(python3 << 'PYEOF'
import sys, torch, ast, textwrap

TARGET = "/workspace/AReaL/areal/trainer/ppo/actor.py"
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_log_proximal_approximation_stats":
        func_node = node
        break

if func_node is None:
    print("0.0")
    sys.exit(0)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1 : func_node.end_lineno]))

captured_stats = {}

class FakeScope:
    def __enter__(self): return self
    def __exit__(self, *a): pass

class FakeStatsTracker:
    def scope(self, name): return FakeScope()
    def denominator(self, **kw): pass
    def stat(self, **kw):
        captured_stats.update(kw)

tracker = FakeStatsTracker()

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

test_cases = [
    # identical policies → all estimators ~0
    (torch.tensor([-1.0, -2.0, -3.0]), torch.tensor([-1.0, -2.0, -3.0])),
    # large positive log-ratio
    (torch.tensor([-0.1, -0.2]), torch.tensor([-5.0, -10.0])),
    # large negative log-ratio
    (torch.tensor([-5.0, -10.0]), torch.tensor([-0.1, -0.2])),
    # single token
    (torch.tensor([-0.5]), torch.tensor([-1.5])),
    # many tokens
    (torch.randn(20), torch.randn(20)),
]

all_ok = True
for logprobs, old_logp in test_cases:
    mask = torch.ones(logprobs.shape[0], dtype=torch.bool)
    captured_stats.clear()
    fn(
        prox_logp_method="none",
        prox_logp_gt=None,
        old_logp=old_logp,
        logprobs=logprobs,
        versions=None,
        current_version=None,
        compute_logp_mask=mask,
    )

    direct_t = next((v for k, v in captured_stats.items() if "direct" in k and isinstance(v, torch.Tensor)), None)
    taylor_t = next((v for k, v in captured_stats.items() if "taylor" in k and isinstance(v, torch.Tensor)), None)
    dual_t = next((v for k, v in captured_stats.items() if "dual" in k and isinstance(v, torch.Tensor)), None)

    if direct_t is None or taylor_t is None or dual_t is None:
        all_ok = False
        break

    log_ratio = (logprobs.float() - old_logp.float()).detach()
    expected_direct = -log_ratio
    expected_taylor = log_ratio ** 2 / 2.0
    expected_dual = log_ratio.exp() - 1 - log_ratio

    all_ok = all_ok and torch.allclose(direct_t.float(), expected_direct, atol=1e-5)
    all_ok = all_ok and torch.allclose(taylor_t.float(), expected_taylor, atol=1e-5)
    all_ok = all_ok and torch.allclose(dual_t.float(), expected_dual, atol=1e-5)

    # Mathematical property: taylor and dual are always non-negative
    all_ok = all_ok and (taylor_t.float() >= -1e-6).all().item()
    all_ok = all_ok and (dual_t.float() >= -1e-6).all().item()

    # Identical policies → all ~0
    if torch.equal(logprobs, old_logp):
        all_ok = all_ok and (direct_t.float().abs() < 1e-5).all().item()
        all_ok = all_ok and (taylor_t.float().abs() < 1e-5).all().item()
        all_ok = all_ok and (dual_t.float().abs() < 1e-5).all().item()

print("1.0" if all_ok else "0.0")
PYEOF
)
echo "  Score: $BEHAV2"
if [ "$(echo "$BEHAV2" | tr -d '[:space:]')" = "1.0" ]; then BEHAV_PASS=1; fi
SCORE=$(python3 -c "print($SCORE + 0.25 * float('${BEHAV2:-0.0}'))")
echo ""

# ---------- BEHAVIORAL 3: logprobs=None guard ----------

# [pr_diff] (0.15): logprobs=None → no KL stats logged, no crash
echo "--- BEHAVIORAL 3: No KL stats when logprobs is None (0.15) ---"
BEHAV3=$(python3 << 'PYEOF'
import sys, torch, ast, textwrap

TARGET = "/workspace/AReaL/areal/trainer/ppo/actor.py"
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_log_proximal_approximation_stats":
        func_node = node
        break

if func_node is None:
    print("0.0")
    sys.exit(0)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1 : func_node.end_lineno]))

# We need to know if the function was MODIFIED to add KL stats at all.
# If the function body is identical to the base commit, it can't pass BEHAV1/2,
# so this test only awards points if BEHAV1 or BEHAV2 also passed (gated in shell).
captured_stats = {}

class FakeScope:
    def __enter__(self): return self
    def __exit__(self, *a): pass

class FakeStatsTracker:
    def scope(self, name): return FakeScope()
    def denominator(self, **kw): pass
    def stat(self, **kw):
        captured_stats.update(kw)

tracker = FakeStatsTracker()

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

# Call with logprobs=None — should not crash and should not log KL stats
old_logp = torch.tensor([-1.5, -2.5, -3.5])
mask = torch.tensor([True, True, True])

captured_stats.clear()
try:
    fn(
        prox_logp_method="none",
        prox_logp_gt=None,
        old_logp=old_logp,
        logprobs=None,
        versions=None,
        current_version=None,
        compute_logp_mask=mask,
    )
except Exception:
    print("0.0")
    sys.exit(0)

# No KL-related stats should have been logged
has_kl = any(
    ("direct" in k or "taylor" in k or "dual" in k) and isinstance(v, torch.Tensor)
    for k, v in captured_stats.items()
)
print("0.0" if has_kl else "1.0")
PYEOF
)
echo "  Score: $BEHAV3"
# Gate BEHAV3 behind at least one core behavioral test passing
# (prevents do-nothing agent from getting free points)
if [ "$BEHAV_PASS" -eq 1 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.15 * float('${BEHAV3:-0.0}'))")
else
    echo "  (gated: skipped — no core behavioral test passed)"
fi
echo ""

# ---------- BEHAVIORAL 4: denominator kwarg used correctly ----------

# [pr_diff] (0.10): KL stats registered with denominator for proper per-token averaging
echo "--- BEHAVIORAL 4: stats_tracker.stat() uses denominator (0.10) ---"
BEHAV4=$(python3 << 'PYEOF'
import sys, torch, ast, textwrap

TARGET = "/workspace/AReaL/areal/trainer/ppo/actor.py"
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_log_proximal_approximation_stats":
        func_node = node
        break

if func_node is None:
    print("0.0")
    sys.exit(0)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1 : func_node.end_lineno]))

# Track all stat() calls including denominator kwarg
stat_calls = []

class FakeScope:
    def __enter__(self): return self
    def __exit__(self, *a): pass

class FakeStatsTracker:
    def scope(self, name): return FakeScope()
    def denominator(self, **kw): pass
    def stat(self, **kw):
        stat_calls.append(dict(kw))

tracker = FakeStatsTracker()

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

logprobs = torch.tensor([-1.0, -2.0, -3.0])
old_logp = torch.tensor([-1.5, -2.5, -3.5])
mask = torch.tensor([True, True, True])

stat_calls.clear()
fn(
    prox_logp_method="none",
    prox_logp_gt=None,
    old_logp=old_logp,
    logprobs=logprobs,
    versions=None,
    current_version=None,
    compute_logp_mask=mask,
)

# Find stat calls that contain KL-related keys
kl_calls = [
    c for c in stat_calls
    if any(("direct" in k or "taylor" in k or "dual" in k) for k in c.keys())
]

if len(kl_calls) < 3:
    print("0.0")
    sys.exit(0)

# Check that each KL stat call has a denominator kwarg
ok = all("denominator" in c for c in kl_calls)
print("1.0" if ok else "0.0")
PYEOF
)
echo "  Score: $BEHAV4"
# Gate behind core behavioral pass
if [ "$BEHAV_PASS" -eq 1 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.10 * float('${BEHAV4:-0.0}'))")
else
    echo "  (gated: skipped — no core behavioral test passed)"
fi
echo ""

# ---------- REGRESSION: pass-to-pass (0.10) ----------

# [pr_diff] (0.05): Function signature preserved
echo "--- REGRESSION: function signature preserved (0.05) ---"
REGR1=$(python3 << 'PYEOF'
import sys, ast

with open("/workspace/AReaL/areal/trainer/ppo/actor.py") as f:
    source = f.read()

tree = ast.parse(source)
found_log_prox = False
found_log_version = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name == "_log_proximal_approximation_stats":
            found_log_prox = True
            args = [a.arg for a in node.args.args]
            if "logprobs" not in args or "old_logp" not in args:
                print("0.0")
                sys.exit(0)
        if node.name == "_log_version_staleness_stats":
            found_log_version = True

print("1.0" if found_log_prox and found_log_version else "0.0")
PYEOF
)
echo "  Score: $REGR1"
# Gated behind behavioral pass
if [ "$BEHAV_PASS" -eq 1 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.05 * float('${REGR1:-0.0}'))")
else
    echo "  (gated: skipped — no core behavioral test passed)"
fi
echo ""

# [agent_config] (0.05): "No wildcard imports" — AGENTS.md:25 @ a0d12293
echo "--- CONFIG: No wildcard imports (0.05) ---"
CONFIG1=$(python3 << 'PYEOF'
with open("/workspace/AReaL/areal/trainer/ppo/actor.py") as f:
    source = f.read()
has_wildcard = any(
    line.strip().startswith("from ") and "import *" in line
    for line in source.splitlines()
    if not line.strip().startswith("#")
)
print("0.0" if has_wildcard else "1.0")
PYEOF
)
echo "  Score: $CONFIG1"
if [ "$BEHAV_PASS" -eq 1 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.05 * float('${CONFIG1:-0.0}'))")
else
    echo "  (gated: skipped — no core behavioral test passed)"
fi
echo ""

# [agent_config] (0.05): "No GPU-CPU sync in hot paths" — AGENTS.md:90 @ a0d12293
echo "--- CONFIG: No GPU-CPU sync in KL block (0.05) ---"
CONFIG2=$(python3 << 'PYEOF'
import ast

with open("/workspace/AReaL/areal/trainer/ppo/actor.py") as f:
    source = f.read()

tree = ast.parse(source)
has_sync = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_log_proximal_approximation_stats":
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                if child.func.attr in ("item", "tolist", "numpy"):
                    has_sync = True
        break

print("0.0" if has_sync else "1.0")
PYEOF
)
echo "  Score: $CONFIG2"
if [ "$BEHAV_PASS" -eq 1 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.05 * float('${CONFIG2:-0.0}'))")
else
    echo "  (gated: skipped — no core behavioral test passed)"
fi
echo ""

# ---------- FINAL SCORE ----------
echo "==========================="
FINAL=$(python3 -c "print(f'{min(1.0, max(0.0, $SCORE)):.4f}')")
echo "Final deterministic score: $FINAL"

echo "$FINAL" > /logs/verifier/reward.txt
python3 -c "
import json
score = float('$FINAL')
behav = 0.35 * float('${BEHAV1:-0.0}') + 0.25 * float('${BEHAV2:-0.0}')
json.dump({
    'reward': score,
    'behavioral': round(behav, 4),
    'regression': round(0.05 * float('${REGR1:-0.0}'), 4),
    'config': round(0.05 * float('${CONFIG1:-0.0}') + 0.05 * float('${CONFIG2:-0.0}'), 4),
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
