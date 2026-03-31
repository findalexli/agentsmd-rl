#!/usr/bin/env bash
set +e

REPO="/repo"
REWARD=0
TOTAL=0

cd "$REPO"

GENERICS_RS="crates/ty_python_semantic/src/types/generics.rs"
BIND_RS="crates/ty_python_semantic/src/types/call/bind.rs"
CONSTRAINTS_RS="crates/ty_python_semantic/src/types/constraints.rs"
RELATION_RS="crates/ty_python_semantic/src/types/relation.rs"
SIGNATURES_RS="crates/ty_python_semantic/src/types/signatures.rs"
TYPES_RS="crates/ty_python_semantic/src/types.rs"

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

bail() {
    echo "$REWARD" > /logs/verifier/reward.txt
    echo "{\"reward\": $REWARD, \"behavioral\": 0.0, \"regression\": 0.0, \"config\": 0.0, \"style_rubric\": 0.0}" > /logs/verifier/reward.json
    exit 0
}

###############################################################################
# GATE 1: Modified Rust files must be valid syntax
###############################################################################
# [pr_diff] (gate): All modified Rust files must parse
GATE_PASS=1
for f in "$GENERICS_RS" "$BIND_RS" "$CONSTRAINTS_RS" "$RELATION_RS" "$SIGNATURES_RS" "$TYPES_RS"; do
    if [ -f "$f" ]; then
        if ! rustfmt --check --edition 2021 "$f" >/dev/null 2>&1; then
            RETCODE=$?
            if [ "$RETCODE" -ge 2 ]; then
                echo "GATE 1 FAILED: $f has syntax errors"
                GATE_PASS=0
            fi
        fi
    fi
done

if [ "$GATE_PASS" -eq 0 ]; then
    REWARD=0.0
    bail
fi
echo "GATE 1 PASSED: All modified files parse as valid Rust"

###############################################################################
# GATE 2: InferableTypeVars uses single lifetime and implements Hash + Eq
#
# This is the CORE fail-to-pass test for this refactoring task.
# On the base commit, InferableTypeVars<'a, 'db> has two lifetimes and does
# not implement Hash or Eq (it contains references). Any correct refactoring
# that achieves salsa compatibility MUST pass this compile test.
#
# We temporarily append a small test module, try to compile, then restore.
###############################################################################
# [pr_diff] (gate): InferableTypeVars<'db> must compile with Hash + Eq bounds
if [ ! -f "$GENERICS_RS" ]; then
    echo "GATE 2 FAILED: $GENERICS_RS not found"
    REWARD=0.0
    bail
fi

cp "$GENERICS_RS" /tmp/generics_backup.rs

cat >> "$GENERICS_RS" << 'GATE_TEST_EOF'

#[allow(dead_code, unused_imports)]
mod _harbor_refactor_gate {
    use super::InferableTypeVars;

    // Requirement 1: single lifetime parameter ('db only, no 'a)
    fn _single_lifetime<'db>(itv: InferableTypeVars<'db>) -> InferableTypeVars<'db> { itv }

    // Requirement 2: salsa-compatible traits
    fn _assert_hash<'db>() where InferableTypeVars<'db>: std::hash::Hash {}
    fn _assert_eq<'db>() where InferableTypeVars<'db>: Eq {}
}
GATE_TEST_EOF

echo "Running compile gate: InferableTypeVars<'db> + Hash + Eq..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo check -p ty_python_semantic 2>/tmp/gate2_err.txt; then
    echo "GATE 2 PASSED: InferableTypeVars<'db> is Hash + Eq"
    GATE2_PASS=1
else
    echo "GATE 2 FAILED: InferableTypeVars must take single lifetime 'db and implement Hash + Eq"
    tail -20 /tmp/gate2_err.txt
    GATE2_PASS=0
fi

# Restore original file before any further checks
cp /tmp/generics_backup.rs "$GENERICS_RS"

if [ "$GATE2_PASS" -eq 0 ]; then
    REWARD=0.0
    bail
fi

###############################################################################
# Behavioral: Compilation check (0.20)
###############################################################################
# [pr_diff] (0.20): Full crate must compile after refactoring
echo "Running cargo check on ty_python_semantic..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo check -p ty_python_semantic 2>/tmp/cargo_check_err.txt; then
    add_score 0.20 1 "cargo check -p ty_python_semantic passes"
else
    echo "Compilation failed:"
    tail -30 /tmp/cargo_check_err.txt
    add_score 0.20 0 "cargo check -p ty_python_semantic passes"
fi

###############################################################################
# Behavioral: Key upstream tests (0.35)
###############################################################################
# [pr_diff] (0.20): Generic specialization tests pass
echo "Running generics mdtests..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
    cargo test -p ty_python_semantic -- mdtest::generics 2>/tmp/test_generics.txt; then
    add_score 0.20 1 "Generics mdtests pass"
else
    tail -20 /tmp/test_generics.txt
    add_score 0.20 0 "Generics mdtests pass"
fi

# [pr_diff] (0.15): Overload resolution tests (exercises InferableTypeVars merge paths)
echo "Running overload mdtests..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
    cargo test -p ty_python_semantic -- mdtest::overloads 2>/tmp/test_overloads.txt; then
    add_score 0.15 1 "Overload mdtests pass"
else
    tail -20 /tmp/test_overloads.txt
    add_score 0.15 0 "Overload mdtests pass"
fi

###############################################################################
# Regression: Pass-to-pass upstream tests (0.15)
###############################################################################
# [pr_diff] (0.10): Type narrowing tests still pass (exercises constraint solving)
echo "Running narrowing mdtests..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
    cargo test -p ty_python_semantic -- mdtest::narrow 2>/tmp/test_narrow.txt; then
    add_score 0.10 1 "Narrowing mdtests pass"
else
    tail -20 /tmp/test_narrow.txt
    add_score 0.10 0 "Narrowing mdtests pass"
fi

# [pr_diff] (0.05): Callable subtyping tests still pass
echo "Running callable subtyping mdtests..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
    cargo test -p ty_python_semantic -- mdtest::callable 2>/tmp/test_callable.txt; then
    add_score 0.05 1 "Callable mdtests pass"
else
    if grep -q "0 tests" /tmp/test_callable.txt 2>/dev/null; then
        add_score 0.05 1 "No direct callable mdtests (OK)"
    else
        add_score 0.05 0 "Callable mdtests pass"
    fi
fi

###############################################################################
# Structural: Refactoring verification (0.20)
###############################################################################
# [pr_diff] (0.10): Two variant (lazy reference merge) must be removed
# WHY grep not call: Checking enum variant existence in Rust source
if grep -q 'Two(' "$GENERICS_RS" 2>/dev/null; then
    add_score 0.10 0 "Two variant removed from InferableTypeVars"
else
    add_score 0.10 1 "Two variant removed from InferableTypeVars"
fi

# [pr_diff] (0.10): salsa interning must be used for inner set storage
# WHY grep not call: Checking for Rust attribute macro in source
# Non-narrow: accepts any #[salsa::interned] struct in the file regardless of name
if grep -q '#\[salsa::interned\]' "$GENERICS_RS" 2>/dev/null; then
    add_score 0.10 1 "salsa::interned used in generics.rs"
else
    add_score 0.10 0 "salsa::interned not found in generics.rs"
fi

###############################################################################
# Config-derived checks (0.10)
###############################################################################
# [agent_config] (0.05): "Rust imports at top of file" — AGENTS.md:76 @ 3a44cce
LOCAL_IMPORTS=$(python3 -c "
import re
with open('$GENERICS_RS') as f:
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
    add_score 0.05 1 "No local imports in functions (AGENTS.md:76)"
else
    add_score 0.05 0 "No local imports in functions (AGENTS.md:76)"
fi

# [agent_config] (0.05): "Follow existing code style" — AGENTS.md:75 @ 3a44cce
# All references to InferableTypeVars across affected files should use single lifetime
DUAL_LIFETIME_REFS=0
for f in "$RELATION_RS" "$BIND_RS" "$CONSTRAINTS_RS" "$SIGNATURES_RS" "$TYPES_RS"; do
    if grep -qP "InferableTypeVars<'[a-z]+,\s*'db>" "$f" 2>/dev/null; then
        DUAL_LIFETIME_REFS=1
        break
    fi
done
if [ "$DUAL_LIFETIME_REFS" -eq 0 ]; then
    add_score 0.05 1 "Consistent single-lifetime signatures (AGENTS.md:75)"
else
    add_score 0.05 0 "Consistent single-lifetime signatures (AGENTS.md:75)"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total: $REWARD / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt

# Category breakdown (approximate, for diagnostics)
python3 -c "
import json
r = $REWARD
behavioral = min(r, 0.55)
regression = max(0, min(r - 0.55, 0.15))
structural = max(0, min(r - 0.70, 0.20))
config = max(0, min(r - 0.90, 0.10))
print(json.dumps({'reward': r, 'behavioral': behavioral, 'regression': regression, 'config': config, 'style_rubric': 0.0}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
