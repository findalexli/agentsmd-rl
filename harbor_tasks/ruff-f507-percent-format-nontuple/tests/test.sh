#!/usr/bin/env bash
# Verifier for ruff-f507-percent-format-nontuple
# Bug: F507 doesn't flag non-tuple RHS in %-formatting with multiple placeholders
# File: crates/ruff_linter/src/rules/pyflakes/rules/strings.rs
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

RUST_FILE="/workspace/ruff/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs"
FIXTURE="/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py"

echo "=== ruff-f507-percent-format-nontuple verifier ==="

# -- GATE: files exist --
echo ""
echo "GATE: Target files exist"
if [ ! -f "$RUST_FILE" ] || [ ! -f "$FIXTURE" ]; then
    echo "GATE FAIL: required files missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_FIXTURE_LITERALS=0.20
W_BEHAV_RESOLVED_TYPE=0.25
W_BEHAV_FIXTURE_SAFE=0.15
W_STRUCTURAL_IMPORT=0.15
W_STRUCTURAL_ATOM_CHECK=0.15
W_ANTISTUB=0.05
W_CONFIG_NO_PANIC=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): Fixture has literal non-tuple test cases --
echo ""
echo "TEST 1: behavioral -- fixture has literal non-tuple F507 test cases (weight=$W_BEHAV_FIXTURE_LITERALS)"
T1=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py") as f:
    source = f.read()

# Check for literal non-tuple test cases
has_int_case = "'%s %s' % 42" in source
has_float_case = "'%s %s' % 3.14" in source
has_str_case = "'%s %s' % \"hello\"" in source
has_bool_case = "'%s %s' % True" in source
has_none_case = "'%s %s' % None" in source

count = sum([has_int_case, has_float_case, has_str_case, has_bool_case, has_none_case])

if count >= 3:
    print(f"PASS: fixture has {count} literal non-tuple test cases")
    sys.exit(0)
elif count >= 1:
    print(f"PASS: fixture has {count} literal non-tuple test case(s) (partial)")
    sys.exit(0)
else:
    print("FAIL: no literal non-tuple test cases found in fixture")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_FIXTURE_LITERALS)")
fi

# -- TEST 2 (BEHAVIORAL): Uses ResolvedPythonType for type inference --
echo ""
echo "TEST 2: behavioral -- uses ResolvedPythonType for non-tuple detection (weight=$W_BEHAV_RESOLVED_TYPE)"
T2=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs") as f:
    source = f.read()

has_resolved = "ResolvedPythonType" in source
has_python_type = "PythonType" in source

if has_resolved and has_python_type:
    print("PASS: uses ResolvedPythonType and PythonType for inference")
    sys.exit(0)
elif has_resolved:
    print("PASS: uses ResolvedPythonType (partial)")
    sys.exit(0)
else:
    print("FAIL: no ResolvedPythonType usage found")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_RESOLVED_TYPE)")
fi

# -- TEST 3 (BEHAVIORAL): Fixture has safe (non-flagged) variable cases --
echo ""
echo "TEST 3: behavioral -- fixture has non-flagged variable/call cases (weight=$W_BEHAV_FIXTURE_SAFE)"
T3=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py") as f:
    source = f.read()

# Variables should NOT be flagged (they could be tuples)
has_var_case = "banana" in source or "% x" in source
has_attr_case = "obj.attr" in source or ".attr" in source
has_call_case = "get_args()" in source or "% func()" in source

safe_count = sum([has_var_case, has_attr_case, has_call_case])

if safe_count >= 2:
    print(f"PASS: fixture has {safe_count} non-flagged safe cases")
    sys.exit(0)
elif safe_count >= 1:
    print(f"PASS: fixture has {safe_count} non-flagged safe case(s)")
    sys.exit(0)
else:
    print("FAIL: no non-flagged safe cases in fixture")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_FIXTURE_SAFE)")
fi

# -- TEST 4 (STRUCTURAL): type_inference import --
echo ""
echo "TEST 4: structural -- type_inference module imported (weight=$W_STRUCTURAL_IMPORT)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs") as f:
    source = f.read()

has_import = "type_inference" in source
has_use = "use ruff_python_semantic" in source and "ResolvedPythonType" in source

if has_import and has_use:
    print("PASS: type_inference module properly imported")
    sys.exit(0)
elif has_import:
    print("PASS: type_inference referenced")
    sys.exit(0)
else:
    print("FAIL: type_inference not imported")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_IMPORT)")
fi

# -- TEST 5 (STRUCTURAL): PythonType::Tuple exclusion check --
echo ""
echo "TEST 5: structural -- checks resolved type is not Tuple (weight=$W_STRUCTURAL_ATOM_CHECK)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs") as f:
    source = f.read()

# The fix should check: if resolved_type != PythonType::Tuple
has_tuple_check = "PythonType::Tuple" in source
has_atom = "Atom" in source and "ResolvedPythonType" in source

if has_tuple_check and has_atom:
    print("PASS: checks ResolvedPythonType::Atom is not Tuple")
    sys.exit(0)
elif has_tuple_check:
    print("PASS: PythonType::Tuple exclusion exists")
    sys.exit(0)
else:
    print("FAIL: no Tuple exclusion check found")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_ATOM_CHECK)")
fi

# -- TEST 6: Anti-stub --
echo ""
echo "TEST 6: anti-stub -- file retains core logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs") as f:
    source = f.read()

required = ["percent_format_positional_count_mismatch", "PercentFormatPositionalCountMismatch",
            "num_positional", "checker"]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 100:
    print(f"FAIL: file has only {line_count} lines -- looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi


# ---------- Config-derived test (0.05): "Avoid panic!, unreachable!, .unwrap()" ----------
# Source: AGENTS.md line 79 @ b8fad8312fde560943653811ae3e16e22b99dfc7
echo ""
echo "TEST config_no_panic: config-derived -- avoid panic!/unwrap (weight=$W_CONFIG_NO_PANIC)"
T_CONFIG=$(python3 << 'PYEOF'
import sys, os
os.chdir('/workspace/ruff')
import subprocess
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1..HEAD'], capture_output=True, text=True)
changed_rs = [f for f in result.stdout.strip().split('\n') if f.endswith('.rs')]
if not changed_rs:
    result2 = subprocess.run(['find', 'crates', '-name', '*.rs', '-newer', 'Cargo.toml'], capture_output=True, text=True)
    changed_rs = [f for f in result2.stdout.strip().split('\n') if f]
warns = 0
for f in changed_rs[:20]:
    try:
        with open(f) as fh:
            for i, line in enumerate(fh, 1):
                s = line.strip()
                if s.startswith('//'):
                    continue
                if ('panic!(' in s or '.unwrap()' in s) and 'test' not in f:
                    warns += 1
    except: pass
if warns > 5:
    print('FAIL: ' + str(warns) + ' uses of panic!/unwrap in changed files')
    sys.exit(1)
print('PASS')
PYEOF
)
echo "$T_CONFIG"
if echo "$T_CONFIG" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_PANIC)")
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
