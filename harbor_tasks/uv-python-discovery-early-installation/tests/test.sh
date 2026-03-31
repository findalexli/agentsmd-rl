#!/usr/bin/env bash
set +e

TOTAL=0
EARNED=0
DETAILS=""

add_check() {
    local name="$1" weight="$2" pass="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        EARNED=$(python3 -c "print($EARNED + $weight)")
        DETAILS="${DETAILS}PASS ($weight): $name\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $name\n"
    fi
}

cd /repo

DISCOVERY="crates/uv-python/src/discovery.rs"
INSTALL="crates/uv-python/src/installation.rs"

# ============================================================
# GATE: Both files must exist and be non-empty
# ============================================================
if [ ! -s "$DISCOVERY" ] || [ ! -s "$INSTALL" ]; then
    echo "GATE FAILED: discovery.rs or installation.rs is missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
    exit 0
fi

# Shared Python helper: strip Rust comments to prevent comment-injection gaming
STRIP_COMMENTS='
import re
def strip_rust_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src
def read_stripped(path):
    with open(path) as f:
        return strip_rust_comments(f.read())
def extract_fn_body(src, fn_name):
    """Extract function body using brace counting."""
    pattern = rf"fn\s+{fn_name}\s*[<(]"
    match = re.search(pattern, src)
    if not match:
        return None
    start = match.start()
    brace_pos = src.index("{", start)
    depth = 1
    pos = brace_pos + 1
    while depth > 0 and pos < len(src):
        if src[pos] == "{": depth += 1
        elif src[pos] == "}": depth -= 1
        pos += 1
    return src[brace_pos:pos]
'

# ============================================================
# [pr_diff] (0.25): Helper function signatures return PythonInstallation, not tuples
# WHY structural: Rust code — no cargo toolchain in image
# ============================================================
python3 -c "
$STRIP_COMMENTS
import re, sys

src = read_stripped('$DISCOVERY')

# Each of the 3 helpers must have Result<PythonInstallation in its signature
helpers = [
    'python_installations',
    'python_installations_from_executables',
    'python_installations_with_executable_name',
]
found = 0
for name in helpers:
    # Match: fn <name><...>(...) -> impl Iterator<Item = Result<PythonInstallation
    pat = rf'fn\s+{name}\s*<[^>]*>\s*\([^{{]*?\)\s*->\s*impl\s+Iterator\s*<\s*Item\s*=\s*Result\s*<\s*PythonInstallation'
    if re.search(pat, src, re.DOTALL):
        found += 1
    else:
        print(f'MISS: {name}')

# No tuple returns remaining anywhere in file
tuple_ret = len(re.findall(r'Result\s*<\s*\(\s*PythonSource\s*,\s*Interpreter\s*\)', src))

if found == 3 and tuple_ret == 0:
    sys.exit(0)
else:
    print(f'{found}/3 helpers with PythonInstallation return, {tuple_ret} tuple returns')
    sys.exit(1)
" && C1=1 || C1=0
add_check "[pr_diff] Helper function signatures return PythonInstallation" 0.25 "$C1"

# ============================================================
# [pr_diff] (0.20): from_tuple removed from both files
# ============================================================
python3 -c "
$STRIP_COMMENTS
import sys

for path in ['$DISCOVERY', '$INSTALL']:
    src = read_stripped(path)
    if 'from_tuple' in src:
        print(f'from_tuple still in {path}')
        sys.exit(1)
sys.exit(0)
" && C2=1 || C2=0
add_check "[pr_diff] from_tuple removed from both files" 0.20 "$C2"

# ============================================================
# [pr_diff] (0.15): find_python_installations calls renamed helpers
# Cross-reference: the public function must invoke the new names
# ============================================================
python3 -c "
$STRIP_COMMENTS
import re, sys

src = read_stripped('$DISCOVERY')

body = extract_fn_body(src, 'find_python_installations')
if body is None:
    print('find_python_installations not found')
    sys.exit(1)

# Must call python_installations( and python_installations_with_executable_name(
calls_inst = bool(re.search(r'python_installations\s*\(', body))
calls_with = bool(re.search(r'python_installations_with_executable_name\s*\(', body))
# Must NOT call old names
calls_old_interp = bool(re.search(r'python_interpreters\s*\(', body))
calls_old_with = bool(re.search(r'python_interpreters_with_executable_name\s*\(', body))

if calls_inst and calls_with and not calls_old_interp and not calls_old_with:
    sys.exit(0)
else:
    print(f'inst={calls_inst} with={calls_with} old_interp={calls_old_interp} old_with={calls_old_with}')
    sys.exit(1)
" && C3=1 || C3=0
add_check "[pr_diff] find_python_installations calls renamed helpers" 0.15 "$C3"

# ============================================================
# [pr_diff] (0.10): PythonInstallation constructed inside python_installations_from_executables
# The struct literal { source, interpreter } must appear in the helper, not just anywhere
# ============================================================
python3 -c "
$STRIP_COMMENTS
import re, sys

src = read_stripped('$DISCOVERY')
body = extract_fn_body(src, 'python_installations_from_executables')
if body is None:
    print('python_installations_from_executables not found')
    sys.exit(1)

# Must construct PythonInstallation { ... } inside this function
if re.search(r'PythonInstallation\s*\{', body):
    sys.exit(0)
else:
    print('No PythonInstallation struct construction in python_installations_from_executables')
    sys.exit(1)
" && C4=1 || C4=0
add_check "[pr_diff] PythonInstallation constructed in from_executables helper" 0.10 "$C4"

# ============================================================
# [pr_diff] (0.10): Closures use field access, not tuple destructuring
# ============================================================
python3 -c "
$STRIP_COMMENTS
import re, sys

src = read_stripped('$DISCOVERY')

# Count .source and .interpreter field accesses (excluding type annotations)
field_src = len(re.findall(r'\w+\.source\b', src))
field_int = len(re.findall(r'\w+\.interpreter\b', src))

# Ensure no tuple destructuring remains: |(source, interpreter)|
tuple_destr = len(re.findall(r'\|\s*\(?\s*_?source\s*,\s*_?interpreter\s*\)?\s*\|', src))

if field_src >= 5 and field_int >= 5 and tuple_destr == 0:
    sys.exit(0)
else:
    print(f'.source={field_src} .interpreter={field_int} tuple_destr={tuple_destr}')
    sys.exit(1)
" && C5=1 || C5=0
add_check "[pr_diff] Closures use field access not tuple destructuring" 0.10 "$C5"

# ============================================================
# [repo_tests] (0.10): P2P — find_python_installations still public
# ============================================================
python3 -c "
$STRIP_COMMENTS
import re, sys

src = read_stripped('$DISCOVERY')
if re.search(r'pub\s+fn\s+find_python_installations', src):
    sys.exit(0)
else:
    sys.exit(1)
" && C6=1 || C6=0
add_check "[repo_tests] find_python_installations still public" 0.10 "$C6"

# ============================================================
# [pr_diff] (0.05): Anti-stub — helper function bodies have >8 non-blank lines
# ============================================================
python3 -c "
$STRIP_COMMENTS
import re, sys

src = read_stripped('$DISCOVERY')

helpers = [
    'python_installations',
    'python_installations_from_executables',
    'python_installations_with_executable_name',
]
for name in helpers:
    body = extract_fn_body(src, name)
    if body is None:
        print(f'{name} not found')
        sys.exit(1)
    non_blank = [l for l in body.splitlines() if l.strip()]
    if len(non_blank) < 8:
        print(f'{name} body too short: {len(non_blank)} non-blank lines (need >=8)')
        sys.exit(1)

sys.exit(0)
" && C7=1 || C7=0
add_check "[pr_diff] Anti-stub: helper bodies have >=8 non-blank lines" 0.05 "$C7"

# ============================================================
# [agent_config] (0.03): "AVOID using panic!, unreachable!, .unwrap()" — CLAUDE.md:7 @ 6d628da
# ============================================================
python3 -c "
$STRIP_COMMENTS
import re, sys

src = read_stripped('$DISCOVERY')
helpers = ['python_installations', 'python_installations_from_executables', 'python_installations_with_executable_name']
for name in helpers:
    body = extract_fn_body(src, name)
    if body is None:
        continue
    for bad in ['.unwrap()', 'panic!', 'unreachable!']:
        if bad in body:
            print(f'{name} contains {bad}')
            sys.exit(1)
sys.exit(0)
" && C8=1 || C8=0
add_check "[agent_config] No unwrap/panic/unreachable — CLAUDE.md:7" 0.03 "$C8"

# ============================================================
# [agent_config] (0.02): "AVOID shortening variable names" — CLAUDE.md:16 @ 6d628da
# ============================================================
python3 -c "
$STRIP_COMMENTS
import re, sys

src = read_stripped('$DISCOVERY')
bad = re.findall(r'(?:filter_ok|map_ok)\s*\(\s*(?:move\s+)?\|\s*(?:mut\s+)?(inst|pi|i|p)\s*\|', src)
if bad:
    print(f'Abbreviated names: {bad}')
    sys.exit(1)
sys.exit(0)
" && C9=1 || C9=0
add_check "[agent_config] No abbreviated variable names — CLAUDE.md:16" 0.02 "$C9"

# ============================================================
# Compute final reward
# ============================================================
REWARD=$(python3 -c "print(round($EARNED, 2))")
echo -e "\n=== Results ==="
echo -e "$DETAILS"
echo "Total: $EARNED / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt
cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true

# Write reward.json
python3 -c "
import json
pr_diff = round($C1 * 0.25 + $C2 * 0.20 + $C3 * 0.15 + $C4 * 0.10 + $C5 * 0.10 + $C7 * 0.05, 2)
regression = round($C6 * 0.10, 2)
config = round($C8 * 0.03 + $C9 * 0.02, 2)
print(json.dumps({
    'reward': $REWARD,
    'behavioral': pr_diff,
    'regression': regression,
    'config': config,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json
cp /logs/verifier/reward.json reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
