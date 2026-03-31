#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="/repo"
REWARD=0.0
TOTAL=0.0

cd "$REPO"

###############################################################################
# GATE: Rust syntax check — modified files must parse
###############################################################################
# [pr_diff] (gate): Core source files must be valid Rust syntax
GATE_FILES=(
    "crates/ty_python_semantic/src/semantic_index/builder.rs"
    "crates/ty_python_semantic/src/semantic_index/predicate.rs"
    "crates/ty_python_semantic/src/semantic_index/reachability_constraints.rs"
    "crates/ty_python_semantic/src/types/narrow.rs"
)
GATE_PASS=true
for f in "${GATE_FILES[@]}"; do
    if [ -f "$f" ]; then
        if ! rustfmt --check --edition 2021 "$f" >/dev/null 2>&1; then
            # rustfmt exit 1 = formatting diff (parseable), exit 2+ = parse error
            RET=$?
            if [ "$RET" -ge 2 ]; then
                echo "GATE FAILED: $f has syntax errors"
                GATE_PASS=false
            fi
        fi
    fi
done

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED: source files parse"

###############################################################################
# Build ty (needed for behavioral tests)
###############################################################################
echo "Building ty..."
if ! cargo build --bin ty 2>/tmp/build_err.txt; then
    echo "BUILD FAILED — cannot run behavioral tests"
    tail -30 /tmp/build_err.txt
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
TY="./target/debug/ty"
echo "Build succeeded."

###############################################################################
# Helper
###############################################################################
add_score() {
    local weight="$1" pass="$2" label="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" -eq 1 ]; then
        REWARD=$(python3 -c "print($REWARD + $weight)")
        echo "PASS ($weight): $label"
    else
        echo "FAIL ($weight): $label"
    fi
}

###############################################################################
# Behavioral: fail-to-pass tests (0.65 total)
###############################################################################

# Create the TypeIs narrowing test file that triggers combinatorial explosion
cat > /tmp/test_typeis_perf.py <<'PYEOF'
"""Test for TypeIs narrowing performance with large Literal unions."""

from typing import Any, Literal, assert_never
from typing_extensions import TypeIs

Kind = Literal[
    "alpha_one", "alpha_two", "alpha_three", "alpha_four",
    "bravo_one", "bravo_two", "bravo_three", "bravo_four",
    "bravo_five", "bravo_six", "bravo_seven", "bravo_eight",
    "charlie_one", "charlie_two", "charlie_three", "charlie_four",
    "charlie_five", "charlie_six", "charlie_seven", "charlie_eight",
    "delta_one", "delta_two", "delta_three", "delta_four",
    "delta_five", "delta_six", "delta_seven", "delta_eight",
    "echo_one", "echo_two", "echo_three", "echo_four",
    "echo_five", "echo_six", "echo_seven", "echo_eight",
    "foxtrot_one", "foxtrot_two", "foxtrot_three", "foxtrot_four",
    "golf_one", "golf_two", "golf_three", "golf_four",
]

ALPHA = Literal["alpha_one", "alpha_two", "alpha_three", "alpha_four",
    "bravo_one", "bravo_two", "bravo_three", "bravo_four",
    "bravo_five", "bravo_six", "bravo_seven", "bravo_eight"]
CHARLIE = Literal["charlie_one", "charlie_two", "charlie_three", "charlie_four",
    "charlie_five", "charlie_six", "charlie_seven"]
DELTA = Literal["delta_one", "delta_two", "delta_three", "delta_four",
    "delta_five", "delta_six"]
ECHO = Literal["echo_one", "echo_two", "echo_three", "echo_four",
    "echo_five", "echo_six"]
FOXTROT = Literal["foxtrot_one", "foxtrot_two"]
GOLF = Literal["golf_one", "golf_two", "golf_three", "golf_four"]

def is_alpha(t: Kind) -> TypeIs[ALPHA]:
    return t.startswith("alpha") or t.startswith("bravo")

def is_charlie(t: Kind) -> TypeIs[CHARLIE]:
    return t.startswith("charlie")

def is_delta(t: Kind) -> TypeIs[DELTA]:
    return t.startswith("delta")

def is_echo(t: Kind) -> TypeIs[ECHO]:
    return t.startswith("echo")

def is_foxtrot(t: Kind) -> TypeIs[FOXTROT]:
    return t.startswith("foxtrot")

def is_golf(t: Kind) -> TypeIs[GOLF]:
    return t.startswith("golf")

Action = Literal[
    "act_one", "act_two", "act_three", "act_four", "act_five",
    "act_six", "act_seven", "act_eight", "act_nine", "act_ten",
    "act_eleven", "act_twelve", "act_thirteen", "act_fourteen",
]

def process(kind: Kind, action: Action | None) -> str:
    if is_golf(kind):
        raise ValueError
    if is_alpha(kind):
        raise ValueError

    if action is None:
        if is_foxtrot(kind):
            return "foxtrot"
        if is_echo(kind):
            return "echo"
        if is_delta(kind):
            return "delta"
        if is_charlie(kind):
            return "charlie"
        return "other"

    match action:
        case "act_one" | "act_two":
            pass
        case "act_three":
            if not is_charlie(kind):
                raise ValueError
        case "act_four" | "act_five":
            if not is_delta(kind):
                raise ValueError
        case "act_six" | "act_seven":
            if not is_echo(kind):
                raise ValueError
        case "act_eight":
            if not is_foxtrot(kind):
                raise ValueError
        case "act_nine":
            pass
        case "act_ten":
            pass
        case "act_eleven":
            pass
        case "act_twelve":
            pass
        case "act_thirteen":
            pass
        case "act_fourteen":
            pass
        case _ as never:
            assert_never(never)

    return kind
PYEOF

# [pr_diff] (0.40): ty check on TypeIs narrowing file must complete within 60s (not hang)
echo "Running ty check on TypeIs narrowing test (timeout 60s)..."
if timeout 60 "$TY" check /tmp/test_typeis_perf.py 2>/tmp/ty_perf_out.txt; then
    add_score 0.40 1 "ty check on TypeIs narrowing completes within 60s"
else
    EXIT_CODE=$?
    if [ "$EXIT_CODE" -eq 124 ]; then
        echo "  TIMEOUT: ty check hung (combinatorial explosion still present)"
    else
        echo "  ty check exited with code $EXIT_CODE"
        cat /tmp/ty_perf_out.txt | tail -10
    fi
    add_score 0.40 0 "ty check on TypeIs narrowing completes within 60s"
fi

# [pr_diff] (0.15): ty check on a simpler narrowing file produces no errors
cat > /tmp/test_noreturn.py <<'PYEOF'
"""Test that NoReturn/Never detection still works correctly."""
import sys
from typing import NoReturn

def exit_fn() -> NoReturn:
    sys.exit(1)

def maybe_exit(flag: bool) -> None:
    if flag:
        exit_fn()
    # After the if, narrowing should know we didn't exit
    x: int = 42
    reveal_type(x)
PYEOF

if timeout 30 "$TY" check /tmp/test_noreturn.py >/tmp/ty_noreturn_out.txt 2>&1; then
    add_score 0.15 1 "ty check on NoReturn narrowing file completes correctly"
else
    EXIT_CODE=$?
    if [ "$EXIT_CODE" -eq 124 ]; then
        echo "  TIMEOUT on simple NoReturn test"
    fi
    add_score 0.15 0 "ty check on NoReturn narrowing file completes correctly"
fi

# [pr_diff] (0.10): ty check on file with many statement-level calls doesn't hang
cat > /tmp/test_many_calls.py <<'PYEOF'
"""Test performance with many statement-level function calls."""

def helper_a() -> str:
    return "a"

def helper_b() -> int:
    return 1

def helper_c() -> float:
    return 1.0

def main() -> None:
    helper_a()
    helper_b()
    helper_c()
    helper_a()
    helper_b()
    helper_c()
    helper_a()
    helper_b()
    helper_c()
    helper_a()
    helper_b()
    helper_c()
    x: int = 42
PYEOF

if timeout 30 "$TY" check /tmp/test_many_calls.py >/dev/null 2>&1; then
    add_score 0.10 1 "ty check on many statement-level calls completes quickly"
else
    add_score 0.10 0 "ty check on many statement-level calls completes quickly"
fi

###############################################################################
# Regression: pass-to-pass (0.15 total)
###############################################################################

# [pr_diff] (0.10): Existing narrowing mdtests still pass
echo "Running narrowing mdtests..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo nextest run -p ty_python_semantic \
    -- "mdtest::narrow" 2>&1 | tail -5 | grep -q "test result: ok\|passed"; then
    add_score 0.10 1 "Upstream narrowing mdtests pass"
else
    # Check if nextest format differs
    if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo nextest run -p ty_python_semantic \
        -- "mdtest::narrow" 2>&1 | grep -q "0 failed"; then
        add_score 0.10 1 "Upstream narrowing mdtests pass"
    else
        add_score 0.10 0 "Upstream narrowing mdtests pass"
    fi
fi

# [pr_diff] (0.05): Reachability-related tests still pass
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo nextest run -p ty_python_semantic \
    -- "reachability" 2>&1 | grep -qE "test result: ok|0 failed"; then
    add_score 0.05 1 "Upstream reachability tests pass"
else
    add_score 0.05 0 "Upstream reachability tests pass"
fi

###############################################################################
# Structural: anti-stub (0.10)
###############################################################################

# [pr_diff] (0.05): reachability_constraints.rs has short-circuit logic for non-Never callables
# The fix must avoid inferring the full call expression when the callable clearly doesn't return Never
RC_FILE="crates/ty_python_semantic/src/semantic_index/reachability_constraints.rs"
if grep -q 'IsNonTerminalCall' "$RC_FILE" && \
   python3 -c "
import re
text = open('$RC_FILE').read()
# The fix should have logic that checks the callable type before the full call expression
# Look for evidence of a multi-step evaluation (not just direct call_expr inference)
has_shortcircuit = bool(re.search(r'infer_expression_type.*callable', text, re.DOTALL))
has_never_check = bool(re.search(r'Never|never', text))
# Must have the IsNonTerminalCall arm with more than just a simple call_expr check
arm_match = re.search(r'IsNonTerminalCall.*?\{(.*?)\n\s*\}', text, re.DOTALL)
if arm_match:
    arm_body = arm_match.group(1)
    # Should be substantially longer than the original 4-line implementation
    has_complex_logic = len(arm_body.strip().splitlines()) > 10
else:
    has_complex_logic = False
print('OK' if (has_shortcircuit and has_never_check and has_complex_logic) else 'FAIL')
" 2>/dev/null | grep -q 'OK'; then
    add_score 0.05 1 "reachability_constraints.rs has enhanced IsNonTerminalCall evaluation"
else
    add_score 0.05 0 "reachability_constraints.rs has enhanced IsNonTerminalCall evaluation"
fi

# [pr_diff] (0.05): predicate.rs IsNonTerminalCall stores more than a single Expression
PRED_FILE="crates/ty_python_semantic/src/semantic_index/predicate.rs"
if python3 -c "
text = open('$PRED_FILE').read()
# The fix should change IsNonTerminalCall to hold a struct with callable + call_expr
# (not just a single Expression)
import re
# Check that IsNonTerminalCall no longer wraps a bare Expression
bare = re.search(r'IsNonTerminalCall\(Expression', text)
# Check that there's a struct defined that includes both callable and call expression info
has_struct = bool(re.search(r'struct\s+\w+.*\{[^}]*callable.*call_expr', text, re.DOTALL))
if bare:
    print('FAIL')  # Still using the old single-Expression form
elif has_struct:
    print('OK')
else:
    print('FAIL')
" 2>/dev/null | grep -q 'OK'; then
    add_score 0.05 1 "IsNonTerminalCall uses enriched predicate data"
else
    add_score 0.05 0 "IsNonTerminalCall uses enriched predicate data"
fi

###############################################################################
# Config-derived checks (0.10)
###############################################################################

# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76
# Check that no local imports were added in the modified files
IMPORT_FAIL=0
for f in "${GATE_FILES[@]}"; do
    if [ -f "$f" ]; then
        if python3 -c "
import re
text = open('$f').read()
# Find functions/impls and check for 'use ' inside them
# Simple heuristic: 'use ' after 'fn ' at deeper indentation
lines = text.splitlines()
in_fn = False
fn_indent = 0
for i, line in enumerate(lines):
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    if re.match(r'(pub\s+)?(async\s+)?fn\s', stripped) or re.match(r'impl\s', stripped):
        in_fn = True
        fn_indent = indent
    elif in_fn and indent <= fn_indent and stripped and not stripped.startswith('//'):
        if stripped.startswith('}'):
            in_fn = False
    if in_fn and indent > fn_indent and stripped.startswith('use '):
        print(f'Local import at line {i+1}: {stripped}')
        exit(1)
" 2>/dev/null; then
            :
        else
            IMPORT_FAIL=1
            break
        fi
    fi
done
if [ "$IMPORT_FAIL" -eq 0 ]; then
    add_score 0.05 1 "No local imports in functions (AGENTS.md:76)"
else
    add_score 0.05 0 "No local imports in functions (AGENTS.md:76)"
fi

# [agent_config] (0.05): "Try hard to avoid panic!, unreachable!, .unwrap()" — AGENTS.md:79
# Check that the changes don't introduce new unwrap/panic/unreachable calls
PANIC_FAIL=0
for f in "${GATE_FILES[@]}"; do
    if [ -f "$f" ]; then
        # Count occurrences in the diff (new lines only)
        DIFF_NEW=$(git diff HEAD -- "$f" 2>/dev/null | grep '^+' | grep -v '^+++' || true)
        if echo "$DIFF_NEW" | grep -qE '\.unwrap\(\)|panic!\(|unreachable!\(' 2>/dev/null; then
            PANIC_FAIL=1
            break
        fi
    fi
done
if [ "$PANIC_FAIL" -eq 0 ]; then
    add_score 0.05 1 "No new panic!/unwrap/unreachable! in changes (AGENTS.md:79)"
else
    add_score 0.05 0 "No new panic!/unwrap/unreachable! in changes (AGENTS.md:79)"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total: $REWARD / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt

# Compute category breakdowns
BEHAV=$(python3 -c "print(min($REWARD, 0.65))")
echo "{\"reward\": $REWARD, \"behavioral\": $BEHAV, \"regression\": 0.0, \"config\": 0.0, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
