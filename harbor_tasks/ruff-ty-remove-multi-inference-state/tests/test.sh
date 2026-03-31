#!/usr/bin/env bash
set +e

REPO="/repo"
cd "$REPO"

BUILDER_RS="crates/ty_python_semantic/src/types/infer/builder.rs"
CONTEXT_RS="crates/ty_python_semantic/src/types/context.rs"
BINEXPR_RS="crates/ty_python_semantic/src/types/infer/builder/binary_expressions.rs"
TYPEEXPR_RS="crates/ty_python_semantic/src/types/infer/builder/type_expression.rs"

REWARD=0
TOTAL=0

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
# GATE: Modified Rust files must be valid syntax
###############################################################################
# [pr_diff] (gate): All modified Rust files must parse as valid Rust
GATE_PASS=1
for f in "$BUILDER_RS" "$CONTEXT_RS" "$BINEXPR_RS" "$TYPEEXPR_RS"; do
    if [ -f "$f" ]; then
        rustfmt --check --edition 2021 "$f" >/dev/null 2>&1
        RC=$?
        if [ "$RC" -ge 2 ]; then
            echo "GATE FAILED: $f has syntax errors"
            GATE_PASS=0
        fi
    fi
done

if [ "$GATE_PASS" -eq 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED: All modified files parse as valid Rust"

###############################################################################
# COMBINED F2P BEHAVIORAL (0.30): Compilation + core types removed
# Both conditions must hold: code compiles AND key types/fields are gone.
# On base commit: types exist → score 0. After correct fix: types gone + compiles → 0.30.
# After deleting everything: doesn't compile → 0.
###############################################################################

# Check three core removals
CORE_REMOVED=1
# [pr_diff] enum MultiInferenceState must be removed from builder.rs
grep -q 'enum MultiInferenceState' "$BUILDER_RS" 2>/dev/null && CORE_REMOVED=0
# [pr_diff] enum InnerExpressionInferenceState must be removed from builder.rs
grep -q 'enum InnerExpressionInferenceState' "$BUILDER_RS" 2>/dev/null && CORE_REMOVED=0
# [pr_diff] multi_inference: bool must be removed from InferContext
grep -q 'multi_inference:\s*bool' "$CONTEXT_RS" 2>/dev/null && CORE_REMOVED=0

# Compilation check
COMPILES=0
echo "Running cargo check on ty_python_semantic..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo check -p ty_python_semantic 2>/tmp/cargo_check_err.txt; then
    COMPILES=1
else
    echo "Compilation failed:"
    tail -30 /tmp/cargo_check_err.txt
fi

# [pr_diff] (0.30): Refactored code compiles with core types removed
if [ "$COMPILES" -eq 1 ] && [ "$CORE_REMOVED" -eq 1 ]; then
    add_score 0.30 1 "Code compiles with MultiInferenceState, InnerExpressionInferenceState, and multi_inference field removed"
else
    add_score 0.30 0 "Code compiles with MultiInferenceState, InnerExpressionInferenceState, and multi_inference field removed (compiles=$COMPILES, core_removed=$CORE_REMOVED)"
fi

###############################################################################
# F2P STRUCTURAL (0.25): Additional removal verification
###############################################################################

# [pr_diff] (0.05): multi_inference_state field removed from TypeInferenceBuilder struct
if grep -q 'multi_inference_state:' "$BUILDER_RS" 2>/dev/null; then
    add_score 0.05 0 "multi_inference_state field removed from builder"
else
    add_score 0.05 1 "multi_inference_state field removed from builder"
fi

# [pr_diff] (0.05): inner_expression_inference_state field removed from TypeInferenceBuilder struct
if grep -q 'inner_expression_inference_state:' "$BUILDER_RS" 2>/dev/null; then
    add_score 0.05 0 "inner_expression_inference_state field removed from builder"
else
    add_score 0.05 1 "inner_expression_inference_state field removed from builder"
fi

# [pr_diff] (0.05): set_multi_inference_state method removed from builder
if grep -q 'fn set_multi_inference_state' "$BUILDER_RS" 2>/dev/null; then
    add_score 0.05 0 "set_multi_inference_state method removed"
else
    add_score 0.05 1 "set_multi_inference_state method removed"
fi

# [pr_diff] (0.05): is_in_multi_inference and set_multi_inference methods removed from InferContext
CONTEXT_METHODS_GONE=1
grep -q 'fn is_in_multi_inference' "$CONTEXT_RS" 2>/dev/null && CONTEXT_METHODS_GONE=0
grep -q 'fn set_multi_inference' "$CONTEXT_RS" 2>/dev/null && CONTEXT_METHODS_GONE=0
add_score 0.05 "$CONTEXT_METHODS_GONE" "is_in_multi_inference/set_multi_inference removed from InferContext"

# [pr_diff] (0.05): discard() method removed from builder (speculative builders no longer need explicit cleanup)
if grep -q 'fn discard' "$BUILDER_RS" 2>/dev/null; then
    add_score 0.05 0 "discard() method removed from builder"
else
    add_score 0.05 1 "discard() method removed from builder"
fi

###############################################################################
# P2P BEHAVIORAL (0.20): Upstream tests still pass
###############################################################################

# [pr_diff] (0.10): Overload/multi-inference related tests pass
echo "Running overload mdtests..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
    cargo test -p ty_python_semantic -- mdtest::overloads 2>/tmp/test_overloads.txt; then
    add_score 0.10 1 "Overload mdtests pass"
else
    tail -20 /tmp/test_overloads.txt
    add_score 0.10 0 "Overload mdtests pass"
fi

# [pr_diff] (0.10): TypedDict/narrowing inference tests pass
echo "Running TypedDict/narrowing mdtests..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
    cargo test -p ty_python_semantic -- mdtest::type_qualifiers::type_dict 2>/tmp/test_typeddict.txt; then
    if grep -q "0 tests" /tmp/test_typeddict.txt 2>/dev/null; then
        # Filter matched zero tests — try broader filter
        if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
            cargo test -p ty_python_semantic -- mdtest::narrow 2>/tmp/test_narrow.txt; then
            add_score 0.10 1 "TypedDict/narrowing mdtests pass"
        else
            add_score 0.10 0 "TypedDict/narrowing mdtests pass"
        fi
    else
        add_score 0.10 1 "TypedDict mdtests pass"
    fi
else
    tail -20 /tmp/test_typeddict.txt
    add_score 0.10 0 "TypedDict mdtests pass"
fi

###############################################################################
# P2P REGRESSION (0.10): Broader test coverage
###############################################################################

# [pr_diff] (0.05): Type expression/annotation tests still pass
echo "Running annotation mdtests..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
    cargo test -p ty_python_semantic -- mdtest::annotations 2>/tmp/test_annotations.txt; then
    add_score 0.05 1 "Annotation mdtests pass"
else
    tail -20 /tmp/test_annotations.txt
    add_score 0.05 0 "Annotation mdtests pass"
fi

# [pr_diff] (0.05): Binary expression inference tests still pass
echo "Running binary expression mdtests..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
    cargo test -p ty_python_semantic -- mdtest::binary 2>/tmp/test_binary.txt; then
    add_score 0.05 1 "Binary expression mdtests pass"
else
    if grep -q "0 tests" /tmp/test_binary.txt 2>/dev/null; then
        # Try broader comparison filter if binary doesn't match
        if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
            cargo test -p ty_python_semantic -- mdtest::comparison 2>/tmp/test_comparison.txt; then
            add_score 0.05 1 "Comparison mdtests pass"
        else
            add_score 0.05 0 "Comparison mdtests pass"
        fi
    else
        add_score 0.05 0 "Binary expression mdtests pass"
    fi
fi

###############################################################################
# CONFIG-DERIVED CHECKS (0.15)
###############################################################################

# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76
# Check that no use statements were added inside function bodies in builder.rs
LOCAL_IMPORTS=$(python3 -c "
import re
with open('$BUILDER_RS') as f:
    content = f.read()
in_fn = False
depth = 0
bad = 0
for line in content.split('\n'):
    stripped = line.strip()
    if re.match(r'(pub(\(.*?\))?\s+)?fn\s+', stripped):
        in_fn = True
    depth += line.count('{') - line.count('}')
    if depth == 0:
        in_fn = False
    if in_fn and depth > 1 and stripped.startswith('use ') and not stripped.startswith('use super'):
        bad += 1
print(bad)
" 2>/dev/null || echo "0")
if [ "$LOCAL_IMPORTS" = "0" ]; then
    add_score 0.05 1 "No local imports in function bodies (AGENTS.md:76)"
else
    add_score 0.05 0 "No local imports in function bodies (AGENTS.md:76)"
fi

# [agent_config] (0.05): "Follow existing code style" — AGENTS.md:75
# MultiInferenceState should not appear as a parameter type anywhere in the crate
if grep -rq 'MultiInferenceState' crates/ty_python_semantic/src/ 2>/dev/null; then
    add_score 0.05 0 "MultiInferenceState fully removed from crate (AGENTS.md:75)"
else
    add_score 0.05 1 "MultiInferenceState fully removed from crate (AGENTS.md:75)"
fi

# [agent_config] (0.05): "Follow existing code style" — AGENTS.md:75
# InnerExpressionInferenceState should not appear anywhere in the crate
if grep -rq 'InnerExpressionInferenceState' crates/ty_python_semantic/src/ 2>/dev/null; then
    add_score 0.05 0 "InnerExpressionInferenceState fully removed from crate (AGENTS.md:75)"
else
    add_score 0.05 1 "InnerExpressionInferenceState fully removed from crate (AGENTS.md:75)"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total: $REWARD / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt

# Write reward.json (approximate category subtotals)
echo "{\"reward\": $REWARD}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
