#!/usr/bin/env bash
set +e

PASS=0.0
cd /workspace/ruff

# File paths
FORMAT_FILE="crates/ruff_server/src/format.rs"
FORMAT_REQ="crates/ruff_server/src/server/api/requests/format.rs"
EXEC_CMD="crates/ruff_server/src/server/api/requests/execute_command.rs"

##############################################################################
# GATE: Source files exist
##############################################################################
for f in "$FORMAT_FILE" "$FORMAT_REQ" "$EXEC_CMD"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f missing"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done
echo "GATE: source files exist"

##############################################################################
# Inject behavioral F2P test into format.rs test module
##############################################################################
# We inject a Rust test that exercises the core bug: format() on a markdown
# file without preview must return a result distinguishable from "unchanged".
# On buggy code: both return Ok(None)  -> assert_ne fails  (F2P signal)
# On fixed code: different variants     -> assert_ne passes (any valid fix)
python3 << 'INJECT_EOF'
import sys

target = "crates/ruff_server/src/format.rs"
with open(target, "r") as f:
    content = f.read()

injection = r'''
    #[allow(unused_imports)]
    use ruff_python_ast::SourceType;

    #[test]
    fn __eval_behavioral_md_preview() {
        let settings = FormatterSettings::default();

        // Already-formatted Python -> "unchanged" result
        let py_doc = TextDocument::new("x = 1\n".to_string(), 0);
        let py_result = format(
            &py_doc,
            SourceType::Python(PySourceType::Python),
            &settings,
            Path::new("test.py"),
            FormatBackend::Internal,
        )
        .unwrap();

        // Markdown without preview -> must NOT equal "unchanged"
        let md_doc = TextDocument::new("# Hello\n".to_string(), 0);
        let md_result = format(
            &md_doc,
            SourceType::Markdown,
            &settings,
            Path::new("test.md"),
            FormatBackend::Internal,
        )
        .unwrap();

        let py_repr = format!("{:?}", py_result);
        let md_repr = format!("{:?}", md_result);
        assert_ne!(
            py_repr, md_repr,
            "Markdown without preview must be distinguishable from unchanged (both were '{}')",
            py_repr
        );
    }
'''

# Find the last '}' that closes mod tests (last line of file)
lines = content.split('\n')
last_brace = -1
for i in range(len(lines) - 1, -1, -1):
    if lines[i].strip() == '}':
        last_brace = i
        break

if last_brace < 0:
    print("ERROR: cannot find mod tests closing brace", file=sys.stderr)
    sys.exit(1)

lines.insert(last_brace, injection)
with open(target, 'w') as f:
    f.write('\n'.join(lines))

print("Injected behavioral test into format.rs")
INJECT_EOF

if [ $? -ne 0 ]; then
    echo "GATE FAIL: test injection failed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# GATE: cargo check (includes injected test)
##############################################################################
echo "Running cargo check -p ruff_server..."
if ! cargo check -p ruff_server 2>&1; then
    echo "GATE FAIL: cargo check failed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: cargo check passed"

##############################################################################
# F2P (0.60): Behavioral — markdown without preview is distinguishable
##############################################################################
# [pr_diff] (0.60): Core bug — format() must return a result for markdown-
# without-preview that is distinguishable from "file unchanged". This test
# calls format() on both paths and asserts the Debug representations differ.
# On buggy code both are None, so assert_ne fails.
echo "Running F2P behavioral test..."
cargo test -p ruff_server -- __eval_behavioral_md_preview --exact 2>&1 | tail -20
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    PASS=$(python3 -c "print($PASS + 0.60)")
    echo "PASS [0.60]: behavioral F2P — markdown preview distinguishable"
else
    echo "FAIL [0.60]: behavioral F2P — markdown result same as unchanged"
fi

##############################################################################
# P2P (0.10): Existing format::tests still pass
##############################################################################
# [pr_diff] (0.10): Existing upstream tests must not regress
echo "Running existing format::tests (excluding injected)..."
cargo test -p ruff_server -- format::tests --skip __eval_behavioral 2>&1 | tail -20
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    PASS=$(python3 -c "print($PASS + 0.10)")
    echo "PASS [0.10]: existing format::tests pass"
else
    echo "FAIL [0.10]: existing format::tests failed"
fi

##############################################################################
# P2P regression (0.05): Other ruff_server tests
##############################################################################
# [pr_diff] (0.05): Non-format ruff_server tests
echo "Running other ruff_server tests..."
cargo test -p ruff_server -- --skip format::tests 2>&1 | tail -10
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    PASS=$(python3 -c "print($PASS + 0.05)")
    echo "PASS [0.05]: other ruff_server tests pass"
else
    echo "FAIL [0.05]: other ruff_server tests failed"
fi

##############################################################################
# Anti-stub (0.05): format.rs is not truncated
##############################################################################
# [pr_diff] (0.05): format.rs must not be a stub/truncated file
LINE_COUNT=$(wc -l < "$FORMAT_FILE")
if [ "$LINE_COUNT" -gt 300 ]; then
    PASS=$(python3 -c "print($PASS + 0.05)")
    echo "PASS [0.05]: format.rs has $LINE_COUNT lines"
else
    echo "FAIL [0.05]: format.rs only $LINE_COUNT lines (truncated?)"
fi

##############################################################################
# Structural (0.10): Warning shown to user in format request handler
##############################################################################
# [pr_diff] (0.10): The format request handler must send a user-visible
# warning/notification when formatting is skipped due to preview mode.
# Accepts any LSP notification mechanism (show_message, ShowMessage, etc.)
if grep -qE 'show_warning_message|show_message|ShowMessageParams|window/showMessage|MessageType::Warning' "$FORMAT_REQ"; then
    PASS=$(python3 -c "print($PASS + 0.10)")
    echo "PASS [0.10]: warning notification in format handler"
else
    echo "FAIL [0.10]: no user-visible warning in format handler"
fi

##############################################################################
# Config (0.05): No new .unwrap() calls in format.rs
##############################################################################
# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79 @ a84a58fe
BASE_UNWRAPS=$(git show HEAD:"$FORMAT_FILE" 2>/dev/null | grep -c '\.unwrap()' || echo "0")
CURR_UNWRAPS=$(grep -c '\.unwrap()' "$FORMAT_FILE" || echo "0")
# Subtract injected test's .unwrap() calls (2 occurrences)
CURR_UNWRAPS=$((CURR_UNWRAPS - 2))
if [ "$CURR_UNWRAPS" -le "$BASE_UNWRAPS" ]; then
    PASS=$(python3 -c "print($PASS + 0.05)")
    echo "PASS [0.05]: no new .unwrap() in format.rs"
else
    echo "FAIL [0.05]: new .unwrap() in format.rs ($BASE_UNWRAPS -> $CURR_UNWRAPS)"
fi

##############################################################################
# Config (0.05): No inline imports in function bodies
##############################################################################
# [agent_config] (0.05): "Rust imports at top of file" — AGENTS.md:76 @ a84a58fe
INLINE_IMPORTS=$(python3 -c "
import re
with open('$FORMAT_FILE') as f:
    lines = f.readlines()
in_fn = False
depth = 0
violations = 0
skip_eval = False
for i, line in enumerate(lines):
    stripped = line.strip()
    # Skip our injected eval function entirely
    if '__eval_behavioral' in stripped and 'fn ' in stripped:
        skip_eval = True
        depth = 0
    if skip_eval:
        depth += stripped.count('{') - stripped.count('}')
        if depth <= 0 and i > 0 and '{' not in stripped:
            skip_eval = False
            depth = 0
        continue
    if re.match(r'(pub\s+)?(fn|async fn) ', stripped):
        in_fn = True
        depth = 0
    if in_fn:
        depth += stripped.count('{') - stripped.count('}')
        if depth <= 0 and in_fn and i > 0:
            in_fn = False
        if in_fn and depth > 0 and stripped.startswith('use '):
            violations += 1
print(violations)
" 2>/dev/null || echo "0")
if [ "$INLINE_IMPORTS" = "0" ]; then
    PASS=$(python3 -c "print($PASS + 0.05)")
    echo "PASS [0.05]: no inline imports in function bodies"
else
    echo "FAIL [0.05]: $INLINE_IMPORTS inline imports in function bodies"
fi

##############################################################################
# Final score
##############################################################################
SCORE=$(python3 -c "print(round(min(1.0, $PASS), 4))")
echo ""
echo "=== TOTAL: $SCORE ==="
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
t = $PASS
behavioral = min(0.60, t)
r = max(0, t - 0.60)
regression = min(0.20, r)
r = max(0, r - 0.20)
config = min(0.10, r)
r = max(0, r - 0.10)
print(json.dumps({
    'reward': round(min(1.0, $PASS), 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
