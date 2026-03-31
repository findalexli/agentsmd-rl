#!/usr/bin/env bash
set +e

REWARD=0
TOTAL=100

cd /workspace/next.js

TARGET_FILE="turbopack/crates/turbopack/src/lib.rs"
MOD_FILE="turbopack/crates/turbopack/src/module_options/mod.rs"

mkdir -p /logs/verifier

##############################################################################
# GATE: File exists and is not trivially broken
##############################################################################
# [pr_diff] (gate): Target file must exist
if [ ! -f "$TARGET_FILE" ]; then
    echo "GATE FAIL: $TARGET_FILE does not exist"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: File exists"

##############################################################################
# Fail-to-pass #1 (0.35): Core fix — process_default_internal uses
# "webpack_loaders" layer name (not the buggy "turbopack_use_loaders")
#
# WHY structural: Rust code requires the full turbopack/swc workspace to
# compile (~10 min, 8GB+ RAM, Rust toolchain). Cannot execute in this container.
#
# Flexible: accepts string literal, const, or variable — just checks that
# "webpack_loaders" appears in the process_default_internal function body
# and "turbopack_use_loaders" does NOT.
##############################################################################
# [pr_diff] (0.35): Layer name in process_default_internal must be "webpack_loaders"
python3 -c "
import sys

src = open('$TARGET_FILE').read()

# Find the process_default_internal function body
fn_start = src.find('fn process_default_internal')
if fn_start == -1:
    print('FAIL: process_default_internal function not found')
    sys.exit(1)

# Extract a generous window of the function (it's ~100 lines)
fn_body = src[fn_start:fn_start + 8000]

# The function must reference the webpack_loaders layer name
# This accepts: rcstr!(\"webpack_loaders\"), a const, or any form
if 'webpack_loaders' not in fn_body:
    print('FAIL: process_default_internal does not reference webpack_loaders layer')
    sys.exit(1)

# The buggy name must NOT appear in this function
if 'turbopack_use_loaders' in fn_body:
    print('FAIL: process_default_internal still uses buggy turbopack_use_loaders name')
    sys.exit(1)

# Verify it's used in a Layer context (not just a comment or unrelated string)
# Accept: Layer::new(rcstr!(\"webpack_loaders\")), Layer::new(CONST), etc.
has_layer_context = ('Layer' in fn_body and 'webpack_loaders' in fn_body)
if not has_layer_context:
    print('FAIL: webpack_loaders not in Layer context')
    sys.exit(1)

print('PASS: process_default_internal uses webpack_loaders layer')
" 2>/dev/null
if [ $? -eq 0 ]; then
    REWARD=$((REWARD + 35))
    echo "PASS [0.35]: Core fix — webpack_loaders layer in process_default_internal"
else
    echo "FAIL [0.35]: Core fix — webpack_loaders layer in process_default_internal"
fi

##############################################################################
# Fail-to-pass #2 (0.15): Old buggy layer name fully removed from file
##############################################################################
# [pr_diff] (0.15): turbopack_use_loaders must not appear anywhere in lib.rs
python3 -c "
import sys
src = open('$TARGET_FILE').read()
if 'turbopack_use_loaders' in src:
    print('FAIL: Buggy layer name turbopack_use_loaders still present in file')
    sys.exit(1)
print('PASS: Old buggy layer name fully removed')
" 2>/dev/null
if [ $? -eq 0 ]; then
    REWARD=$((REWARD + 15))
    echo "PASS [0.15]: Old buggy layer name removed"
else
    echo "FAIL [0.15]: Old buggy layer name still present"
fi

##############################################################################
# Fail-to-pass #3 (0.15): Cross-file consistency — both lib.rs and
# module_options/mod.rs reference the same "webpack_loaders" layer name.
# This is the root cause: mismatched names between the two files.
##############################################################################
# [pr_diff] (0.15): Both code paths use consistent layer name
python3 -c "
import sys

lib_src = open('$TARGET_FILE').read()
mod_src = open('$MOD_FILE').read()

# Both files must contain the webpack_loaders string
if 'webpack_loaders' not in lib_src:
    print('FAIL: lib.rs missing webpack_loaders reference')
    sys.exit(1)
if 'webpack_loaders' not in mod_src:
    print('FAIL: module_options/mod.rs missing webpack_loaders reference')
    sys.exit(1)

# Neither file should have the buggy name
if 'turbopack_use_loaders' in lib_src or 'turbopack_use_loaders' in mod_src:
    print('FAIL: Buggy layer name still present in one of the files')
    sys.exit(1)

print('PASS: Both files use consistent webpack_loaders layer name')
" 2>/dev/null
if [ $? -eq 0 ]; then
    REWARD=$((REWARD + 15))
    echo "PASS [0.15]: Cross-file layer name consistency"
else
    echo "FAIL [0.15]: Cross-file layer name inconsistency"
fi

##############################################################################
# Pass-to-pass #1 (0.10): Loader pipeline structure preserved
# The process_default_internal function must still contain the key constructs
# of the loader pipeline — ensures the agent didn't delete/gut the function.
##############################################################################
# [pr_diff] (0.10): Key loader pipeline constructs present
python3 -c "
import sys
src = open('$TARGET_FILE').read()
required = [
    'node_evaluate_asset_context',
    'WebpackLoaderItem',
    'WebpackLoaders',
    'loader_runner_package',
    'SourceTransforms',
]
missing = [r for r in required if r not in src]
if missing:
    print(f'FAIL: Missing expected constructs: {missing}')
    sys.exit(1)
print('PASS: Loader pipeline structure preserved')
" 2>/dev/null
if [ $? -eq 0 ]; then
    REWARD=$((REWARD + 10))
    echo "PASS [0.10]: Loader pipeline structure preserved"
else
    echo "FAIL [0.10]: Loader pipeline structure broken"
fi

##############################################################################
# Pass-to-pass #2 (0.05): Other Layer::new calls untouched
# The externals-tracing layer must still be present (collateral damage check)
##############################################################################
# [pr_diff] (0.05): externals-tracing layer not removed
python3 -c "
import sys
src = open('$TARGET_FILE').read()
if 'externals-tracing' not in src:
    print('FAIL: externals-tracing layer missing (collateral damage)')
    sys.exit(1)
print('PASS: Other layers untouched')
" 2>/dev/null
if [ $? -eq 0 ]; then
    REWARD=$((REWARD + 5))
    echo "PASS [0.05]: Other layers untouched"
else
    echo "FAIL [0.05]: Other layers damaged"
fi

##############################################################################
# Anti-stub (0.05): File is not gutted
# WHY structural: Can't compile Rust; check file substantiality
##############################################################################
# [pr_diff] (0.05): File must be substantial (original is ~1000 lines)
python3 -c "
import sys
src = open('$TARGET_FILE').read()
lines = src.strip().splitlines()
if len(lines) < 800:
    print(f'FAIL: File suspiciously short ({len(lines)} lines, expected ~1000+)')
    sys.exit(1)
print(f'PASS: File has {len(lines)} lines (not stubbed)')
" 2>/dev/null
if [ $? -eq 0 ]; then
    REWARD=$((REWARD + 5))
    echo "PASS [0.05]: Anti-stub check"
else
    echo "FAIL [0.05]: File appears stubbed"
fi

##############################################################################
# Structural (0.05): Layer name is used as an argument to evaluate context
# Flexible: checks that node_evaluate_asset_context and webpack_loaders
# appear near each other (within ~500 chars), accepting any syntax.
##############################################################################
# [pr_diff] (0.05): webpack_loaders used in evaluate context (flexible nesting)
python3 -c "
import sys

src = open('$TARGET_FILE').read()

# Find node_evaluate_asset_context calls
idx = 0
found = False
while True:
    pos = src.find('node_evaluate_asset_context', idx)
    if pos == -1:
        break
    # Check if webpack_loaders appears within 500 chars after the call
    window = src[pos:pos + 500]
    if 'webpack_loaders' in window:
        found = True
        break
    idx = pos + 1

if not found:
    print('FAIL: webpack_loaders not near any node_evaluate_asset_context call')
    sys.exit(1)
print('PASS: webpack_loaders used in evaluate context')
" 2>/dev/null
if [ $? -eq 0 ]; then
    REWARD=$((REWARD + 5))
    echo "PASS [0.05]: Layer name in evaluate context"
else
    echo "FAIL [0.05]: Layer name not in evaluate context"
fi

##############################################################################
# Config-derived (0.05): Formatting compliance
# [agent_config] (0.05): No tabs or trailing whitespace — AGENTS.md:414 @ b6ff1f60
# Checks all lines containing "webpack_loaders" for basic formatting
##############################################################################
python3 -c "
import sys
src = open('$TARGET_FILE').read()
lines = src.splitlines()
for i, line in enumerate(lines):
    if 'webpack_loaders' in line:
        if line.rstrip() != line:
            print(f'FAIL: Line {i+1} has trailing whitespace')
            sys.exit(1)
        if '\t' in line:
            print(f'FAIL: Line {i+1} uses tabs instead of spaces')
            sys.exit(1)
        if len(line) > 120:
            print(f'FAIL: Line {i+1} exceeds 120 chars')
            sys.exit(1)
print('PASS: Formatting looks correct')
" 2>/dev/null
if [ $? -eq 0 ]; then
    REWARD=$((REWARD + 5))
    echo "PASS [0.05]: Rust formatting compliance"
else
    echo "FAIL [0.05]: Rust formatting issue"
fi

##############################################################################
# Compute final reward
##############################################################################
FINAL=$(echo "scale=2; $REWARD / $TOTAL" | bc)
echo ""
echo "Total: $FINAL / 1.00 ($REWARD / $TOTAL)"
echo "$FINAL" > /logs/verifier/reward.txt

# Breakdown: behavioral=0.65, regression=0.15, structural=0.10, config=0.05
BEH=$(echo "scale=2; ($REWARD - 15) / $TOTAL" | bc 2>/dev/null || echo "0")
echo "{\"reward\": $FINAL, \"behavioral\": 0, \"regression\": 0, \"config\": 0, \"style_rubric\": 0}" > /logs/verifier/reward.json

# Also write to legacy location
cp /logs/verifier/reward.txt /workspace/next.js/reward.txt 2>/dev/null || true
cp /logs/verifier/reward.json /workspace/next.js/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
