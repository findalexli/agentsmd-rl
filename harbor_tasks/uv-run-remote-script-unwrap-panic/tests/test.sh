#!/usr/bin/env bash
set +e

TOTAL=0.0
SCORE=0.0
REWARD_FILE="/logs/verifier/reward.txt"
REWARD_JSON="/logs/verifier/reward.json"

add_score() {
    local weight="$1" pass="$2" label="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" -eq 1 ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        echo "PASS ($weight): $label"
    else
        echo "FAIL ($weight): $label"
    fi
}

cd /repo

# ============================================================
# GATE: Syntax / compilation check
# ============================================================
# [pr_diff] (GATE): Code compiles
echo "=== GATE: Compilation check ==="
if ! cargo check -p uv 2>/tmp/compile_err.txt; then
    echo "GATE FAIL: Compilation failed"
    cat /tmp/compile_err.txt
    echo "0.0" > "$REWARD_FILE"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > "$REWARD_JSON"
    exit 0
fi
echo "GATE PASS: Code compiles"

# ============================================================
# Fail-to-pass: Core bug fix (0.60)
# ============================================================

# [pr_diff] (0.35): The .unwrap() on the optional downloaded_script in as_command is eliminated
# Accepts ANY valid fix: removing param, making non-optional, using ?, match, ok_or, etc.
echo "=== F2P: No unsafe unwrap on downloaded_script in as_command ==="
PASS_CORE=0
CORE_CHECK=$(python3 -c "
import re, sys

with open('crates/uv/src/commands/project/run.rs') as f:
    src = f.read()

# Find as_command function body (robust: match fn to closing brace at same indent)
lines = src.split('\n')
in_func = False
brace_depth = 0
func_lines = []
for line in lines:
    if re.search(r'fn\s+as_command\b', line):
        in_func = True
    if in_func:
        func_lines.append(line)
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0 and len(func_lines) > 1:
            break

if not func_lines:
    print('NO_FUNC')
    sys.exit(0)

body = '\n'.join(func_lines)

# The bug: .unwrap() on downloaded_script which is Option<&NamedTempFile>
# Check 1: if downloaded_script is not mentioned at all — param was removed (gold patch + others)
if 'downloaded_script' not in body:
    print('FIXED_PARAM_REMOVED')
    sys.exit(0)

# Check 2: downloaded_script exists but is NOT Option type (made non-optional)
sig_match = re.search(r'fn\s+as_command\s*\([^)]*\)', body, re.DOTALL)
if sig_match:
    sig = sig_match.group(0)
    if 'downloaded_script' in sig and 'Option' not in sig:
        print('FIXED_NON_OPTIONAL')
        sys.exit(0)

# Check 3: downloaded_script exists as Option but no .unwrap() on it
has_unwrap_on_ds = False
for line in func_lines:
    stripped = line.strip()
    if 'downloaded_script' in stripped and '.unwrap()' in stripped:
        has_unwrap_on_ds = True

if not has_unwrap_on_ds:
    print('FIXED_SAFE_HANDLING')
    sys.exit(0)

print('BUGGY')
" 2>/dev/null)
if echo "$CORE_CHECK" | grep -q 'FIXED'; then
    PASS_CORE=1
fi
add_score 0.35 $PASS_CORE "No unsafe .unwrap() on downloaded_script in as_command"

# [pr_diff] (0.25): PythonRemote execution path cannot panic on missing download
# Accepts: file stored in enum, param made non-optional, error handling added
echo "=== F2P: PythonRemote execution is panic-safe ==="
PASS_SAFE=0
SAFE_CHECK=$(python3 -c "
import re, sys

with open('crates/uv/src/commands/project/run.rs') as f:
    src = f.read()

# Strategy 1: PythonRemote now holds a file-type field (not just a URL)
# Accept NamedTempFile, TempPath, PathBuf, tempfile::*, or any path-like type
if re.search(r'PythonRemote\s*[\({].*(?:NamedTempFile|TempPath|PathBuf|tempfile|DownloadedScript|ScriptFile)', src):
    print('SAFE_FILE_IN_ENUM')
    sys.exit(0)

# Strategy 2: as_command doesn't take downloaded_script Option at all
if not re.search(r'fn\s+as_command[^{]*Option[^{]*downloaded', src, re.DOTALL):
    # No Option<...downloaded_script> in as_command — safe
    print('SAFE_NO_OPTION')
    sys.exit(0)

# Strategy 3: Option is handled with ?, match, if let, ok_or, etc. (not unwrap)
lines = src.split('\n')
in_func = False
brace_depth = 0
func_body = []
for line in lines:
    if re.search(r'fn\s+as_command\b', line):
        in_func = True
    if in_func:
        func_body.append(line)
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0 and len(func_body) > 1:
            break

body_text = '\n'.join(func_body)
if 'downloaded_script' in body_text:
    # Has the param — check it's safely handled
    if '.unwrap()' not in body_text:
        print('SAFE_NO_UNWRAP')
        sys.exit(0)
    # Check if unwrap is on a different variable
    has_ds_unwrap = any('downloaded_script' in l and '.unwrap()' in l for l in func_body)
    if not has_ds_unwrap:
        print('SAFE_UNWRAP_ELSEWHERE')
        sys.exit(0)

print('UNSAFE')
" 2>/dev/null)
if echo "$SAFE_CHECK" | grep -q 'SAFE'; then
    PASS_SAFE=1
fi
add_score 0.25 $PASS_SAFE "PythonRemote execution path is panic-safe"

# ============================================================
# Pass-to-pass: Upstream regression tests (0.15)
# ============================================================

# [repo_tests] (0.10): uv-cli crate tests still pass
echo "=== P2P: uv-cli tests ==="
PASS_CLI=0
if cargo test -p uv-cli 2>&1 | grep -q "test result: ok"; then
    PASS_CLI=1
fi
add_score 0.10 $PASS_CLI "uv-cli crate tests still pass"

# [repo_tests] (0.05): uv-scripts crate tests still pass
echo "=== P2P: uv-scripts tests ==="
PASS_SCRIPTS=0
if cargo test -p uv-scripts 2>&1 | grep -q "test result: ok"; then
    PASS_SCRIPTS=1
fi
add_score 0.05 $PASS_SCRIPTS "uv-scripts crate tests still pass"

# ============================================================
# Anti-stub / regression (0.10)
# ============================================================

# [pr_diff] (0.05): as_command still exists with a real implementation
echo "=== Anti-stub: as_command has real implementation ==="
PASS_REAL=0
REAL_CHECK=$(python3 -c "
import re

with open('crates/uv/src/commands/project/run.rs') as f:
    src = f.read()

lines = src.split('\n')
in_func = False
brace_depth = 0
func_lines = []
for line in lines:
    if re.search(r'fn\s+as_command\b', line):
        in_func = True
    if in_func:
        func_lines.append(line)
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0 and len(func_lines) > 1:
            break

# Count meaningful lines (not empty, comments, braces-only)
meaningful = [l for l in func_lines if l.strip() and not l.strip().startswith('//') and l.strip() not in ('{', '}')]
if len(meaningful) >= 8:
    print('REAL')
else:
    print('STUB')
" 2>/dev/null)
if echo "$REAL_CHECK" | grep -q 'REAL'; then
    PASS_REAL=1
fi
add_score 0.05 $PASS_REAL "as_command has real implementation (>=8 meaningful lines)"

# [pr_diff] (0.05): PythonRemote variant still exists in RunCommand enum
echo "=== Anti-stub: PythonRemote variant exists ==="
PASS_VARIANT=0
if grep -q 'PythonRemote' crates/uv/src/commands/project/run.rs; then
    PASS_VARIANT=1
fi
add_score 0.05 $PASS_VARIANT "PythonRemote variant still exists in RunCommand"

# ============================================================
# Config-derived checks (0.15)
# ============================================================

# [agent_config] (0.10): "AVOID using panic!, unreachable!, .unwrap()" — CLAUDE.md:7 @ 867e535f
echo "=== Config: No .unwrap() in PythonRemote code paths ==="
PASS_NO_PANIC=0
PANIC_CHECK=$(python3 -c "
import re

with open('crates/uv/src/commands/project/run.rs') as f:
    src = f.read()

# Extract as_command body
lines = src.split('\n')
in_func = False
brace_depth = 0
func_lines = []
for line in lines:
    if re.search(r'fn\s+as_command\b', line):
        in_func = True
    if in_func:
        func_lines.append(line)
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0 and len(func_lines) > 1:
            break

body = '\n'.join(func_lines)

# Check for any .unwrap() in PythonRemote handling within as_command
# Find lines between PythonRemote and next variant/closing
remote_lines = []
in_remote = False
for line in func_lines:
    if 'PythonRemote' in line:
        in_remote = True
    if in_remote:
        remote_lines.append(line)
        # Stop at next match arm or function end
        if line.strip().startswith('}') and len(remote_lines) > 2:
            break

remote_block = '\n'.join(remote_lines)
if '.unwrap()' in remote_block:
    print('HAS_UNWRAP')
elif not remote_lines:
    # PythonRemote handling restructured; check whole function
    if '.unwrap()' not in body or 'downloaded_script' not in body:
        print('NO_UNWRAP')
    else:
        print('HAS_UNWRAP')
else:
    print('NO_UNWRAP')
" 2>/dev/null)
if echo "$PANIC_CHECK" | grep -q 'NO_UNWRAP'; then
    PASS_NO_PANIC=1
fi
add_score 0.10 $PASS_NO_PANIC "No .unwrap() in PythonRemote code paths (CLAUDE.md:7)"

# [agent_config] (0.05): "PREFER patterns like if let to handle fallibility" — CLAUDE.md:8 @ 867e535f
# Accepts: match destructuring, if let, ?, ok_or, map — or removing the Option entirely
echo "=== Config: Safe error handling pattern ==="
PASS_PATTERN=0
PATTERN_CHECK=$(python3 -c "
import re

with open('crates/uv/src/commands/project/run.rs') as f:
    src = f.read()

# Find as_command
lines = src.split('\n')
in_func = False
brace_depth = 0
func_lines = []
for line in lines:
    if re.search(r'fn\s+as_command\b', line):
        in_func = True
    if in_func:
        func_lines.append(line)
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0 and len(func_lines) > 1:
            break

body = '\n'.join(func_lines)

# If downloaded_script is gone, the Option was eliminated entirely — safe by construction
if 'downloaded_script' not in body:
    print('SAFE')
# Match/if-let/? used instead of unwrap
elif any(kw in body for kw in ['.ok_or', 'if let', '? ;', '?;', '? ,', '?,', '.map(', '.and_then', 'match ']):
    if '.unwrap()' not in body or 'downloaded_script' not in [l for l in func_lines if '.unwrap()' in l]:
        print('SAFE')
    else:
        print('UNSAFE')
elif '.unwrap()' not in body:
    print('SAFE')
else:
    print('UNSAFE')
" 2>/dev/null)
if echo "$PATTERN_CHECK" | grep -q 'SAFE'; then
    PASS_PATTERN=1
fi
add_score 0.05 $PASS_PATTERN "Safe fallibility handling pattern (CLAUDE.md:8)"

# ============================================================
# Summary
# ============================================================
echo ""
echo "=== SCORE: $SCORE / $TOTAL ==="

REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo "$REWARD" > "$REWARD_FILE"

BEH=$(python3 -c "
checks = [(0.35, $PASS_CORE), (0.25, $PASS_SAFE)]
print(round(sum(w for w, p in checks if p), 4))
")
REG=$(python3 -c "
checks = [(0.10, $PASS_CLI), (0.05, $PASS_SCRIPTS)]
print(round(sum(w for w, p in checks if p), 4))
")
STRUCT=$(python3 -c "
checks = [(0.05, $PASS_REAL), (0.05, $PASS_VARIANT)]
print(round(sum(w for w, p in checks if p), 4))
")
CONF=$(python3 -c "
checks = [(0.10, $PASS_NO_PANIC), (0.05, $PASS_PATTERN)]
print(round(sum(w for w, p in checks if p), 4))
")

echo "{\"reward\": $REWARD, \"behavioral\": $BEH, \"regression\": $REG, \"structural\": $STRUCT, \"config\": $CONF, \"style_rubric\": 0.0}" > "$REWARD_JSON"
echo "Reward: $REWARD"
cat "$REWARD_JSON"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
