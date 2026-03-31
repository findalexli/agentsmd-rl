#!/usr/bin/env bash
set +e

REPO="/home/user/uv"
LIB="$REPO/crates/uv-trampoline-builder/src/lib.rs"
TOTAL=0.0
BEHAVIORAL=0.0
REGRESSION=0.0
CONFIG=0.0

add() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
    local bucket="$2"
    local cur
    cur=$(eval echo "\$$bucket")
    eval "$bucket=$(python3 -c "print(round($cur + $1, 4))")"
}

# ── GATE: file exists and is valid UTF-8 ──
# [pr_diff] (0): lib.rs must exist and be readable
if [ ! -f "$LIB" ]; then
    echo "GATE FAIL: lib.rs not found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0,"behavioral":0,"regression":0,"config":0}' > /logs/verifier/reward.json
    exit 0
fi

# ── Behavioral: Error enum has a dedicated WriteResources variant (structural, justified: Rust code, no compiler) ──

# [pr_diff] (0.15): WriteResources variant exists as a struct variant in the Error enum
python3 -c "
import re, sys
src = open('$LIB').read()

# Find the Error enum body
enum_m = re.search(r'pub\s+enum\s+Error\s*\{(.*?)\n\}', src, re.DOTALL)
if not enum_m:
    print('FAIL: Error enum not found')
    sys.exit(1)
enum_body = enum_m.group(1)

# WriteResources must be a struct variant (not unit or tuple)
if not re.search(r'WriteResources\s*\{', enum_body):
    print('FAIL: WriteResources struct variant not found in Error enum')
    sys.exit(1)

# Extract the WriteResources block
m = re.search(r'WriteResources\s*\{([^}]+)\}', enum_body)
if not m:
    print('FAIL: Could not parse WriteResources body')
    sys.exit(1)
body = m.group(1)

# Must have a PathBuf field (any field name)
if not re.search(r':\s*PathBuf', body):
    print('FAIL: WriteResources has no PathBuf field')
    sys.exit(1)

# Must have an io::Error field (any field name)
if not re.search(r'io::Error', body):
    print('FAIL: WriteResources has no io::Error field')
    sys.exit(1)

print('PASS')
" && {
    echo "PASS: WriteResources variant with PathBuf + io::Error fields"
    add 0.15 BEHAVIORAL
} || {
    echo "FAIL: WriteResources variant incomplete or missing"
}

# [pr_diff] (0.10): WriteResources has a #[source] attribute on the error field
python3 -c "
import re, sys
src = open('$LIB').read()
enum_m = re.search(r'pub\s+enum\s+Error\s*\{(.*?)\n\}', src, re.DOTALL)
if not enum_m: sys.exit(1)
# Look for #[source] inside the WriteResources block
m = re.search(r'WriteResources\s*\{([^}]+)\}', enum_m.group(1))
if not m or '#[source]' not in m.group(1):
    sys.exit(1)
" && {
    echo "PASS: WriteResources has #[source] attribute"
    add 0.10 BEHAVIORAL
} || {
    echo "FAIL: WriteResources missing #[source] attribute"
}

# [pr_diff] (0.10): Error display for WriteResources references the path field
python3 -c "
import re, sys
src = open('$LIB').read()
# thiserror #[error(\"...\")] before WriteResources should mention the path somehow
# Accept any display format that includes a path-like field reference
# Use .*? with DOTALL to handle nested parens (e.g. path.user_display())
pattern = r'#\[error\(.*?\b(path|file)\b.*?\)\]\s*(?:#\[.*?\]\s*)*WriteResources'
if not re.search(pattern, src, re.DOTALL):
    sys.exit(1)
" && {
    echo "PASS: WriteResources error display references path"
    add 0.10 BEHAVIORAL
} || {
    echo "FAIL: WriteResources error display missing path reference"
}

# ── Behavioral: WriteResources is actually USED in write_resources function ──

# [pr_diff] (0.25): write_resources maps errors to WriteResources (not Error::Io)
# This is the CORE check: the variant must actually be wired in, not just declared.
python3 -c "
import re, sys
src = open('$LIB').read()

# Extract the write_resources function body
m = re.search(r'fn write_resources\(.*?\n\}', src, re.DOTALL)
if not m:
    print('FAIL: write_resources function not found')
    sys.exit(1)
body = m.group(0)

# WriteResources (or Error::WriteResources) must appear in the function body
if not re.search(r'(Error::)?WriteResources', body):
    print('FAIL: WriteResources not used in write_resources function')
    sys.exit(1)

# Error::Io(...from_raw_os_error...) must NOT appear — it should be replaced
if re.search(r'Error::Io\s*\(\s*io::Error::from_raw_os_error', body, re.DOTALL):
    print('FAIL: Error::Io(io::Error::from_raw_os_error...) still used in write_resources')
    sys.exit(1)

# Must still have error handling — at least 2 map_err or ? operators with WriteResources context
# This prevents the gaming exploit of deleting error handling entirely
err_handling_count = len(re.findall(r'map_err|WriteResources', body))
if err_handling_count < 3:
    print(f'FAIL: Insufficient error handling (found {err_handling_count} map_err/WriteResources refs, need >=3)')
    sys.exit(1)

print('PASS')
" && {
    echo "PASS: write_resources uses WriteResources for error mapping"
    add 0.25 BEHAVIORAL
} || {
    echo "FAIL: write_resources does not properly use WriteResources"
}

# [pr_diff] (0.10): write_resources captures the path in error construction
# The path parameter must be referenced when constructing WriteResources errors
python3 -c "
import re, sys
src = open('$LIB').read()

m = re.search(r'fn write_resources\(.*?\n\}', src, re.DOTALL)
if not m: sys.exit(1)
body = m.group(0)

# WriteResources construction must reference path (path.to_path_buf(), path.into(), etc.)
# This ensures the file path is actually captured in the error
ws_blocks = re.findall(r'WriteResources\s*\{([^}]+)\}', body)
if not ws_blocks:
    # Also accept a closure/function that returns WriteResources
    if not re.search(r'WriteResources\s*\{', body):
        # Maybe via a closure assigned to a variable
        # Look for: let ... = |...| Error::WriteResources { ... path ... }
        # or: let ... = |...| ... WriteResources { ... path ... }
        closures = re.findall(r'\|[^|]*\|\s*(?:Error::)?WriteResources\s*\{([^}]+)\}', body)
        if not closures:
            print('FAIL: No WriteResources construction found')
            sys.exit(1)
        ws_blocks = closures

path_captured = False
for block in ws_blocks:
    # Accept any reference to path parameter: path.to_path_buf(), path.to_owned(), path.into(), etc.
    if re.search(r'\bpath\b', block):
        path_captured = True
        break

if not path_captured:
    print('FAIL: WriteResources does not capture the path parameter')
    sys.exit(1)

print('PASS')
" && {
    echo "PASS: WriteResources captures the file path"
    add 0.10 BEHAVIORAL
} || {
    echo "FAIL: WriteResources does not capture the file path"
}

# ── Regression (pass-to-pass) ──

# [pr_diff] (0.05): Original Error variants still present
python3 -c "
src = open('$LIB').read()
# These are the original variants that must not be removed
required = ['Io(', 'InvalidPath', 'UnsupportedWindowsArch', 'NotWindows', 'UnprocessableMetadata', 'ResourceTooLarge']
for v in required:
    if v not in src:
        print(f'Missing variant: {v}')
        exit(1)
" && {
    echo "PASS: All original Error variants preserved"
    add 0.05 REGRESSION
} || {
    echo "FAIL: Original Error variants missing"
}

# [pr_diff] (0.05): write_resources function signature unchanged
python3 -c "
import re, sys
src = open('$LIB').read()
if not re.search(r'fn\s+write_resources\s*\(\s*path\s*:\s*&Path', src):
    sys.exit(1)
" && {
    echo "PASS: write_resources signature intact"
    add 0.05 REGRESSION
} || {
    echo "FAIL: write_resources signature changed"
}

# [pr_diff] (0.05): ResourceTooLarge still used in write_resources
python3 -c "
import re, sys
src = open('$LIB').read()
m = re.search(r'fn write_resources\(.*?\n\}', src, re.DOTALL)
if not m or 'ResourceTooLarge' not in m.group(0):
    sys.exit(1)
" && {
    echo "PASS: ResourceTooLarge still used in write_resources"
    add 0.05 REGRESSION
} || {
    echo "FAIL: ResourceTooLarge removed from write_resources"
}

# ── Config-derived checks ──

# [agent_config] (0.05): "AVOID using panic!, unreachable!, .unwrap()" — CLAUDE.md:7 @ 8b1a15ea
python3 -c "
import re, sys
src = open('$LIB').read()
m = re.search(r'fn write_resources\(.*?\n\}', src, re.DOTALL)
if not m: sys.exit(1)
body = m.group(0)
for line in body.split('\n'):
    stripped = line.strip()
    if stripped.startswith('//'):
        continue
    if '.unwrap()' in stripped or re.search(r'\bpanic!\b', stripped) or re.search(r'\bunreachable!\b', stripped):
        print(f'Found forbidden pattern: {stripped}')
        sys.exit(1)
" && {
    echo "PASS: No unwrap/panic/unreachable in write_resources"
    add 0.05 CONFIG
} || {
    echo "FAIL: Found unwrap/panic/unreachable in write_resources"
}

# [agent_config] (0.05): "PREFER top-level imports over local imports" — CLAUDE.md:16 @ 8b1a15ea
# If using .user_display() or .simplified(), the Simplified trait must be imported at top level
python3 -c "
import re, sys
src = open('$LIB').read()

# Check if the code uses user_display() or simplified() (methods from Simplified trait)
m = re.search(r'fn write_resources\(.*?\n\}', src, re.DOTALL)
uses_simplified = False
if m:
    if re.search(r'\.(user_display|simplified)\s*\(', m.group(0)):
        uses_simplified = True

# Also check the Error enum display attributes
enum_m = re.search(r'pub\s+enum\s+Error\s*\{(.*?)\n\}', src, re.DOTALL)
if enum_m and re.search(r'\.(user_display|simplified)\s*\(', enum_m.group(1)):
    uses_simplified = True

# Also check #[error(...)] attributes which may call user_display
if re.search(r'user_display|simplified', src):
    uses_simplified = True

if not uses_simplified:
    # If they don't use Simplified methods, this check is N/A — pass
    sys.exit(0)

# If they do use it, must be imported at top level
lines = src.split('\n')
in_fn = False
for line in lines:
    if re.match(r'^(pub\s+)?fn\s', line) or re.match(r'^\s+(pub\s+)?fn\s', line):
        in_fn = True
    if not in_fn and re.search(r'use\s+.*Simplified', line):
        sys.exit(0)

print('FAIL: Simplified used but not imported at top level')
sys.exit(1)
" && {
    echo "PASS: Simplified import check OK"
    add 0.05 CONFIG
} || {
    echo "FAIL: Simplified not imported at top level"
}

# ── Summary ──
echo ""
echo "=== SCORE ==="
echo "Behavioral: $BEHAVIORAL"
echo "Regression: $REGRESSION"
echo "Config:     $CONFIG"
echo "Total:      $TOTAL"

echo "$TOTAL" > /logs/verifier/reward.txt
python3 -c "
import json
print(json.dumps({
    'reward': $TOTAL,
    'behavioral': $BEHAVIORAL,
    'regression': $REGRESSION,
    'config': $CONFIG
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
