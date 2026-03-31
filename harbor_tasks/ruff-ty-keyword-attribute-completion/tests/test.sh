#!/usr/bin/env bash
set +e

SCORE=0
REPO=/workspace/ruff

# ── GATE (0.00): Rust compilation check ────────────────────────────
# [pr_diff] (0.00): Code must compile
echo "=== GATE: cargo check ==="
cd "$REPO"
if ! cargo check -p ty_ide --quiet 2>&1; then
    echo "GATE FAILED: code does not compile"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

# ── BEHAVIORAL 1 (0.40): keyword-prefix completion returns results ─
# [pr_diff] (0.40): {1}.is<CURSOR> must produce completions like isdisjoint
# Injects a Rust test into the completion test module that exercises the
# exact buggy code path: a keyword token ("is") after a dot.
echo "=== BEHAVIORAL 1: keyword-prefix attribute completion ==="

# Write test functions to include directly inside mod tests (no nested module).
# Using contains()/not_contains() API which is the idiomatic test pattern.
cat > /tmp/harbor_kw_test.rs << 'RUSTEOF'
// Behavioral tests: keyword-prefixed attribute completion
// At the buggy baseline, {1}.is<CURSOR> returns zero completions because
// "is" is lexed as TokenKind::Is (a keyword), not TokenKind::Name.

#[test]
fn harbor_keyword_prefix_is_completes() {
    // "is" is a Python keyword — the lexer tokenizes it as TokenKind::Is.
    // A correct fix must recognize keyword tokens after dot as valid
    // completion prefixes.
    let test = completion_test_builder(
        "\
{1}.is<CURSOR>
",
    )
    .skip_builtins()
    .skip_keywords()
    .build();

    // set.isdisjoint must appear — it starts with "is" and is a set method
    test.contains("isdisjoint");
}

#[test]
fn harbor_keyword_prefix_in_completes() {
    // "in" is also a Python keyword — tests a second keyword token.
    let test = completion_test_builder(
        "\
[1, 2, 3].in<CURSOR>
",
    )
    .skip_builtins()
    .skip_keywords()
    .build();

    // list.index starts with "in" — must appear in completions
    test.contains("index");
}
RUSTEOF

# Save agent's version of completion.rs, then inject our test
COMP_RS="$REPO/crates/ty_ide/src/completion.rs"
cp "$COMP_RS" /tmp/agent_completion.rs.bak
cp /tmp/harbor_kw_test.rs "$REPO/crates/ty_ide/src/harbor_kw_test.rs"

# Insert include! just before the final closing brace of the file
# (which closes the #[cfg(test)] mod tests block)
python3 << 'PYEOF'
path = "/workspace/ruff/crates/ty_ide/src/completion.rs"
with open(path, "r") as f:
    content = f.read()

insertion = '\n    include!("harbor_kw_test.rs");\n'
last_brace = content.rfind("}")
if last_brace == -1:
    print("ERROR: could not find closing brace")
    exit(1)

new_content = content[:last_brace] + insertion + content[last_brace:]
with open(path, "w") as f:
    f.write(new_content)

print("Injected harbor_kw_test.rs include into completion.rs test module")
PYEOF

B1_SCORE=0
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo nextest run -p ty_ide -- harbor_keyword_prefix 2>&1 | tee /tmp/b1.log | tail -30; then
    PASSED=$(grep -oP '\d+ passed' /tmp/b1.log | head -1 | grep -oP '\d+' || echo 0)
    if [ "${PASSED:-0}" -ge 2 ]; then
        echo "PASS: both keyword-prefix completion tests passed"
        B1_SCORE=40
    elif [ "${PASSED:-0}" -ge 1 ]; then
        echo "PARTIAL: 1 of 2 keyword-prefix tests passed"
        B1_SCORE=25
    else
        echo "FAIL: keyword-prefix completion tests did not pass"
    fi
else
    echo "FAIL: keyword-prefix completion tests failed or errored"
fi
SCORE=$((SCORE + B1_SCORE))

# Restore agent's version of completion.rs (remove our injection)
cp /tmp/agent_completion.rs.bak "$COMP_RS"
rm -f "$REPO/crates/ty_ide/src/harbor_kw_test.rs"

# ── BEHAVIORAL 2 (0.20): PR-specific completion test if agent added one ─
# [pr_diff] (0.20): Agent may add their own test for keyword-prefix completion
# Run any test matching "keyword" in ty_ide — the agent might name it differently
echo "=== BEHAVIORAL 2: agent-added keyword completion test ==="
B2_SCORE=0
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo nextest run -p ty_ide -- keyword 2>&1 | tee /tmp/b2.log | tail -20; then
    PASSED=$(grep -oP '\d+ passed' /tmp/b2.log | head -1 | grep -oP '\d+' || echo 0)
    if [ "${PASSED:-0}" -ge 1 ]; then
        echo "PASS: agent keyword test(s) passed ($PASSED)"
        B2_SCORE=20
    else
        echo "SKIP: no agent-added keyword tests found"
    fi
else
    # If tests exist but fail, that's a fail; if no tests match, cargo nextest
    # exits non-zero with "no tests matched" which is fine (score stays 0)
    echo "SKIP: no keyword tests or tests failed"
fi
SCORE=$((SCORE + B2_SCORE))

# ── PASS-TO-PASS (0.15): existing completion tests still pass ──────
# [pr_diff] (0.15): Non-attribute completion tests should not regress
echo "=== PASS-TO-PASS: existing completion tests ==="
P2P_SCORE=0
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo nextest run -p ty_ide -- completion 2>&1 | tee /tmp/p2p.log | tail -20; then
    PASSED=$(grep -oP '\d+ passed' /tmp/p2p.log | head -1 | grep -oP '\d+' || echo 0)
    if [ "${PASSED:-0}" -ge 10 ]; then
        echo "PASS: completion tests pass ($PASSED)"
        P2P_SCORE=15
    else
        echo "FAIL: too few completion tests passed ($PASSED)"
    fi
else
    echo "FAIL: completion tests had failures"
fi
SCORE=$((SCORE + P2P_SCORE))

# ── CONFIG-DERIVED (0.10): no .unwrap() introduced in changed code ─
# [agent_config] (0.10): "Try hard to avoid patterns that require panic!, unreachable!, or .unwrap()" — AGENTS.md:79 @ 4aabc71f
echo "=== CONFIG: no unwrap in diff ==="
CONFIG_SCORE=0
DIFF=$(cd "$REPO" && git diff HEAD -- crates/ty_ide/src/completion.rs)
if echo "$DIFF" | grep -q '^+.*\.unwrap()'; then
    echo "FAIL: .unwrap() introduced in changed code"
else
    echo "PASS: no .unwrap() introduced"
    CONFIG_SCORE=10
fi
SCORE=$((SCORE + CONFIG_SCORE))

# ── ANTI-GAMING (0.15): existing attribute_access tests still pass ─
# [pr_diff] (0.15): Fix must not break existing attribute completion behavior
echo "=== ANTI-GAMING: existing attribute_access tests ==="
AG_SCORE=0
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo nextest run -p ty_ide -- "attribute_access_set$|attribute_access_empty" 2>&1 | tee /tmp/ag.log | tail -20; then
    PASSED=$(grep -oP '\d+ passed' /tmp/ag.log | head -1 | grep -oP '\d+' || echo 0)
    if [ "${PASSED:-0}" -ge 2 ]; then
        echo "PASS: existing attribute tests still pass ($PASSED)"
        AG_SCORE=15
    else
        echo "FAIL: existing attribute tests regressed"
    fi
else
    echo "FAIL: existing attribute tests failed"
fi
SCORE=$((SCORE + AG_SCORE))

# ── Compute final reward ────────────────────────────────────────────
REWARD=$(python3 -c "print(round($SCORE / 100.0, 4))")
echo ""
echo "=== FINAL SCORE: $REWARD / 1.0 ==="
echo "$REWARD" > /logs/verifier/reward.txt

# Component scores
BEHAVIORAL=$(python3 -c "print(round(($B1_SCORE + $B2_SCORE) / 100.0, 4))")
REGRESSION=$(python3 -c "print(round(($P2P_SCORE + $AG_SCORE) / 100.0, 4))")
CONFIG_F=$(python3 -c "print(round($CONFIG_SCORE / 100.0, 4))")

echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG_F, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
