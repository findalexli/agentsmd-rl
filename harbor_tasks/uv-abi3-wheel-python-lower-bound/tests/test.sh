#!/usr/bin/env bash
set +e

REPO="/repo"
TOTAL=0.0
add() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

cd "$REPO"

TARGET_FILE="crates/uv-distribution-types/src/prioritized_distribution.rs"

###############################################################################
# GATE (0.00): Rust syntax — must compile the modified crate
###############################################################################
# [pr_diff] (0.00): Code must compile
echo "=== GATE: cargo check ==="
if ! cargo check -p uv-distribution-types 2>&1; then
    echo "GATE FAILED: compilation error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE passed."

###############################################################################
# Behavioral: abi3 wheels produce >= markers (0.35)
###############################################################################
# [pr_diff] (0.35): abi3 ABI tag causes python version to be lower bound, not exact
echo "=== Behavioral: abi3 wheels produce >= markers ==="
SCORE_ABI3=0.0

cp "$TARGET_FILE" "$TARGET_FILE.bak"

python3 <<'PYEOF'
path = "/repo/crates/uv-distribution-types/src/prioritized_distribution.rs"
with open(path, "r") as f:
    content = f.read()

test_code = '''
    #[test]
    fn test_abi3_lower_bound_injected() {
        // abi3 wheel with major.minor: cp39-abi3 means CPython >= 3.9
        assert_python_markers(
            "pkg-1.0-cp39-abi3-any.whl",
            "python_full_version >= '3.9' and platform_python_implementation == 'CPython'",
        );
        // abi3 wheel with different version: cp312-abi3
        assert_python_markers(
            "pkg-1.0-cp312-abi3-any.whl",
            "python_full_version >= '3.12' and platform_python_implementation == 'CPython'",
        );
        // abi3 wheel with major-only tag: cp3-abi3
        assert_python_markers(
            "pkg-1.0-cp3-abi3-any.whl",
            "python_full_version >= '3' and platform_python_implementation == 'CPython'",
        );
    }
'''

last_brace = content.rfind("}")
if last_brace != -1:
    content = content[:last_brace] + test_code + "\n" + content[last_brace:]

with open(path, "w") as f:
    f.write(content)
PYEOF

if cargo test -p uv-distribution-types -- test_abi3_lower_bound_injected --no-fail-fast 2>&1; then
    SCORE_ABI3=0.35
    echo "abi3 lower bound tests: PASSED"
else
    echo "abi3 lower bound tests: FAILED"
fi

mv "$TARGET_FILE.bak" "$TARGET_FILE"

echo "Score: $SCORE_ABI3"
add "$SCORE_ABI3"

###############################################################################
# Behavioral: abi3 with platform markers (0.15)
###############################################################################
# [pr_diff] (0.15): abi3 combined with platform-specific tags produces correct combined markers
echo "=== Behavioral: abi3 + platform markers ==="
SCORE_ABI3_PLATFORM=0.0

cp "$TARGET_FILE" "$TARGET_FILE.bak"

python3 <<'PYEOF'
path = "/repo/crates/uv-distribution-types/src/prioritized_distribution.rs"
with open(path, "r") as f:
    content = f.read()

test_code = '''
    #[test]
    fn test_abi3_combined_markers_injected() {
        // abi3 wheel with platform-specific filename
        assert_implied_markers(
            "pkg-1.0-cp39-abi3-manylinux_2_28_x86_64.whl",
            "python_full_version >= '3.9' and platform_python_implementation == 'CPython' and sys_platform == 'linux' and platform_machine == 'x86_64'",
        );
    }
'''

last_brace = content.rfind("}")
if last_brace != -1:
    content = content[:last_brace] + test_code + "\n" + content[last_brace:]

with open(path, "w") as f:
    f.write(content)
PYEOF

if cargo test -p uv-distribution-types -- test_abi3_combined_markers_injected --no-fail-fast 2>&1; then
    SCORE_ABI3_PLATFORM=0.15
    echo "abi3 combined markers test: PASSED"
else
    echo "abi3 combined markers test: FAILED"
fi

mv "$TARGET_FILE.bak" "$TARGET_FILE"

echo "Score: $SCORE_ABI3_PLATFORM"
add "$SCORE_ABI3_PLATFORM"

###############################################################################
# Behavioral: non-abi3 wheels still use exact version (0.15)
###############################################################################
# [pr_diff] (0.15): Non-abi3 wheels must not be affected — still exact match
echo "=== Behavioral: non-abi3 still exact ==="
SCORE_NON_ABI3=0.0

cp "$TARGET_FILE" "$TARGET_FILE.bak"

python3 <<'PYEOF'
path = "/repo/crates/uv-distribution-types/src/prioritized_distribution.rs"
with open(path, "r") as f:
    content = f.read()

test_code = '''
    #[test]
    fn test_non_abi3_still_exact_injected() {
        // Non-abi3 wheel: cp39-cp39 should still be exact 3.9.*
        assert_python_markers(
            "pkg-1.0-cp39-cp39-any.whl",
            "python_full_version >= '3.9' and python_full_version < '3.10' and platform_python_implementation == 'CPython'",
        );
        // Pure python wheel should not be affected
        assert_python_markers(
            "pkg-1.0-py3-none-any.whl",
            "python_full_version >= '3' and python_full_version < '4'",
        );
    }
'''

last_brace = content.rfind("}")
if last_brace != -1:
    content = content[:last_brace] + test_code + "\n" + content[last_brace:]

with open(path, "w") as f:
    f.write(content)
PYEOF

if cargo test -p uv-distribution-types -- test_non_abi3_still_exact_injected --no-fail-fast 2>&1; then
    SCORE_NON_ABI3=0.15
    echo "non-abi3 exact version test: PASSED"
else
    echo "non-abi3 exact version test: FAILED"
fi

mv "$TARGET_FILE.bak" "$TARGET_FILE"

echo "Score: $SCORE_NON_ABI3"
add "$SCORE_NON_ABI3"

###############################################################################
# Pass-to-pass: existing unit tests still pass (0.15)
###############################################################################
# [pr_diff] (0.15): Existing implied marker tests must not regress
echo "=== P2P: existing unit tests ==="
SCORE_P2P=0.0
if cargo test -p uv-distribution-types -- test_implied_python_markers test_implied_markers --no-fail-fast 2>&1; then
    SCORE_P2P=0.15
    echo "Existing tests: PASSED"
else
    echo "Existing tests: FAILED"
fi
echo "Score: $SCORE_P2P"
add "$SCORE_P2P"

###############################################################################
# Config-derived: no unwrap() in changed code (0.10)
###############################################################################
# [agent_config] (0.10): "AVOID using .unwrap()" — CLAUDE.md:7
echo "=== Config: no unwrap in implied_python_markers ==="
SCORE_UNWRAP=0.0

python3 <<'PYEOF'
import sys

path = "/repo/crates/uv-distribution-types/src/prioritized_distribution.rs"
with open(path, "r") as f:
    content = f.read()

start = content.find("fn implied_python_markers(")
if start == -1:
    print("Function not found")
    sys.exit(1)

brace_count = 0
in_func = False
end = start
for i in range(start, len(content)):
    if content[i] == '{':
        brace_count += 1
        in_func = True
    elif content[i] == '}':
        brace_count -= 1
        if in_func and brace_count == 0:
            end = i + 1
            break

func_body = content[start:end]
if ".unwrap()" in func_body:
    print("FAIL: .unwrap() found in implied_python_markers")
    sys.exit(1)
else:
    print("OK: no .unwrap() in implied_python_markers")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    SCORE_UNWRAP=0.10
fi
echo "Score: $SCORE_UNWRAP"
add "$SCORE_UNWRAP"

###############################################################################
# Anti-stub: function contains meaningful abi3 logic (0.10)
###############################################################################
# [pr_diff] (0.10): Solution must contain actual abi3 detection logic, not a stub
echo "=== Anti-stub: meaningful abi3 logic ==="
SCORE_STUB=0.0

python3 <<'PYEOF'
import sys

path = "/repo/crates/uv-distribution-types/src/prioritized_distribution.rs"
with open(path, "r") as f:
    content = f.read()

start = content.find("fn implied_python_markers(")
if start == -1:
    print("FAIL: function not found")
    sys.exit(1)

brace_count = 0
in_func = False
end = start
for i in range(start, len(content)):
    if content[i] == '{':
        brace_count += 1
        in_func = True
    elif content[i] == '}':
        brace_count -= 1
        if in_func and brace_count == 0:
            end = i + 1
            break

func_body = content[start:end]

# Must reference abi3 in some form
has_abi3_ref = "abi3" in func_body.lower() or "Abi3" in func_body
# Must use greater_than_equal or >= logic
has_gte = "greater_than_equal" in func_body or ">=" in func_body
# Must still have equals_star for non-abi3 path
has_exact = "equals_star" in func_body or "==" in func_body

if has_abi3_ref and has_gte and has_exact:
    print("OK: contains abi3 detection with both >= and ==* paths")
    sys.exit(0)
else:
    print(f"FAIL: abi3_ref={has_abi3_ref}, gte={has_gte}, exact={has_exact}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    SCORE_STUB=0.10
fi
echo "Score: $SCORE_STUB"
add "$SCORE_STUB"

###############################################################################
# Summary
###############################################################################
echo ""
echo "=== TOTAL ==="
echo "Total: $TOTAL"

# Write reward
echo "$TOTAL" > /logs/verifier/reward.txt

# Build JSON breakdown
python3 -c "
import json
data = {
    'reward': $TOTAL,
    'behavioral': round($SCORE_ABI3 + $SCORE_ABI3_PLATFORM + $SCORE_NON_ABI3, 4),
    'regression': round($SCORE_P2P, 4),
    'config': round($SCORE_UNWRAP, 4),
    'structural': round($SCORE_STUB, 4),
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'), indent=2)
print(json.dumps(data, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
