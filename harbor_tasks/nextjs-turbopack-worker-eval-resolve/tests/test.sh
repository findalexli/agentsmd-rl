#!/usr/bin/env bash
# Verifier for nextjs-turbopack-worker-eval-resolve
#
# Bug: Turbopack's NodeWorkerConstructor handler doesn't check for { eval: true }
# in the second argument, causing it to treat inline JS code as a file path.
# The fix adds eval-option detection and also separates DataUri/Uri from Dynamic
# in parse.rs's append_path.
#
# ALL checks are structural because turbopack requires ~200+ crates + nightly Rust
# to compile. To resist gaming, every check strips comments before inspection.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

REFS="/workspace/next.js/turbopack/crates/turbopack-ecmascript/src/references/mod.rs"
PARSE="/workspace/next.js/turbopack/crates/turbopack-core/src/resolve/parse.rs"

###############################################################################
# GATE: Source files exist
###############################################################################
if [ ! -f "$REFS" ] || [ ! -f "$PARSE" ]; then
    echo "GATE FAILED: Required source files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Helper: strip Rust comments from source code so checks can't be gamed by
# injecting keywords inside // or /* */ comments.
###############################################################################
cat > /tmp/strip_rust_comments.py << 'STRIP_EOF'
import re, sys

def strip_rust_comments(src):
    """Remove // line comments and /* */ block comments, preserving string literals."""
    result = []
    i = 0
    in_string = False
    string_char = None
    while i < len(src):
        # Handle string literals (don't strip inside them)
        if not in_string and src[i] == '"' and (i == 0 or src[i-1] != '\\'):
            # Check for raw string r#"..."#
            in_string = True
            string_char = '"'
            result.append(src[i])
            i += 1
            continue
        if in_string and src[i] == string_char and (i == 0 or src[i-1] != '\\'):
            in_string = False
            result.append(src[i])
            i += 1
            continue
        if in_string:
            result.append(src[i])
            i += 1
            continue
        # Line comment
        if src[i:i+2] == '//':
            while i < len(src) and src[i] != '\n':
                i += 1
            continue
        # Block comment
        if src[i:i+2] == '/*':
            i += 2
            while i < len(src) - 1 and src[i:i+2] != '*/':
                i += 1
            i += 2
            continue
        result.append(src[i])
        i += 1
    return ''.join(result)

if __name__ == '__main__':
    src = open(sys.argv[1]).read()
    print(strip_rust_comments(src))
STRIP_EOF

###############################################################################
# Weight allocation:
#   TEST 1 [pr_diff]    (0.30): eval option detected + early exit in handler
#   TEST 2 [pr_diff]    (0.20): DataUri/Uri separated from Dynamic (fail-to-pass)
#   TEST 3 [pr_diff]    (0.15): Regression — Worker path resolution preserved
#   TEST 4 [pr_diff]    (0.10): Warning/diagnostic for dynamic eval
#   TEST 5 [pr_diff]    (0.10): Worker-specific error code (not FS_METHOD)
#   TEST 6 [structural] (0.10): Anti-stub — substantial new code in handler
#   TEST 7 [pr_diff]    (0.05): parse.rs DataUri/Uri individually yield Dynamic
#   TOTAL               = 1.00
###############################################################################

SCORE="0.0"

###############################################################################
# TEST 1 [pr_diff] (0.30): The NodeWorkerConstructor handler now detects the
# eval option in the second argument and has an early-exit code path that
# skips worker reference creation.
#
# Accepts any implementation that:
#   - Inspects the second argument (args.get(1), args[1], destructuring, etc.)
#   - Checks for "eval" key
#   - Has an early return/skip path before path resolution
# Rejects: keyword injection via comments (stripped before inspection)
###############################################################################
echo ""
echo "TEST 1: [pr_diff] eval option detection + early exit in NodeWorkerConstructor"
python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_rust_comments import strip_rust_comments

with open("/workspace/next.js/turbopack/crates/turbopack-ecmascript/src/references/mod.rs") as f:
    raw_src = f.read()

src = strip_rust_comments(raw_src)

# Find the NodeWorkerConstructor match arm (comment-stripped)
idx = src.find('NodeWorkerConstructor')
if idx < 0:
    print("FAIL: NodeWorkerConstructor not found")
    sys.exit(1)

# Get a large chunk of the handler
chunk = src[idx:idx+5000]

# 1a: Must inspect second argument — accept multiple patterns
has_second_arg = any(p in chunk for p in [
    'args.get(1)', 'args[1]', 'second_arg', 'options_arg',
    'get(1)', '[1]',
])
# Also accept if they destructure or pattern-match on the args list
if not has_second_arg:
    has_second_arg = bool(re.search(r'args\s*\.\s*get\s*\(\s*1\s*\)', chunk))
if not has_second_arg:
    # Accept: let [_, opts, ..] = or similar destructuring
    has_second_arg = bool(re.search(r'\[_\s*,\s*\w+', chunk))

if not has_second_arg:
    print("FAIL: Handler does not inspect the second Worker constructor argument")
    sys.exit(1)

# 1b: Must reference "eval" in actual code (not comments — already stripped)
eval_refs = [m.start() for m in re.finditer(r'"eval"', chunk)]
if not eval_refs:
    print("FAIL: No reference to \"eval\" key in handler code")
    sys.exit(1)

# 1c: Must have an early-exit path — accept return, continue, break, or skip flag
has_exit = bool(re.search(
    r'return\s+Ok\s*\(|'           # return Ok(...)
    r'return\s+;|'                  # bare return
    r'continue\s*;|'               # continue
    r'skip\w*\s*=\s*true|'         # skip flag
    r'break\s*;',                   # break
    chunk
))
if not has_exit:
    print("FAIL: No early-exit path when eval is true")
    sys.exit(1)

# 1d: The exit path must come before the path resolution call (js_value_to_pattern)
# Find first exit after eval check, and the path resolution call
eval_pos = eval_refs[0]
after_eval = chunk[eval_pos:]

exit_match = re.search(
    r'return\s+Ok\s*\(|return\s*;|continue\s*;|skip\w*\s*=\s*true|break\s*;',
    after_eval
)
pattern_match = re.search(r'js_value_to_pattern', after_eval)

if exit_match and pattern_match:
    if exit_match.start() > pattern_match.start():
        print("FAIL: Exit path comes after path resolution — eval:true still resolves as path")
        sys.exit(1)
elif not exit_match:
    print("FAIL: No exit path found after eval check")
    sys.exit(1)

print("PASS: Handler detects eval option and exits early before path resolution")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.30:.4f}')")
    echo "  +0.30 (total: $SCORE)"
else
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# TEST 2 [pr_diff] (0.20): In parse.rs, the buggy code groups
#   Request::DataUri { .. } | Request::Uri { .. } | Request::Dynamic
# in one match arm. A correct fix separates DataUri/Uri from Dynamic.
# This is the closest to a fail-to-pass test: the buggy code FAILS this check.
###############################################################################
echo ""
echo "TEST 2: [pr_diff] DataUri/Uri no longer grouped with Dynamic in parse.rs"
python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_rust_comments import strip_rust_comments

with open("/workspace/next.js/turbopack/crates/turbopack-core/src/resolve/parse.rs") as f:
    raw_src = f.read()

src = strip_rust_comments(raw_src)

# The BUGGY pattern: DataUri/Uri/Dynamic all in one match arm
# Accept variations in spacing and field patterns
buggy = bool(re.search(
    r'DataUri\s*\{[^}]*\}\s*\|\s*Request::Uri\s*\{[^}]*\}\s*\|\s*Request::Dynamic',
    src
))
if buggy:
    print("FAIL: DataUri/Uri still grouped with Dynamic (buggy pattern present)")
    sys.exit(1)

# Also check the reverse ordering
buggy2 = bool(re.search(
    r'Dynamic\s*\|\s*Request::(DataUri|Uri)',
    src
))
if buggy2:
    print("FAIL: Dynamic still grouped with DataUri/Uri (buggy pattern, reversed)")
    sys.exit(1)

# Verify all three variants still exist (weren't deleted)
has_datauri = 'DataUri' in src
has_uri = bool(re.search(r'Request::Uri\b', src))
has_dynamic = bool(re.search(r'Request::Dynamic\b', src))

if not (has_datauri and has_uri and has_dynamic):
    print("FAIL: Missing DataUri, Uri, or Dynamic variant in parse.rs")
    sys.exit(1)

print("PASS: DataUri/Uri separated from Dynamic in parse.rs")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.20:.4f}')")
    echo "  +0.20 (total: $SCORE)"
else
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# TEST 3 [pr_diff] (0.15): Regression — the original Worker(path) resolution
# still works: js_value_to_pattern and WorkerAssetReference are present in the
# NodeWorkerConstructor handler.
###############################################################################
echo ""
echo "TEST 3: [pr_diff] Regression — Worker path resolution preserved"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from strip_rust_comments import strip_rust_comments

with open("/workspace/next.js/turbopack/crates/turbopack-ecmascript/src/references/mod.rs") as f:
    raw_src = f.read()

src = strip_rust_comments(raw_src)

idx = src.find('NodeWorkerConstructor')
if idx < 0:
    print("FAIL: NodeWorkerConstructor not found")
    sys.exit(1)

chunk = src[idx:idx+6000]

if 'js_value_to_pattern' not in chunk:
    print("FAIL: js_value_to_pattern removed — Worker(path) resolution broken")
    sys.exit(1)

if 'WorkerAssetReference' not in chunk:
    print("FAIL: WorkerAssetReference removed — Worker(path) broken")
    sys.exit(1)

print("PASS: Worker path resolution preserved")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.15:.4f}')")
    echo "  +0.15 (total: $SCORE)"
else
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# TEST 4 [pr_diff] (0.10): A warning or diagnostic is emitted when the eval
# option is present but its value cannot be statically determined.
# Accepts: span_warn, warn, emit_warning, emit_diagnostic, report, handler.warn, etc.
###############################################################################
echo ""
echo "TEST 4: [pr_diff] Warning/diagnostic for dynamic eval"
python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_rust_comments import strip_rust_comments

with open("/workspace/next.js/turbopack/crates/turbopack-ecmascript/src/references/mod.rs") as f:
    raw_src = f.read()

src = strip_rust_comments(raw_src)

idx = src.find('NodeWorkerConstructor')
if idx < 0:
    print("FAIL: NodeWorkerConstructor not found")
    sys.exit(1)

chunk = src[idx:idx+5000]

# Accept multiple warning/diagnostic emission patterns
has_warning = bool(re.search(
    r'warn\s*\(|'
    r'warn_with_code\s*\(|'
    r'span_warn\s*\(|'
    r'emit_warning\s*\(|'
    r'emit_diagnostic\s*\(|'
    r'report\s*\(|'
    r'handler\s*\.\s*warn',
    chunk
))

if not has_warning:
    print("FAIL: No warning/diagnostic emitted for dynamic eval option")
    sys.exit(1)

# The warning should be in a conditional path (not unconditional)
# Check that it's inside some kind of branch (else, _, match arm)
warn_pos = re.search(
    r'(warn\s*\(|warn_with_code\s*\(|span_warn\s*\(|emit_warning\s*\(|emit_diagnostic\s*\(|handler\s*\.\s*warn)',
    chunk
)
if warn_pos:
    before = chunk[max(0, warn_pos.start()-200):warn_pos.start()]
    # Should be inside a branch — look for else, =>, _, if, match
    has_branch = bool(re.search(r'else\s*\{|=>\s*\{|\b_\b|if\b|match\b', before))
    if not has_branch:
        print("WARN: Warning may not be conditional (minor concern)")

print("PASS: Warning/diagnostic found in NodeWorkerConstructor handler")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.10:.4f}')")
    echo "  +0.10 (total: $SCORE)"
else
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# TEST 5 [pr_diff] (0.10): The error diagnostic in the Worker handler uses a
# Worker-specific error code, NOT the generic FS_METHOD code.
# Accepts: NEW_WORKER, WORKER_EVAL, WORKER_CONSTRUCTOR, or any identifier
# containing "WORKER" that replaces the old FS_METHOD.
###############################################################################
echo ""
echo "TEST 5: [pr_diff] Worker-specific error code (not FS_METHOD)"
python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_rust_comments import strip_rust_comments

with open("/workspace/next.js/turbopack/crates/turbopack-ecmascript/src/references/mod.rs") as f:
    raw_src = f.read()

src = strip_rust_comments(raw_src)

idx = src.find('NodeWorkerConstructor')
if idx < 0:
    print("FAIL: NodeWorkerConstructor not found")
    sys.exit(1)

# Get the handler section up to the next WellKnownFunctionKind or end
chunk = src[idx:idx+6000]

# FS_METHOD should NOT appear in the Worker handler
if 'FS_METHOD' in chunk:
    print("FAIL: Worker handler still uses FS_METHOD error code")
    sys.exit(1)

# Some Worker-specific error code should be present
# Accept any identifier containing WORKER in upper/mixed case
has_worker_code = bool(re.search(r'[A-Z_]*WORKER[A-Z_]*', chunk))
# Also accept: "new_worker", "worker_constructor", etc. in string literals
if not has_worker_code:
    has_worker_code = bool(re.search(r'["\'].*worker.*["\']', chunk, re.IGNORECASE))

if not has_worker_code:
    print("FAIL: No Worker-specific error code found in handler")
    sys.exit(1)

print("PASS: Worker handler uses Worker-specific error code")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.10:.4f}')")
    echo "  +0.10 (total: $SCORE)"
else
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# TEST 6 [structural] (0.10): Anti-stub — the NodeWorkerConstructor handler
# has substantially MORE code than the original (which was ~15 lines).
# The fix adds eval detection logic, so the handler should be meaningfully
# larger. Also checks file line count.
###############################################################################
echo ""
echo "TEST 6: [structural] Anti-stub — handler has substantial new code"
python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_rust_comments import strip_rust_comments

with open("/workspace/next.js/turbopack/crates/turbopack-ecmascript/src/references/mod.rs") as f:
    raw_src = f.read()

# Check total file size
total_lines = raw_src.count('\n')
if total_lines < 2000:
    print(f"FAIL: references/mod.rs only has {total_lines} lines — possible stub")
    sys.exit(1)

src = strip_rust_comments(raw_src)

# Find the NodeWorkerConstructor handler and measure its size
idx = src.find('NodeWorkerConstructor')
if idx < 0:
    print("FAIL: NodeWorkerConstructor not found")
    sys.exit(1)

# Count non-empty lines in the handler section
chunk = src[idx:idx+5000]
code_lines = [l.strip() for l in chunk.split('\n') if l.strip() and l.strip() != '{' and l.strip() != '}']

# The original handler is ~15 lines. The fix adds ~30-50 lines of eval detection.
# Require at least 25 meaningful code lines in the handler.
if len(code_lines) < 25:
    print(f"FAIL: Handler has only {len(code_lines)} code lines — likely stubbed or incomplete")
    sys.exit(1)

print(f"PASS: Handler has {len(code_lines)} code lines, file has {total_lines} total lines")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.10:.4f}')")
    echo "  +0.10 (total: $SCORE)"
else
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# TEST 7 [pr_diff] (0.05): In parse.rs, DataUri and Uri each individually
# produce Dynamic when append_path is called. Verify they have their own
# handling that results in Dynamic.
###############################################################################
echo ""
echo "TEST 7: [pr_diff] DataUri/Uri each produce Dynamic independently"
python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_rust_comments import strip_rust_comments

with open("/workspace/next.js/turbopack/crates/turbopack-core/src/resolve/parse.rs") as f:
    raw_src = f.read()

src = strip_rust_comments(raw_src)

# Find append_path function
ap_idx = src.find('fn append_path')
if ap_idx < 0:
    ap_idx = src.find('append_path')
if ap_idx < 0:
    print("FAIL: append_path not found")
    sys.exit(1)

chunk = src[ap_idx:ap_idx+3000]

# DataUri should have its own arm or be in a separate group from Dynamic
# Check that DataUri appears in the function and is handled
if 'DataUri' not in chunk:
    print("FAIL: DataUri not handled in append_path")
    sys.exit(1)

# Verify Dynamic appears as a result/return value near DataUri/Uri handling
# (they should produce Dynamic when a path is appended)
has_dynamic_result = bool(re.search(r'Dynamic', chunk))
if not has_dynamic_result:
    print("FAIL: No Dynamic result in append_path")
    sys.exit(1)

print("PASS: DataUri/Uri produce Dynamic in append_path")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.05:.4f}')")
    echo "  +0.05 (total: $SCORE)"
else
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# FINAL SCORE
###############################################################################
echo ""
echo "============================================"
echo "FINAL SCORE: $SCORE"
echo "============================================"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
