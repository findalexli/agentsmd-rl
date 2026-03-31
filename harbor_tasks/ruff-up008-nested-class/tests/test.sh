#!/usr/bin/env bash
# Verifier for ruff-up008-nested-class
# Bug: UP008 false positive for nested classes where inner class name is unreachable
# Fix: Use semantic scope-based class discovery instead of statement-parent walking
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

RUST_FILE="/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs"
FIXTURE="/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py"

echo "=== ruff-up008-nested-class verifier ==="

# -- GATE: Code compiles --
echo ""
echo "GATE: Rust code compiles"
cd /workspace/ruff
# Quick syntax check first
if ! command -v rustc &>/dev/null; then
    echo "GATE SKIP: rustc not available, proceeding with syntax/other checks"
else
    # Try a light compilation check on just the changed file (if cargo is available)
    if command -v cargo &>/dev/null; then
        cargo check --package ruff_linter --lib 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "GATE WARNING: cargo check failed, but proceeding with tests"
        else
            echo "GATE PASS: Code compiles"
        fi
    fi
fi

# Weights: >=60% behavioral, <=40% structural
# All weights must sum to 1.0
W_BEHAV_NESTED_NO_FALSE_POSITIVE=0.30  # Core fix: nested class super() doesn't trigger UP008
W_BEHAV_DOTTED_CHAIN=0.20              # Dotted chain works: super(Outer.Inner, self) at correct nesting
W_BEHAV_TRUE_POSITIVE_STILL_WORKS=0.15 # Regular super(Class, self) still triggers UP008
W_BEHAV_TODO_REMOVED=0.05              # TODO comments removed from fixture
W_P2P_SNAPSHOT_PASS=0.15               # Pass-to-pass: existing snapshot tests pass
W_STRUCTURAL_SCOPE_BASED=0.10          # Uses semantic scopes (not statement parents)
W_ANTISTUB=0.05                        # File has actual implementation

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL FAIL-TO-PASS): Nested class super() does NOT trigger UP008 --
echo ""
echo "TEST 1: behavioral F2P -- nested class super() does not trigger false positive (weight=$W_BEHAV_NESTED_NO_FALSE_POSITIVE)"
T1=$(python3 << 'PYEOF'
import subprocess
import sys
import tempfile
import os

# Test case: nested class with super(Inner, self) should NOT trigger UP008
# (Inner is not accessible at that scope - would be NameError at runtime)
test_code = '''
class Base:
    def __init__(self, foo):
        self.foo = foo

class Outer:
    class Inner(Base):
        def __init__(self, foo):
            super(Inner, self).__init__(foo)  # Should NOT trigger UP008
'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_code)
    test_file = f.name

try:
    result = subprocess.run(
        ['/workspace/ruff/target/release/ruff', 'check', '--select', 'UP008', test_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    # If no UP008 violation, the fix works (exit code 0, empty output)
    if result.returncode == 0 and 'UP008' not in result.stdout and 'UP008' not in result.stderr:
        print("PASS: Nested class super() correctly does NOT trigger UP008")
        sys.exit(0)
    else:
        print(f"FAIL: UP008 still triggers on nested class (output: {result.stdout} {result.stderr})")
        sys.exit(1)
except subprocess.TimeoutExpired:
    print("FAIL: ruff check timed out")
    sys.exit(1)
except FileNotFoundError:
    # Try building first
    print("INFO: ruff binary not found, attempting to use cargo run...")
    try:
        result = subprocess.run(
            ['cargo', 'run', '--release', '--', 'check', '--select', 'UP008', test_file],
            cwd='/workspace/ruff',
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0 and 'UP008' not in result.stdout and 'UP008' not in result.stderr:
            print("PASS: Nested class super() correctly does NOT trigger UP008 (via cargo run)")
            sys.exit(0)
        else:
            print(f"FAIL: UP008 still triggers on nested class")
            sys.exit(1)
    except Exception as e:
        print(f"FAIL: Could not run ruff: {e}")
        sys.exit(1)
finally:
    os.unlink(test_file)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_NESTED_NO_FALSE_POSITIVE)")
fi

# -- TEST 2 (BEHAVIORAL FAIL-TO-PASS): Multi-level nesting with dotted chain --
echo ""
echo "TEST 2: behavioral F2P -- multi-level dotted chain not falsely flagged (weight=$W_BEHAV_DOTTED_CHAIN)"
T2=$(python3 << 'PYEOF'
import subprocess
import sys
import tempfile
import os

# Test case: super(Inner.C, self) with extra nesting - should NOT trigger
test_code = '''
class Base:
    def __init__(self, foo):
        self.foo = foo

class HigherLevelsOfNesting:
    class Inner:
        class C(Base):
            def __init__(self, foo):
                super(Inner.C, self).__init__(foo)  # Should NOT trigger UP008
'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_code)
    test_file = f.name

try:
    result = subprocess.run(
        ['/workspace/ruff/target/release/ruff', 'check', '--select', 'UP008', test_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode == 0 and 'UP008' not in result.stdout:
        print("PASS: Multi-level dotted chain correctly does NOT trigger UP008")
        sys.exit(0)
    else:
        # Try cargo run fallback
        result = subprocess.run(
            ['cargo', 'run', '--release', '--', 'check', '--select', 'UP008', test_file],
            cwd='/workspace/ruff',
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0 and 'UP008' not in result.stdout:
            print("PASS: Multi-level dotted chain correctly does NOT trigger UP008 (via cargo run)")
            sys.exit(0)
        else:
            print(f"FAIL: UP008 triggers on multi-level dotted chain")
            sys.exit(1)
except Exception as e:
    print(f"FAIL: Error running test: {e}")
    sys.exit(1)
finally:
    os.unlink(test_file)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_DOTTED_CHAIN)")
fi

# -- TEST 3 (BEHAVIORAL): True positive still works --
echo ""
echo "TEST 3: behavioral -- regular super(Class, self) still triggers UP008 (weight=$W_BEHAV_TRUE_POSITIVE_STILL_WORKS)"
T3=$(python3 << 'PYEOF'
import subprocess
import sys
import tempfile
import os

# Test case: regular super(Class, self) at top level should STILL trigger
test_code = '''
class Base:
    def __init__(self, foo):
        self.foo = foo

class MyClass(Base):
    def __init__(self, foo):
        super(MyClass, self).__init__(foo)  # SHOULD trigger UP008
'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_code)
    test_file = f.name

try:
    result = subprocess.run(
        ['/workspace/ruff/target/release/ruff', 'check', '--select', 'UP008', test_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    # Should find UP008 violation
    if 'UP008' in result.stdout or 'UP008' in result.stderr or result.returncode != 0:
        print("PASS: Regular super(Class, self) still triggers UP008")
        sys.exit(0)
    else:
        # Try cargo run
        result = subprocess.run(
            ['cargo', 'run', '--release', '--', 'check', '--select', 'UP008', test_file],
            cwd='/workspace/ruff',
            capture_output=True,
            text=True,
            timeout=120
        )
        if 'UP008' in result.stdout or result.returncode != 0:
            print("PASS: Regular super(Class, self) still triggers UP008 (via cargo run)")
            sys.exit(0)
        else:
            print("FAIL: Regular super(Class, self) should trigger UP008 but doesn't")
            sys.exit(1)
except Exception as e:
    print(f"FAIL: Error running test: {e}")
    sys.exit(1)
finally:
    os.unlink(test_file)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_TRUE_POSITIVE_STILL_WORKS)")
fi

# -- TEST 4 (BEHAVIORAL): TODO comments removed from fixture --
echo ""
echo "TEST 4: behavioral -- TODO comments about nested class false positive removed (weight=$W_BEHAV_TODO_REMOVED)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py") as f:
    source = f.read()

# The old code had TODO(charlie) comments about false positives
if "false positive until nested class matching is fixed" in source:
    print("FAIL: TODO comment about nested class false positive still present")
    sys.exit(1)
else:
    print("PASS: TODO comments about nested class false positive removed")
    sys.exit(0)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_TODO_REMOVED)")
fi

# -- TEST 5 (PASS-TO-PASS): Existing UP008 tests still pass --
echo ""
echo "TEST 5: P2P -- existing UP008 snapshot tests pass (weight=$W_P2P_SNAPSHOT_PASS)"
T5=$(python3 << 'PYEOF'
import subprocess
import sys

# Run the UP008-specific tests using cargo test
result = subprocess.run(
    ['cargo', 'test', '--package', 'ruff_linter', '--', 'UP008', '--nocapture'],
    cwd='/workspace/ruff',
    capture_output=True,
    text=True,
    timeout=300
)

# Check for test failures
if result.returncode == 0 and ('test result: ok' in result.stdout or 'test result: ok' in result.stderr):
    print("PASS: UP008 snapshot tests pass")
    sys.exit(0)
elif 'UP008' not in result.stdout and 'UP008' not in result.stderr:
    # If no UP008 tests found, check if we can at least parse the fixture
    result2 = subprocess.run(
        ['/workspace/ruff/target/release/ruff', 'check', '--select', 'UP008', '/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py'],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Just verify it runs without panic
    if result2.returncode in [0, 1]:  # 0 = no violations, 1 = violations found
        print("PASS: UP008 runs on fixture without errors (P2P via manual run)")
        sys.exit(0)
    else:
        print(f"FAIL: ruff execution failed")
        sys.exit(1)
else:
    print(f"FAIL: UP008 tests failed")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P_SNAPSHOT_PASS)")
fi

# -- TEST 6 (STRUCTURAL): Uses semantic scope-based approach --
echo ""
echo "TEST 6: structural -- uses semantic scope-based class discovery (weight=$W_STRUCTURAL_SCOPE_BASED)"
T6=$(python3 << 'PYEOF'
import ast
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

# The fix should use semantic scopes, not statement parent walking
# Check for scope-based patterns (but allow different variable names)
patterns = [
    "semantic()" in source,
    "ScopeKind" in source,
    "current_scope" in source or "current_scopes" in source,
]

# Should NOT use old parent-finding approach
old_pattern = 'parents.find(|stmt| stmt.is_class_def_stmt())'

if all(patterns):
    if old_pattern not in source:
        print("PASS: Uses semantic scope-based approach, old pattern removed")
        sys.exit(0)
    else:
        print("PARTIAL: Uses semantic scopes but old pattern still present")
        sys.exit(0)  # Still give partial credit
else:
    print("FAIL: Not using semantic scope-based approach")
    sys.exit(1)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_SCOPE_BASED)")
elif echo "$T6" | grep -q "PARTIAL"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_SCOPE_BASED * 0.5)")
fi

# -- TEST 7: Anti-stub (counts only if behavioral tests pass) --
echo ""
echo "TEST 7: anti-stub -- implementation not gutted (weight=$W_ANTISTUB)"
T7=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

# Check for reasonable implementation depth
lines = source.splitlines()

# Count non-trivial lines (not empty, not just brackets, not just comments)
meaningful = 0
for line in lines:
    stripped = line.strip()
    if stripped and not stripped.startswith('//') and len(stripped) > 3:
        if stripped not in ['}', '{', ');', ')', '(']:
            meaningful += 1

# Should have substantial implementation
if meaningful < 30:
    print(f"FAIL: Only {meaningful} meaningful lines - looks like a stub")
    sys.exit(1)

# Check for key function components
required_concepts = ['super_call_with_parameters', 'checker', 'ExprCall']
missing = [c for c in required_concepts if c not in source]
if missing:
    print(f"FAIL: Missing expected components: {missing}")
    sys.exit(1)

print(f"PASS: File has {meaningful} meaningful lines, core logic present")
sys.exit(0)
PYEOF
)
echo "$T7"
# Anti-stub only counts if at least one F2P behavioral test passed
if echo "$T7" | grep -q "^PASS" && [ $(python3 -c "print($SCORE >= 0.35)") = "True" ]; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
elif echo "$T7" | grep -q "^PASS"; then
    echo "(Anti-stub skipped: F2P tests not yet passing)"
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# Optional: Write detailed breakdown
python3 << PYEOF > "$(dirname "$REWARD_FILE")/reward.json"
{
  "reward": $REWARD,
  "breakdown": {
    "nested_no_fp": "$(echo "$T1" | grep -q '^PASS' && echo 'PASS' || echo 'FAIL')",
    "dotted_chain": "$(echo "$T2" | grep -q '^PASS' && echo 'PASS' || echo 'FAIL')",
    "true_positive": "$(echo "$T3" | grep -q '^PASS' && echo 'PASS' || echo 'FAIL')",
    "todo_removed": "$(echo "$T4" | grep -q '^PASS' && echo 'PASS' || echo 'FAIL')",
    "p2p_snapshot": "$(echo "$T5" | grep -q '^PASS' && echo 'PASS' || echo 'FAIL')",
    "scope_based": "$(echo "$T6" | grep -q 'PASS' && echo 'PASS' || echo 'FAIL')",
    "anti_stub": "$(echo "$T7" | grep -q '^PASS' && echo 'PASS' || echo 'FAIL')"
  }
}
PYEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
