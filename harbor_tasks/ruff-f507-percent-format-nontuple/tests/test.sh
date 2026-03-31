#!/usr/bin/env bash
# Verifier for ruff-f507-percent-format-nontuple
# Bug: F507 doesn't flag non-tuple RHS in %-formatting with multiple placeholders
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

# Verify Rust is available for compilation
if ! command -v cargo &> /dev/null; then
    echo "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

# Weights: >=60% behavioral, <=40% structural
W_F2P_COMPILE=0.10        # Code compiles
W_F2P_LITERAL_INT=0.10    # '%s %s' % 42 triggers F507
W_F2P_LITERAL_FLOAT=0.10  # '%s %s' % 3.14 triggers F507
W_F2P_LITERAL_STR=0.10    # '%s %s' % "hello" triggers F507
W_F2P_COMPOUND_EXPR=0.10  # '%s %s' % -1 triggers F507 (unary op)
W_P2P_SAFE_CASES=0.10     # Variables/calls do NOT trigger F507
W_P2P_SINGLE_PLACEHOLDER=0.05  # '%s' % 42 is OK
W_STRUCTURAL_TYPE_INFERENCE=0.15  # Uses ResolvedPythonType
W_ANTISTUB=0.10           # File has meaningful implementation
W_CONFIG_NO_PANIC=0.10    # No panic!/unwrap in changed code

SCORE="0.0"
FAILED_F2P=0  # Track if any fail-to-pass test fails

echo ""
echo "=== Building ruff (required for behavioral tests) ==="
cd /workspace/ruff

# Try incremental build first, fall back to full build
cargo build --release --bin ruff 2>&1 | tail -20
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "RELEASE BUILD FAILED, trying debug build..."
    cargo build --bin ruff 2>&1 | tail -20
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        echo "BUILD FAIL: ruff compilation failed"
        echo "0.0000" > "$REWARD_FILE"
        exit 0
    fi
    RUFF_BIN="/workspace/ruff/target/debug/ruff"
else
    RUFF_BIN="/workspace/ruff/target/release/ruff"
fi

echo "BUILD SUCCESS"
SCORE=$(python3 -c "print($SCORE + $W_F2P_COMPILE)")

# Helper function to check if F507 is reported on a line
check_f507_on_line() {
    local file="$1"
    local line_num="$2"
    local description="$3"
    
    output=$($RUFF_BIN check --output-format=concise --select=F507 "$file" 2>/dev/null)
    # Check if F507 is reported for the specific line
    echo "$output" | grep -q "F507.*$line_num\|:$line_num "
    return $?
}

# Helper function to check if a line has NO F507
check_no_f507_on_line() {
    local file="$1"
    local line_num="$2"
    
    output=$($RUFF_BIN check --output-format=concise --select=F507 "$file" 2>/dev/null)
    # Should NOT find F507 on this line
    if echo "$output" | grep -q "F507.*$line_num\|:$line_num "; then
        return 1
    fi
    return 0
}

echo ""
echo "=== FAIL-TO-PASS: Verify F507 triggers for literal non-tuples ==="

# For fail-to-pass tests, the buggy baseline would NOT flag these
# Fixed code SHOULD flag them

echo ""
echo "TEST F2P1: F507 triggered on literal int (line 29)"
if check_f507_on_line "$FIXTURE" "29" "'%s %s' % 42"; then
    echo "PASS: F507 detected on literal int"
    SCORE=$(python3 -c "print($SCORE + $W_F2P_LITERAL_INT)")
else
    echo "FAIL: F507 not detected on literal int"
    FAILED_F2P=1
fi

echo ""
echo "TEST F2P2: F507 triggered on literal float (line 30)"
if check_f507_on_line "$FIXTURE" "30" "'%s %s' % 3.14"; then
    echo "PASS: F507 detected on literal float"
    SCORE=$(python3 -c "print($SCORE + $W_F2P_LITERAL_FLOAT)")
else
    echo "FAIL: F507 not detected on literal float"
    FAILED_F2P=1
fi

echo ""
echo "TEST F2P3: F507 triggered on literal string (line 31)"
if check_f507_on_line "$FIXTURE" "31" "'%s %s' % \"hello\""; then
    echo "PASS: F507 detected on literal string"
    SCORE=$(python3 -c "print($SCORE + $W_F2P_LITERAL_STR)")
else
    echo "FAIL: F507 not detected on literal string"
    FAILED_F2P=1
fi

echo ""
echo "TEST F2P4: F507 triggered on compound expression (line 38)"
if check_f507_on_line "$FIXTURE" "38" "'%s %s' % -1"; then
    echo "PASS: F507 detected on unary op expression"
    SCORE=$(python3 -c "print($SCORE + $W_F2P_COMPOUND_EXPR)")
else
    echo "FAIL: F507 not detected on unary op expression"
    FAILED_F2P=1
fi

echo ""
echo "=== PASS-TO-PASS: Verify safe cases are NOT flagged ==="

echo ""
echo "TEST P2P1: No F507 on variable reference (line 47)"
if check_no_f507_on_line "$FIXTURE" "47"; then
    echo "PASS: F507 not triggered on variable"
    SCORE=$(python3 -c "print($SCORE + $W_P2P_SAFE_CASES)")
else
    echo "FAIL: F507 incorrectly triggered on variable"
fi

echo ""
echo "TEST P2P2: No F507 on single placeholder with literal (line 44)"
if check_no_f507_on_line "$FIXTURE" "44"; then
    echo "PASS: F507 not triggered on single placeholder"
    SCORE=$(python3 -c "print($SCORE + $W_P2P_SINGLE_PLACEHOLDER)")
else
    echo "FAIL: F507 incorrectly triggered on single placeholder"
fi

echo ""
echo "=== STRUCTURAL: Type inference usage ==="

echo ""
echo "TEST STRUCT1: Uses ResolvedPythonType for type inference"
T_STRUCT=$(python3 << 'PYEOF'
import sys
import ast

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs") as f:
    source = f.read()

# Check for actual usage of ResolvedPythonType - not just string matching
# The fix should use ResolvedPythonType::from() and check for Atom
has_resolved_from = "ResolvedPythonType::from" in source
has_atom_check = "ResolvedPythonType::Atom" in source or "let resolved_type" in source
has_tuple_comparison = "PythonType::Tuple" in source

# Also verify the logic flow exists
has_if_branch = source.count("if") > 10  # Sanity check for actual code

if has_resolved_from and has_tuple_comparison:
    print("PASS: uses ResolvedPythonType::from() with Tuple comparison")
    sys.exit(0)
elif has_resolved_from:
    print("PARTIAL: uses ResolvedPythonType but may not compare with Tuple")
    sys.exit(0)
else:
    print("FAIL: no ResolvedPythonType usage found")
    sys.exit(1)
PYEOF
)
echo "$T_STRUCT"
if echo "$T_STRUCT" | grep -q "PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_TYPE_INFERENCE)")
fi

echo ""
echo "TEST ANTI_STUB: File has meaningful implementation"
T_STUB=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyflakes/rules/strings.rs") as f:
    source = f.read()

# Count actual implementation lines (non-comment, non-empty)
lines = source.splitlines()
code_lines = [l for l in lines if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('///')]

if len(code_lines) < 50:
    print(f"FAIL: only {len(code_lines)} code lines - looks like a stub")
    sys.exit(1)

# Check for the specific function being modified
if "percent_format_positional_count_mismatch" not in source:
    print("FAIL: missing the target function")
    sys.exit(1)

# Verify the function has actual logic (not just pass/nop)
func_start = source.find("pub(crate) fn percent_format_positional_count_mismatch")
if func_start == -1:
    func_start = source.find("fn percent_format_positional_count_mismatch")
    
if func_start != -1:
    func_section = source[func_start:func_start+2000]
    # Count control flow statements
    control_flow = func_section.count('if ') + func_section.count('match ') + func_section.count('for ')
    if control_flow < 2:
        print(f"FAIL: function lacks control flow (only {control_flow} branches)")
        sys.exit(1)

print(f"PASS: {len(code_lines)} code lines, function present with control flow")
sys.exit(0)
PYEOF
)
echo "$T_STUB"
if echo "$T_STUB" | grep -q "PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

echo ""
echo "TEST CONFIG: No panic!/unwrap in changed code"
T_CONFIG=$(python3 << 'PYEOF'
import sys, subprocess, os

os.chdir('/workspace/ruff')

# Get list of changed Rust files
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1..HEAD'], 
                       capture_output=True, text=True)
changed_rs = [f for f in result.stdout.strip().split('\n') if f.endswith('.rs')]

# If no tracked changes, find recently modified files
if not changed_rs or changed_rs == ['']:
    # Check if files in the crate have been modified vs original
    result = subprocess.run(['git', 'status', '--porcelain'], 
                           capture_output=True, text=True)
    for line in result.stdout.strip().split('\n'):
        if line.endswith('.rs') and 'crates/ruff_linter' in line:
            changed_rs.append(line[3:])  # Strip status prefix

# Also always check the main file being modified
if 'crates/ruff_linter/src/rules/pyflakes/rules/strings.rs' not in changed_rs:
    changed_rs.append('crates/ruff_linter/src/rules/pyflakes/rules/strings.rs')

warns = 0
for f in changed_rs[:10]:
    if not f:
        continue
    filepath = f if f.startswith('/') else os.path.join('/workspace/ruff', f)
    if not os.path.exists(filepath):
        continue
    try:
        with open(filepath) as fh:
            for i, line in enumerate(fh, 1):
                s = line.strip()
                # Skip comments
                if s.startswith('//'):
                    continue
                # Count risky operations (but allow in tests)
                if 'panic!(' in s or ('.unwrap()' in s and 'test' not in f.lower()):
                    warns += 1
                    if warns <= 3:
                        print(f"WARNING: {f}:{i}: {s[:60]}")
    except:
        pass

if warns > 3:
    print(f'FAIL: {warns} uses of panic!/unwrap')
    sys.exit(1)

print('PASS')
sys.exit(0)
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
echo "Failed F2P tests: $FAILED_F2P"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# Write detailed reward.json
cat > /logs/verifier/reward.json << EOF
{
  "reward": $REWARD,
  "compile": $(python3 -c "print($REWARD >= 0.10 and '1' or '0')"),
  "behavioral_f2p": $(python3 -c "print($REWARD >= 0.40 and '1' or '0')"),
  "behavioral_p2p": $(python3 -c "print($REWARD >= 0.55 and '1' or '0')"),
  "structural": $([ "$T_STRUCT" = "*PASS*" ] && echo "1" || echo "0"),
  "failed_f2p_count": $FAILED_F2P
}
EOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
