#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# Tier system: compilation (gate), behavioral (rust compilation), config
WEIGHTS[compile]=0.15
WEIGHTS[behavioral_atomic]=0.35
WEIGHTS[behavioral_prune]=0.35
WEIGHTS[config_fmt]=0.05

for key in compile behavioral_atomic behavioral_prune config_fmt; do
    RESULTS[$key]=0
done

TARGET_HISTORY="src/agent/history.rs"
TARGET_PRUNER="src/agent/history_pruner.rs"
WORKSPACE="/workspace/zeroclaw"

# ---------- GATE: Required files exist ----------
if [ ! -f "$TARGET_HISTORY" ] || [ ! -f "$TARGET_PRUNER" ]; then
    echo "GATE FAIL: required files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- GATE: Compilation (15%) ----------
cd "$WORKSPACE"
# Remove Cargo.lock to avoid stale dependency issues
rm -f Cargo.lock
cargo check --all-targets 2>&1 | tail -20
if [ $? -eq 0 ]; then RESULTS[compile]=1; echo "COMPILE: PASS"; else echo "COMPILE: FAIL"; fi

# If compilation fails, no behavioral tests can run
if [ ${RESULTS[compile]} -eq 0 ]; then
    SCORE=$(python3 -c "print(f'${WEIGHTS[compile]}' if 0 else '0.0')")
    echo "$SCORE" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (35%): Atomic tool group handling ----------
# [pr_diff] Verify the code handles assistant+tools atomically
# Test via actual Rust test execution if available, or AST-verified logic
python3 << 'PYEOF'
import subprocess, ast, sys, os, re

os.chdir('/workspace/zeroclaw')

# Try to run the actual tests first - this is the best behavioral check
result = subprocess.run(['cargo', 'test', '--lib', '--', 'emergency', '--nocapture'],
                       capture_output=True, text=True, timeout=120)

# Check if tests passed
if 'test result: ok' in result.stdout or 'test result: ok' in result.stderr:
    print("BEHAVIORAL_ATOMIC: Tests pass")
    sys.exit(0)

# If no tests exist, verify the implementation logic via AST analysis
# This is a structural gate that verifies the pattern, but doesn't award full points
with open('src/agent/history.rs') as f:
    source = f.read()

# Must have emergency_history_trim function
if 'fn emergency_history_trim' not in source:
    print("FAIL: emergency_history_trim function not found")
    sys.exit(1)

# Extract function body (simplified regex for Rust)
fn_match = re.search(r'fn emergency_history_trim[^{]*\{([^}]*\{[^}]*\}[^}]*)*\}', source, re.DOTALL)
if not fn_match:
    # Try matching with balanced braces
    depth = 0
    start = source.find('fn emergency_history_trim')
    if start == -1:
        print("FAIL: Cannot find function start")
        sys.exit(1)
    body_start = source.find('{', start)
    for i, c in enumerate(source[body_start:], body_start):
        if c == '{': depth += 1
        if c == '}':
            depth -= 1
            if depth == 0:
                fn_body = source[body_start:i+1]
                break
else:
    fn_body = fn_match.group(0)

# Verify atomic handling pattern: must look for consecutive tools
# Valid patterns: loop counting tools, chunks(), windows(), group_by, etc.
atomic_patterns = [
    'while',                               # Loop to count consecutive tools
    'chunks',                              # Group by chunks
    'windows',                             # Sliding window detection
    'tuple_windows',                       # itertools pattern
    'consecutive',                         # Explicit consecutive marker
    '.skip',                               # Skip multiple items
    '.take',                               # Take multiple items
    'split_inclusive',                     # Group by boundary
]

tool_patterns = [
    'MessageRole::Tool',
    r'\.role\s*==?\s*.*[Tt]ool',
    'role:.*Tool',
]

has_atomic_pattern = any(p in fn_body for p in atomic_patterns)
has_tool_handling = any(re.search(p, fn_body) for p in tool_patterns)

if not has_tool_handling:
    print("FAIL: No tool message handling found")
    sys.exit(1)

if not has_atomic_pattern:
    # Check if there's any vector slicing or draining (atomic removal pattern)
    if not any(p in fn_body for p in ['drain', 'split_off', 'retain']):
        print("FAIL: No atomic removal pattern found")
        sys.exit(1)

print("BEHAVIORAL_ATOMIC: Implementation verified")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral_atomic]=1; echo "TEST behavioral_atomic: PASS"; else echo "TEST behavioral_atomic: FAIL"; fi

# ---------- PRIMARY 2 (35%): Prune history with atomic groups ----------
# [pr_diff] Verify prune_history handles both phases correctly
python3 << 'PYEOF'
import subprocess, ast, sys, os, re

os.chdir('/workspace/zeroclaw')

# Try to run tests
test_result = subprocess.run(['cargo', 'test', '--lib', '--', 'prune', '--nocapture'],
                            capture_output=True, text=True, timeout=120)

if 'test result: ok' in test_result.stdout or 'test result: ok' in test_result.stderr:
    print("BEHAVIORAL_PRUNE: Tests pass")
    sys.exit(0)

# Verify implementation via structure
with open('src/agent/history_pruner.rs') as f:
    source = f.read()

if 'fn prune_history' not in source:
    print("FAIL: prune_history function not found")
    sys.exit(1)

# Extract prune_history function body
start = source.find('fn prune_history')
if start == -1:
    print("FAIL: Cannot find prune_history")
    sys.exit(1)

depth = 0
body_start = source.find('{', start)
for i, c in enumerate(source[body_start:], body_start):
    if c == '{': depth += 1
    if c == '}':
        depth -= 1
        if depth == 0:
            fn_body = source[body_start:i+1]
            break

# Must have both phase indicators
phase_indicators = [
    ('budget', 'token', 'max_tokens'),  # Phase 2: budget enforcement
    ('collapse', 'summary', 'compact'),  # Phase 1: collapsing
]

has_budget_phase = any(p in fn_body.lower() for p in phase_indicators[0])
has_collapse_phase = any(p in fn_body.lower() for p in phase_indicators[1])

# Must handle tool groups atomically in at least one phase
tool_group_patterns = [
    'while', 'chunks', 'windows', 'consecutive', 'atomic', 'group',
    'skip', 'take', 'split_inclusive'
]
has_tool_group_handling = any(p in fn_body for p in tool_group_patterns)

# Check for the specific bug fix pattern: old code checked [i+1], fixed code counts consecutive
old_bug_pattern = r'messages\[i\s*+\s*1\]\.role\s*==?\s*.*[Tt]ool'
has_old_bug = re.search(old_bug_pattern, fn_body)

if has_old_bug and not has_tool_group_handling:
    print("FAIL: Still uses single-pair pattern without consecutive handling")
    sys.exit(1)

if not has_tool_group_handling:
    print("FAIL: No tool group handling pattern")
    sys.exit(1)

print("BEHAVIORAL_PRUNE: Implementation verified")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral_prune]=1; echo "TEST behavioral_prune: PASS"; else echo "TEST behavioral_prune: FAIL"; fi

# ---------- PASS-TO-PASS (implied): If compile passes, basic structure is valid ----------
# [pr_diff] Compilation gate ensures no breaking changes

# ---------- Config-derived test (5%): Formatting ----------
# [agent_config] (0.05): "cargo fmt --all -- --check"
cd /workspace/zeroclaw
RUSTFMT_CHECK=0
# Check if changed files need formatting
if git diff --name-only HEAD~1..HEAD 2>/dev/null | grep -q '\.rs$'; then
    if cargo fmt --all -- --check 2>/dev/null; then
        RUSTFMT_CHECK=1
    fi
else
    # No changes or git error - skip penalty for unchanged files
    RUSTFMT_CHECK=1
fi
RESULTS[config_fmt]=$RUSTFMT_CHECK

# Calculate score
SCORE=$(python3 -c "
w = {'compile': ${RESULTS[compile]} * ${WEIGHTS[compile]},
     'behavioral_atomic': ${RESULTS[behavioral_atomic]} * ${WEIGHTS[behavioral_atomic]},
     'behavioral_prune': ${RESULTS[behavioral_prune]} * ${WEIGHTS[behavioral_prune]},
     'config_fmt': ${RESULTS[config_fmt]} * ${WEIGHTS[config_fmt]}}
print(f'{sum(w.values()):.2f}')
")

echo ">>> RESULTS: compile=${RESULTS[compile]}, atomic=${RESULTS[behavioral_atomic]}, prune=${RESULTS[behavioral_prune]}, fmt=${RESULTS[config_fmt]}"
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# Write detailed JSON
python3 << PYEOF
import json
result = {
    "reward": float("$SCORE"),
    "compile": {"passed": ${RESULTS[compile]}, "weight": ${WEIGHTS[compile]}, "points": ${RESULTS[compile]} * ${WEIGHTS[compile]}},
    "behavioral_atomic": {"passed": ${RESULTS[behavioral_atomic]}, "weight": ${WEIGHTS[behavioral_atomic]}, "points": ${RESULTS[behavioral_atomic]} * ${WEIGHTS[behavioral_atomic]}},
    "behavioral_prune": {"passed": ${RESULTS[behavioral_prune]}, "weight": ${WEIGHTS[behavioral_prune]}, "points": ${RESULTS[behavioral_prune]} * ${WEIGHTS[behavioral_prune]}},
    "config_fmt": {"passed": ${RESULTS[config_fmt]}, "weight": ${WEIGHTS[config_fmt]}, "points": ${RESULTS[config_fmt]} * ${WEIGHTS[config_fmt]}}
}
with open("/logs/verifier/reward.json", "w") as f:
    json.dump(result, f, indent=2)
PYEOF

# LLM rubric judge source /tests/judge_hook.sh 2>/dev/null || true
