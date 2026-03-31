#!/usr/bin/env bash
set +e

SCORE=0
REPO=/workspace/ruff

# ── GATE (0.00): Rust compilation check ────────────────────────────
# [pr_diff] (0.00): Code must compile
echo "=== GATE: cargo check ==="
if ! cargo check -p ty_ide --quiet 2>&1; then
    echo "GATE FAILED: code does not compile"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

COMPLETION_RS="$REPO/crates/ty_ide/src/completion.rs"

# Save agent's version of completion.rs so we can restore after injecting tests
cp "$COMPLETION_RS" /tmp/agent_completion.rs

# ── FAIL-TO-PASS 1 (0.35): no panic on completion before opening paren ──
# [pr_diff] (0.35): list[int]<CURSOR>() must not panic — exercises the exact buggy code path
#
# We inject a Rust test into the crate that exercises the panic scenario.
# On buggy code: debug_assert! fires in add_function_arg_completions → panic → test fails.
# On fixed code: completion correctly skips argument completions → test passes.
echo "=== FAIL-TO-PASS 1: completion before paren does not panic ==="

# Append a test to the agent's modified completion.rs
cat >> "$COMPLETION_RS" << 'INJECT_TEST'

// Injected by test harness — exercises the panic path from issue ty#3087
#[cfg(test)]
mod injected_bugfix_tests {
    use super::tests::completion_test_builder;

    #[test]
    fn injected_no_panic_completion_before_paren() {
        let test = completion_test_builder(
            r#"
list[int]<CURSOR>()
"#,
        )
        .skip_keywords()
        .skip_builtins()
        .skip_auto_import()
        .build();

        // We just need this not to panic. The bug causes a debug_assert! failure.
        let _ = test.snapshot();
    }

    #[test]
    fn injected_no_panic_dict_subscript_before_paren() {
        let test = completion_test_builder(
            r#"
dict[str, int]<CURSOR>()
"#,
        )
        .skip_keywords()
        .skip_builtins()
        .skip_auto_import()
        .build();

        let _ = test.snapshot();
    }
}
INJECT_TEST

# Run both injected tests (debug mode — debug_assert! is active)
if cargo nextest run -p ty_ide -- injected_no_panic_completion_before_paren 2>&1 | tee /tmp/f2p1.log | tail -20; then
    if grep -q "1 passed" /tmp/f2p1.log; then
        echo "PASS: no panic on list[int]<CURSOR>()"
        SCORE=$(python3 -c "print($SCORE + 0.35)")
    else
        echo "FAIL: test did not report 1 passed"
    fi
else
    echo "FAIL: injected_no_panic_completion_before_paren panicked or failed"
fi

# ── FAIL-TO-PASS 2 (0.15): variant with dict subscript ──────────
# [pr_diff] (0.15): dict[str, int]<CURSOR>() also must not panic
echo "=== FAIL-TO-PASS 2: dict subscript variant ==="
if cargo nextest run -p ty_ide -- injected_no_panic_dict_subscript_before_paren 2>&1 | tee /tmp/f2p2.log | tail -20; then
    if grep -q "1 passed" /tmp/f2p2.log; then
        echo "PASS: no panic on dict[str, int]<CURSOR>()"
        SCORE=$(python3 -c "print($SCORE + 0.15)")
    else
        echo "FAIL: test did not report 1 passed"
    fi
else
    echo "FAIL: injected dict subscript test panicked or failed"
fi

# Restore agent's version (without injected tests)
cp /tmp/agent_completion.rs "$COMPLETION_RS"

# ── PASS-TO-PASS (0.20): existing completion tests still pass ──────
# [pr_diff] (0.20): Non-argument completion tests should not regress
echo "=== PASS-TO-PASS: upstream completion tests ==="
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo nextest run -p ty_ide -- completion 2>&1 | tee /tmp/p2p.log | tail -20; then
    PASSED=$(grep -oP '\d+ passed' /tmp/p2p.log | head -1 | grep -oP '\d+')
    if [ "${PASSED:-0}" -ge 10 ]; then
        echo "PASS: completion tests pass ($PASSED passed)"
        SCORE=$(python3 -c "print($SCORE + 0.20)")
    else
        echo "FAIL: too few completion tests passed (${PASSED:-0})"
    fi
else
    echo "FAIL: completion tests had failures"
fi

# ── PASS-TO-PASS 2 (0.10): argument completion inside actual args still works ─
# [pr_diff] (0.10): Argument completion tests should still pass when cursor IS inside arguments
echo "=== PASS-TO-PASS 2: argument completion tests ==="
if CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo nextest run -p ty_ide -- argument 2>&1 | tee /tmp/p2p2.log | tail -20; then
    PASSED=$(grep -oP '\d+ passed' /tmp/p2p2.log | head -1 | grep -oP '\d+')
    if [ "${PASSED:-0}" -ge 2 ]; then
        echo "PASS: argument completion tests pass ($PASSED passed)"
        SCORE=$(python3 -c "print($SCORE + 0.10)")
    else
        echo "FAIL: not enough argument tests passed (${PASSED:-0})"
    fi
else
    echo "FAIL: argument completion tests failed"
fi

# ── CONFIG-DERIVED (0.10): no .unwrap() introduced in changed code ─
# [agent_config] (0.10): "Try hard to avoid patterns that require panic!, unreachable!, or .unwrap()" — AGENTS.md:79 @ d8126625
echo "=== CONFIG: no unwrap in diff ==="
DIFF=$(cd "$REPO" && git diff HEAD -- crates/ty_ide/src/completion.rs)
if echo "$DIFF" | grep -q '^+.*\.unwrap()'; then
    echo "FAIL: .unwrap() introduced in changed code"
else
    echo "PASS: no .unwrap() introduced"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi

# ── ANTI-STUB (0.10): completion.rs has non-trivial changes ──────
# [pr_diff] (0.10): Actual code change in completion.rs, not a stub or comment
echo "=== ANTI-STUB: completion.rs has substantive changes ==="
DIFF_ADDED=$(cd "$REPO" && git diff HEAD -- crates/ty_ide/src/completion.rs | grep '^+' | grep -v '^+++' | grep -v '^+\s*//' | grep -v '^+$' | wc -l)
DIFF_REMOVED=$(cd "$REPO" && git diff HEAD -- crates/ty_ide/src/completion.rs | grep '^-' | grep -v '^---' | grep -v '^-\s*//' | grep -v '^-$' | wc -l)
DIFF_TOTAL=$((DIFF_ADDED + DIFF_REMOVED))
if [ "$DIFF_TOTAL" -ge 3 ]; then
    echo "PASS: completion.rs has $DIFF_TOTAL non-comment changed lines"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: completion.rs changes too minimal ($DIFF_TOTAL lines)"
fi

# ── Compute final reward ────────────────────────────────────────────
REWARD=$(python3 -c "print(round($SCORE, 4))")
echo ""
echo "=== FINAL SCORE: $REWARD / 1.0 ==="
echo "$REWARD" > /logs/verifier/reward.txt

# Compute component scores for reward.json
BEHAVIORAL=$(python3 -c "print(round(min($SCORE, 0.50), 4))")
REGRESSION=$(python3 -c "print(round(min(max($SCORE - 0.50, 0), 0.30), 4))")
CONFIG=$(python3 -c "print(round(min(max($SCORE - 0.80, 0), 0.10), 4))")
ANTI_STUB=$(python3 -c "print(round(min(max($SCORE - 0.90, 0), 0.10), 4))")

echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
