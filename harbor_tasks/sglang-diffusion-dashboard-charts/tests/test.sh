#!/usr/bin/env bash
set -euo pipefail

SCORE=0
FILE="scripts/ci/utils/diffusion/generate_diffusion_dashboard.py"

echo "=== GATE: Syntax check ==="
# [pr_diff] (0): Python syntax gate — abort on failure
if ! python3 -c "import py_compile; py_compile.compile('$FILE', doraise=True)" 2>&1; then
    echo "GATE FAILED: syntax error"
    mkdir -p /logs/verifier
    echo "0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASSED"
echo ""

# After the gate, allow individual tests to fail without aborting
set +e

# ---------------------------------------------------------------------------
# Helper: build test data
# ---------------------------------------------------------------------------
HELPER='
import sys, os, tempfile, json
sys.path.insert(0, ".")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def make_run(ts, sha, cases):
    """Build a run dict from {case_id: {framework: latency}}."""
    cr = {}
    for cid, results in cases.items():
        cr[cid] = {"case_id": cid, "results": {fw: {"latency_seconds": v} for fw, v in results.items()}}
    return {"timestamp": ts, "commit_sha": sha, "comparison_results": cr}

def capture_axes(func, current, history, charts_dir):
    """Call generate_dashboard while capturing matplotlib axes."""
    captured = []
    orig = plt.subplots
    def patched(*a, **kw):
        fig, ax = orig(*a, **kw)
        captured.append(ax)
        return fig, ax
    plt.subplots = patched
    try:
        md = func(current, history, charts_dir=charts_dir)
    finally:
        plt.subplots = orig
    return md, captured
'

# ---------------------------------------------------------------------------
# Fail-to-pass behavioral tests (0.65 total)
# ---------------------------------------------------------------------------

echo "=== F2P: Y-axis scaling uses data range ==="
# [pr_diff] (0.25): Y-axis uses data-range-based limits instead of bottom=0
RESULT=$(python3 -c "
$HELPER
from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

current = make_run('2025-01-15T00:00:00Z', 'abc123',
    {'case1': {'sglang': 48.0, 'vllm-omni': 52.0}})
history = [make_run('2025-01-14T00:00:00Z', 'def456',
    {'case1': {'sglang': 50.0, 'vllm-omni': 53.0}})]

with tempfile.TemporaryDirectory() as td:
    md, axes = capture_axes(generate_dashboard, current, history, td)
    if not axes:
        print('FAIL: no axes captured')
    else:
        ax = axes[0]
        ymin, ymax = ax.get_ylim()
        # Buggy: ymin=0 (bottom=0). Fixed: ymin should be > 10 for values ~48-53
        if ymin > 10:
            print('PASS')
        else:
            print(f'FAIL: ymin={ymin:.2f}, expected > 10 for values in 48-53 range')
" 2>&1 | tail -1)
echo "  $RESULT"
if [[ "$RESULT" == "PASS" ]]; then SCORE=$(python3 -c "print($SCORE + 0.25)"); fi
echo ""

echo "=== F2P: Y-axis never goes negative ==="
# [pr_diff] (0.05): Y-axis bottom should be >= 0 even with low values
RESULT=$(python3 -c "
$HELPER
from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

# Low values close to 0 — ymin must not go negative
current = make_run('2025-01-15T00:00:00Z', 'abc1',
    {'lo': {'sglang': 0.5, 'vllm-omni': 1.0}})
history = [make_run('2025-01-14T00:00:00Z', 'def4',
    {'lo': {'sglang': 0.8, 'vllm-omni': 1.2}})]

with tempfile.TemporaryDirectory() as td:
    md, axes = capture_axes(generate_dashboard, current, history, td)
    if not axes:
        print('FAIL: no axes captured')
    else:
        ymin, _ = axes[0].get_ylim()
        if ymin >= 0:
            print('PASS')
        else:
            print(f'FAIL: ymin={ymin:.4f}, must be >= 0')
" 2>&1 | tail -1)
echo "  $RESULT"
if [[ "$RESULT" == "PASS" ]]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi
echo ""

echo "=== F2P: Legend not in upper-right ==="
# [pr_diff] (0.10): Legend moved away from upper-right to reduce data overlap
RESULT=$(python3 -c "
$HELPER
from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

current = make_run('2025-01-15T00:00:00Z', 'abc1',
    {'case1': {'sglang': 10.0, 'vllm-omni': 12.0}})
history = [make_run('2025-01-14T00:00:00Z', 'def4',
    {'case1': {'sglang': 11.0, 'vllm-omni': 13.0}})]

with tempfile.TemporaryDirectory() as td:
    md, axes = capture_axes(generate_dashboard, current, history, td)
    if not axes:
        print('FAIL: no axes captured')
    else:
        legend = axes[0].get_legend()
        if not legend:
            print('FAIL: no legend')
        else:
            loc = legend._loc
            # matplotlib loc codes: 1=upper right (buggy default)
            # Accept any non-upper-right position (2,3,4,6,7,8,9,10,etc.)
            if loc == 1:
                print(f'FAIL: legend still in upper right (loc={loc})')
            else:
                print('PASS')
" 2>&1 | tail -1)
echo "  $RESULT"
if [[ "$RESULT" == "PASS" ]]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi
echo ""

echo "=== F2P: History window accepts 10+ entries ==="
# [pr_diff] (0.10): Dashboard retains at least 14 runs, not just 7
RESULT=$(python3 -c "
$HELPER
from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

# Provide 12 history entries — buggy code would truncate to 7
current = make_run('2025-01-15T00:00:00Z', 'curr00',
    {'case1': {'sglang': 10.0}})
history = [
    make_run(f'2025-01-{14-i:02d}T00:00:00Z', f'hist{i:02d}',
        {'case1': {'sglang': 10.0 + i * 0.5}})
    for i in range(12)
]

with tempfile.TemporaryDirectory() as td:
    md, axes = capture_axes(generate_dashboard, current, history, td)

# The markdown table should contain all 12 history commit SHAs
# If truncated to 7, several will be missing
found = sum(1 for i in range(12) if f'hist{i:02d}' in md)
if found >= 10:
    print('PASS')
else:
    print(f'FAIL: only {found}/12 history entries in output (truncated?)')
" 2>&1 | tail -1)
echo "  $RESULT"
if [[ "$RESULT" == "PASS" ]]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi
echo ""

echo "=== F2P: Section header reflects actual run count ==="
# [pr_diff] (0.15): Header says actual count, not hardcoded "7"
RESULT=$(python3 -c "
$HELPER
import re
from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

# 4 history + 1 current = 5 runs
current = make_run('2025-01-15T00:00:00Z', 'curr00',
    {'case1': {'sglang': 10.0}})
history = [
    make_run(f'2025-01-{14-i:02d}T00:00:00Z', f'sha{i}',
        {'case1': {'sglang': 10.0 + i}})
    for i in range(4)
]

md = generate_dashboard(current, history)

# Should NOT contain hardcoded 'Last 7 Runs'
if 'Last 7 Runs' in md:
    print('FAIL: header still hardcoded to 7')
else:
    # Accept any dynamic count that matches actual data
    m = re.search(r'Last (\d+) Runs', md)
    if m:
        count = int(m.group(1))
        # 4 history + 1 current = 5
        if count == 5:
            print('PASS')
        elif count == 7:
            print('FAIL: hardcoded to 7')
        else:
            # Accept other reasonable counts (maybe off-by-one in counting)
            print('PASS')
    else:
        # Maybe they changed the header format entirely — check no hardcoded 7
        if '7 Runs' not in md and '(7)' not in md:
            print('PASS')
        else:
            print('FAIL: still references 7 runs')
" 2>&1 | tail -1)
echo "  $RESULT"
if [[ "$RESULT" == "PASS" ]]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi
echo ""

# ---------------------------------------------------------------------------
# Pass-to-pass regression tests (0.20 total)
# ---------------------------------------------------------------------------

echo "=== P2P: Dashboard generates valid markdown ==="
# [pr_diff] (0.10): generate_dashboard returns markdown with title, tables, cases
RESULT=$(python3 -c "
$HELPER
from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

current = make_run('2025-01-15T00:00:00Z', 'abc123def',
    {'wan22_ti2v': {'sglang': 45.2, 'vllm-omni': 50.1},
     'flux_t2i': {'sglang': 12.5, 'vllm-omni': 15.3}})
history = [make_run('2025-01-14T00:00:00Z', 'def456abc',
    {'wan22_ti2v': {'sglang': 46.0, 'vllm-omni': 51.0},
     'flux_t2i': {'sglang': 13.0, 'vllm-omni': 16.0}})]

md = generate_dashboard(current, history)
errors = []
if not isinstance(md, str) or len(md) < 200:
    errors.append('output too short or wrong type')
if '|' not in md:
    errors.append('no table separators')
if 'wan22_ti2v' not in md:
    errors.append('missing case id')
if 'abc123d' not in md:
    errors.append('missing commit sha')
# Verify latency values appear somewhere
if '45.2' not in md and '45.20' not in md:
    errors.append('missing latency value')
if errors:
    print(f'FAIL: {errors}')
else:
    print('PASS')
" 2>&1 | tail -1)
echo "  $RESULT"
if [[ "$RESULT" == "PASS" ]]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi
echo ""

echo "=== P2P: Chart PNG files generated ==="
# [pr_diff] (0.05): Charts saved to disk as PNG when charts_dir provided
RESULT=$(python3 -c "
$HELPER
from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

current = make_run('2025-01-15T00:00:00Z', 'abc1',
    {'test_case': {'sglang': 10.0, 'vllm-omni': 12.0}})
history = [make_run('2025-01-14T00:00:00Z', 'def4',
    {'test_case': {'sglang': 11.0, 'vllm-omni': 13.0}})]

with tempfile.TemporaryDirectory() as td:
    generate_dashboard(current, history, charts_dir=td)
    pngs = [f for f in os.listdir(td) if f.endswith('.png')]
    if len(pngs) >= 1:
        # Verify files are non-trivial (actual images, not empty)
        sizes = [os.path.getsize(os.path.join(td, f)) for f in pngs]
        if all(s > 1000 for s in sizes):
            print('PASS')
        else:
            print(f'FAIL: PNG files too small: {sizes}')
    else:
        print(f'FAIL: no PNG files in {os.listdir(td)}')
" 2>&1 | tail -1)
echo "  $RESULT"
if [[ "$RESULT" == "PASS" ]]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi
echo ""

echo "=== P2P: Multiple cases produce multiple charts ==="
# [pr_diff] (0.05): Each case gets its own chart file
RESULT=$(python3 -c "
$HELPER
from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

current = make_run('2025-01-15T00:00:00Z', 'abc1',
    {'case_a': {'sglang': 10.0, 'vllm-omni': 12.0},
     'case_b': {'sglang': 20.0, 'vllm-omni': 22.0}})
history = [make_run('2025-01-14T00:00:00Z', 'def4',
    {'case_a': {'sglang': 11.0, 'vllm-omni': 13.0},
     'case_b': {'sglang': 21.0, 'vllm-omni': 23.0}})]

with tempfile.TemporaryDirectory() as td:
    generate_dashboard(current, history, charts_dir=td)
    pngs = [f for f in os.listdir(td) if f.endswith('.png')]
    # Should have at least 2 latency charts (one per case)
    if len(pngs) >= 2:
        print('PASS')
    else:
        print(f'FAIL: expected >=2 charts, got {len(pngs)}: {pngs}')
" 2>&1 | tail -1)
echo "  $RESULT"
if [[ "$RESULT" == "PASS" ]]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi
echo ""

# ---------------------------------------------------------------------------
# Config-derived checks (0.10 total)
# ---------------------------------------------------------------------------

echo "=== Config: Module importable with expected API ==="
# [agent_config] (0.05): "New code must match surrounding style" — python/sglang/multimodal_gen/.claude/CLAUDE.md:1
RESULT=$(python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard
    import inspect
    sig = inspect.signature(generate_dashboard)
    params = list(sig.parameters.keys())
    if 'current' not in params and len(params) < 2:
        print('FAIL: generate_dashboard signature changed unexpectedly')
    else:
        print('PASS')
except Exception as e:
    print(f'FAIL: import error: {e}')
" 2>&1 | tail -1)
echo "  $RESULT"
if [[ "$RESULT" == "PASS" ]]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi
echo ""

echo "=== Config: Anti-stub (function produces real output) ==="
# [agent_config] (0.05): Ensure generate_dashboard is not stubbed
RESULT=$(python3 -c "
$HELPER
from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

current = make_run('2025-01-15T00:00:00Z', 'aaa111',
    {'stub_test': {'sglang': 5.0}})
history = [make_run('2025-01-14T00:00:00Z', 'bbb222',
    {'stub_test': {'sglang': 6.0}})]

with tempfile.TemporaryDirectory() as td:
    md, axes = capture_axes(generate_dashboard, current, history, td)

# A real implementation should produce both markdown AND charts
errors = []
if not md or len(md) < 100:
    errors.append('markdown too short')
if not axes:
    errors.append('no matplotlib axes created')
pngs = [f for f in os.listdir(td) if f.endswith('.png')] if os.path.isdir(td) else []
if not pngs:
    errors.append('no chart files')
if errors:
    print(f'FAIL: {errors}')
else:
    print('PASS')
" 2>&1 | tail -1)
echo "  $RESULT"
if [[ "$RESULT" == "PASS" ]]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi
echo ""

# ---------------------------------------------------------------------------
# Final score
# ---------------------------------------------------------------------------

echo "=== FINAL ==="
echo "Score: $SCORE / 1.0"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
score = $SCORE
json.dump({
    'reward': round(score, 2),
}, open('/logs/verifier/reward.json', 'w'))
print(json.dumps({'reward': round(score, 2)}, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
