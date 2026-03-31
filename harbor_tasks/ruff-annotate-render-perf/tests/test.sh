#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0
DL_FILE="crates/ruff_annotate_snippets/src/renderer/display_list.rs"
SB_FILE="crates/ruff_annotate_snippets/src/renderer/styled_buffer.rs"

cd /workspace/ruff 2>/dev/null || cd /repo

echo "=== Annotate-Snippets Render Performance Fix ==="

# ── GATE: Files exist and crate compiles ──────────────────────────────
# [pr_diff] (gate): Modified files must exist
if [ ! -f "$DL_FILE" ] || [ ! -f "$SB_FILE" ]; then
    echo "GATE FAIL: target files not found"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# [pr_diff] (gate): Crate must compile
echo "Checking compilation..."
if ! cargo check -p ruff_annotate_snippets 2>&1; then
    echo "GATE FAIL: cargo check failed"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS: compiles"

set +e

# ── Fail-to-pass: Behavioral tests via injected Rust tests ───────────

# Inject tests for normalize_whitespace Cow optimization into display_list.rs
# These tests FAIL on pre-fix code (returns String, not Cow) and PASS on fix.
cat >> "$DL_FILE" << 'TESTCODE'

#[cfg(test)]
mod _harbor_cow_optimization_tests {
    use super::*;
    use std::borrow::Cow;

    #[test]
    fn plain_ascii_avoids_allocation() {
        let input = "hello world 123 normal line of code";
        let result = normalize_whitespace(input);
        assert!(
            matches!(result, Cow::Borrowed(_)),
            "plain ASCII input should avoid allocation (return Cow::Borrowed)"
        );
        assert_eq!(&*result, input);
    }

    #[test]
    fn tab_replacement_produces_correct_output() {
        let result = normalize_whitespace("before\tafter");
        assert!(
            matches!(result, Cow::Owned(_)),
            "string with tab should allocate (return Cow::Owned)"
        );
        assert!(!result.contains('\t'), "tab character should be replaced");
        assert!(result.contains("before"), "content before tab preserved");
        assert!(result.contains("after"), "content after tab preserved");
    }

    #[test]
    fn complex_clean_string_avoids_allocation() {
        let input = "def foo(x: int, y: str = 'hello') -> None:  # comment with $pecial chars!";
        let result = normalize_whitespace(input);
        assert!(
            matches!(result, Cow::Borrowed(_)),
            "string without replacement chars should avoid allocation"
        );
        assert_eq!(&*result, input);
    }

    #[test]
    fn empty_string_avoids_allocation() {
        let result = normalize_whitespace("");
        assert!(
            matches!(result, Cow::Borrowed(_)),
            "empty string should avoid allocation"
        );
        assert_eq!(&*result, "");
    }

    #[test]
    fn unicode_control_chars_replaced() {
        // \u{202a} is LEFT-TO-RIGHT EMBEDDING, should be stripped
        let input = "hello\u{202a}world";
        let result = normalize_whitespace(input);
        assert!(
            matches!(result, Cow::Owned(_)),
            "string with Unicode control char should allocate"
        );
        assert!(!result.contains('\u{202a}'), "control char should be removed");
        assert!(result.contains("hello"), "surrounding text preserved");
        assert!(result.contains("world"), "surrounding text preserved");
    }
}
TESTCODE

echo "Running Cow optimization tests..."

# [pr_diff] (0.25): normalize_whitespace avoids allocation for plain text
if cargo test -p ruff_annotate_snippets -- _harbor_cow_optimization_tests::plain_ascii_avoids_allocation --exact 2>&1 | tail -5 | grep -q "ok"; then
    echo "PASS (0.25): plain ASCII avoids allocation"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    echo "FAIL (0.25): plain ASCII should avoid allocation"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.25)")

# [pr_diff] (0.20): normalize_whitespace correctly handles tabs with Cow::Owned
if cargo test -p ruff_annotate_snippets -- _harbor_cow_optimization_tests::tab_replacement_produces_correct_output --exact 2>&1 | tail -5 | grep -q "ok"; then
    echo "PASS (0.20): tab replacement correct with Cow"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    echo "FAIL (0.20): tab replacement should work with Cow return"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.20)")

# [pr_diff] (0.15): normalize_whitespace avoids allocation for complex clean strings
if cargo test -p ruff_annotate_snippets -- _harbor_cow_optimization_tests::complex_clean_string_avoids_allocation --exact 2>&1 | tail -5 | grep -q "ok"; then
    echo "PASS (0.15): complex clean string avoids allocation"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL (0.15): complex clean string should avoid allocation"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.15)")

# [pr_diff] (0.05): normalize_whitespace avoids allocation for empty string
if cargo test -p ruff_annotate_snippets -- _harbor_cow_optimization_tests::empty_string_avoids_allocation --exact 2>&1 | tail -5 | grep -q "ok"; then
    echo "PASS (0.05): empty string avoids allocation"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL (0.05): empty string should avoid allocation"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

# [pr_diff] (0.10): normalize_whitespace handles Unicode control characters
if cargo test -p ruff_annotate_snippets -- _harbor_cow_optimization_tests::unicode_control_chars_replaced --exact 2>&1 | tail -5 | grep -q "ok"; then
    echo "PASS (0.10): Unicode control chars correctly replaced"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL (0.10): Unicode control chars should be replaced"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# Revert injected tests so they don't interfere with pass-to-pass
git checkout -- "$DL_FILE"

# ── Pass-to-pass: existing tests still pass ───────────────────────────

# [pr_diff] (0.10): Existing crate tests pass (regression check)
echo "Running existing crate tests..."
if cargo test -p ruff_annotate_snippets 2>&1 | tail -5 | grep -q "ok"; then
    echo "PASS (0.10): existing crate tests pass"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL (0.10): existing crate tests regressed"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# ── Config-derived checks ─────────────────────────────────────────────

# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76 @ e7f1c536
# Check no use/extern crate statements inside function bodies in changed files
if ! python3 -c "
import re
for path in ['$DL_FILE', '$SB_FILE']:
    content = open(path).read()
    in_fn = False
    brace_depth = 0
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r'(pub(\(crate\))?\s+)?fn\s+\w+', stripped):
            in_fn = True
            brace_depth = 0
        if in_fn:
            brace_depth += stripped.count('{') - stripped.count('}')
            if brace_depth > 0 and re.match(r'use\s+', stripped):
                exit(1)
            if brace_depth <= 0 and '{' in line:
                in_fn = brace_depth > 0
exit(0)
"; then
    echo "FAIL (0.05): local imports found inside functions (AGENTS.md:76)"
else
    echo "PASS (0.05): no local imports in functions"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

# [agent_config] (0.05): "Try hard to avoid patterns that require panic!, unreachable!, or .unwrap()" — AGENTS.md:79 @ e7f1c536
# Only check if agent INTRODUCED new unwrap/panic/unreachable (delta check via git diff)
NEW_UNWRAPS=$(git diff HEAD -- "$DL_FILE" "$SB_FILE" 2>/dev/null | grep -cE '^\+.*\b(unwrap\(\)|panic!\(|unreachable!\()' || true)
if [ "$NEW_UNWRAPS" -eq 0 ] 2>/dev/null; then
    echo "PASS (0.05): no new unwrap/panic/unreachable introduced"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL (0.05): $NEW_UNWRAPS new unwrap/panic/unreachable found (AGENTS.md:79)"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

# ── Summary ───────────────────────────────────────────────────────────

echo ""
echo "Total: $SCORE / $TOTAL"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
score = float('$SCORE')
data = {'reward': score}
print(json.dumps(data))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
