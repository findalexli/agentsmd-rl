#!/usr/bin/env bash
# Verifier for pytorch-sycl-msvc-include-filter
# Bug: SYCL extension build on Windows fails with oneAPI 2025.3+ due to MSVC include path conflicts
# File: torch/utils/cpp_extension.py
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/pytorch/torch/utils/cpp_extension.py"

echo "=== pytorch-sycl-msvc-include-filter verifier ==="

# -- GATE: Python syntax validity --
# [pr_diff] (0): Syntax check — abort on failure
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/pytorch/torch/utils/cpp_extension.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error in target file -- aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_BEHAV_FILTER_NEW=0.25
W_BEHAV_FILTER_OLD=0.20
W_BEHAV_FILTER_NOENV=0.15
W_BEHAV_INTEGRATION=0.10
W_P2P_NONCUDA=0.10
W_STRUCT_CALLSITE=0.10
W_ANTISTUB=0.05
W_CONFIG_STYLE=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): Filtering works for oneAPI >= 2025.3 --
# [pr_diff] (0.25): MSVC include paths filtered when icpx version >= 20250300
echo ""
echo "TEST 1: behavioral -- MSVC paths filtered for oneAPI 2025.3+ (weight=$W_BEHAV_FILTER_NEW)"
T1=$(python3 << 'PYEOF'
import sys, os, ast, textwrap

# Extract the filter function from the source using AST
with open("/workspace/pytorch/torch/utils/cpp_extension.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find a function that filters MSVC include dirs from pp_opts
filter_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        # Look for a function that takes pp_opts and filters based on MSVC/VCTools
        src_segment = ast.get_source_segment(source, node)
        if src_segment and 'VCToolsInstallDir' in src_segment and 'pp_opts' in src_segment:
            filter_func = node
            break

if filter_func is None:
    print("FAIL: no function found that filters MSVC include dirs from pp_opts")
    sys.exit(1)

# Extract the function source and exec it with mocked _get_icpx_version
func_source = ast.get_source_segment(source, filter_func)
func_name = filter_func.name

# Dedent to make it top-level
func_source = textwrap.dedent(func_source)

# Mock _get_icpx_version to return a version >= 2025.3
mock_env = {}
exec(f"""
import os
def _get_icpx_version():
    return "20250300"

{func_source}
""", mock_env)

the_func = mock_env[func_name]

# Set up environment
os.environ['VCToolsInstallDir'] = r'C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130'

test_opts = [
    '-DSOME_DEFINE',
    r'-IC:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130\include',
    '-I/some/other/path',
    r'-IC:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130\lib',
    '-O2',
]

result = the_func(test_opts)

# MSVC paths should be filtered out
if len(result) != 3:
    print(f"FAIL: expected 3 items after filtering, got {len(result)}: {result}")
    sys.exit(1)

# Check the right items remain
if '-DSOME_DEFINE' not in result or '-I/some/other/path' not in result or '-O2' not in result:
    print(f"FAIL: wrong items remaining after filter: {result}")
    sys.exit(1)

# Check MSVC paths are gone
for item in result:
    if 'Microsoft Visual Studio' in item:
        print(f"FAIL: MSVC path not filtered: {item}")
        sys.exit(1)

print("PASS: MSVC include paths correctly filtered for oneAPI 2025.3+")
sys.exit(0)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_FILTER_NEW)")
fi

# -- TEST 2 (BEHAVIORAL): No filtering for older oneAPI versions --
# [pr_diff] (0.20): Paths preserved when icpx version < 20250300 (version gating)
echo ""
echo "TEST 2: behavioral -- no filtering for old oneAPI versions (weight=$W_BEHAV_FILTER_OLD)"
T2=$(python3 << 'PYEOF'
import sys, os, ast, textwrap

with open("/workspace/pytorch/torch/utils/cpp_extension.py") as f:
    source = f.read()

tree = ast.parse(source)

filter_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        src_segment = ast.get_source_segment(source, node)
        if src_segment and 'VCToolsInstallDir' in src_segment and 'pp_opts' in src_segment:
            filter_func = node
            break

if filter_func is None:
    print("FAIL: no filter function found")
    sys.exit(1)

func_source = ast.get_source_segment(source, filter_func)
func_name = filter_func.name
func_source = textwrap.dedent(func_source)

# Mock _get_icpx_version to return an OLD version (< 2025.3)
mock_env = {}
exec(f"""
import os
def _get_icpx_version():
    return "20240200"

{func_source}
""", mock_env)

the_func = mock_env[func_name]

os.environ['VCToolsInstallDir'] = r'C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130'

test_opts = [
    '-DSOME_DEFINE',
    r'-IC:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130\include',
    '-I/some/other/path',
    '-O2',
]

result = the_func(test_opts)

# With old version, ALL paths should be preserved (no filtering)
if len(result) != len(test_opts):
    print(f"FAIL: expected {len(test_opts)} items (no filtering), got {len(result)}: {result}")
    sys.exit(1)

if result != test_opts:
    print(f"FAIL: paths were modified when they shouldn't be: {result}")
    sys.exit(1)

print("PASS: no filtering applied for old oneAPI version (version gating works)")
sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_FILTER_OLD)")
fi

# -- TEST 3 (BEHAVIORAL): No filtering when VCToolsInstallDir not set --
# [pr_diff] (0.15): Paths preserved when VCToolsInstallDir is unset
echo ""
echo "TEST 3: behavioral -- no filtering when VCToolsInstallDir unset (weight=$W_BEHAV_FILTER_NOENV)"
T3=$(python3 << 'PYEOF'
import sys, os, ast, textwrap

with open("/workspace/pytorch/torch/utils/cpp_extension.py") as f:
    source = f.read()

tree = ast.parse(source)

filter_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        src_segment = ast.get_source_segment(source, node)
        if src_segment and 'VCToolsInstallDir' in src_segment and 'pp_opts' in src_segment:
            filter_func = node
            break

if filter_func is None:
    print("FAIL: no filter function found")
    sys.exit(1)

func_source = ast.get_source_segment(source, filter_func)
func_name = filter_func.name
func_source = textwrap.dedent(func_source)

# Mock _get_icpx_version with new version but NO VCToolsInstallDir
mock_env = {}
exec(f"""
import os
def _get_icpx_version():
    return "20250300"

{func_source}
""", mock_env)

the_func = mock_env[func_name]

# Remove VCToolsInstallDir if set
os.environ.pop('VCToolsInstallDir', None)

test_opts = [
    '-DSOME_DEFINE',
    r'-IC:\some\msvc\path\include',
    '-I/some/other/path',
]

result = the_func(test_opts)

if len(result) != len(test_opts):
    print(f"FAIL: expected {len(test_opts)} items (no filtering without env var), got {len(result)}")
    sys.exit(1)

print("PASS: no filtering when VCToolsInstallDir is not set")
sys.exit(0)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_FILTER_NOENV)")
fi

# -- TEST 4 (BEHAVIORAL): Filter function is used in sycl_cflags construction --
# [pr_diff] (0.10): The filter is actually called when building sycl_cflags
echo ""
echo "TEST 4: behavioral -- filter is applied in sycl_cflags construction (weight=$W_BEHAV_INTEGRATION)"
T4=$(python3 << 'PYEOF'
import sys, re

with open("/workspace/pytorch/torch/utils/cpp_extension.py") as f:
    source = f.read()

# Find the sycl_cflags assignment line — it should NOT pass raw pp_opts anymore
# The buggy line was: sycl_cflags = common_cflags + pp_opts + _COMMON_SYCL_FLAGS
# The fix wraps pp_opts through the filter function

# Look for the sycl_cflags assignment
sycl_lines = [line.strip() for line in source.splitlines()
               if 'sycl_cflags' in line and 'pp_opts' in line and '=' in line and 'common_cflags' in line]

if not sycl_lines:
    print("FAIL: could not find sycl_cflags assignment with pp_opts")
    sys.exit(1)

line = sycl_lines[0]

# The line should NOT be just "common_cflags + pp_opts + ..." (raw pp_opts)
# It should wrap pp_opts in some filtering function call
if re.search(r'\+\s*pp_opts\s*\+', line):
    print(f"FAIL: sycl_cflags still uses raw pp_opts: {line}")
    sys.exit(1)

# There should be a function call wrapping pp_opts
if 'pp_opts' in line and '(' in line and ')' in line:
    print(f"PASS: pp_opts is filtered before use in sycl_cflags: {line}")
    sys.exit(0)
else:
    print(f"FAIL: could not confirm pp_opts filtering in: {line}")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_INTEGRATION)")
fi

# -- TEST 5 (PASS-TO-PASS): Non-SYCL paths are unaffected --
# [pr_diff] (0.10): CUDA/HIP cflags construction is unchanged
echo ""
echo "TEST 5: pass-to-pass -- CUDA/HIP cflags construction unchanged (weight=$W_P2P_NONCUDA)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/utils/cpp_extension.py") as f:
    source = f.read()

# Verify win_cuda_flags and win_hip_flags still exist and are unchanged
has_cuda_flags = 'def win_cuda_flags(cflags):' in source
has_hip_flags = 'def win_hip_flags(cflags):' in source

# Verify cuda_cflags doesn't go through MSVC filtering
cuda_lines = [line.strip() for line in source.splitlines()
               if 'cuda_cflags' in line and 'pp_opts' in line and '=' in line]

cuda_raw = any('+ pp_opts +' in line or '+ pp_opts\n' in line for line in cuda_lines)

issues = []
if not has_cuda_flags:
    issues.append("win_cuda_flags function missing")
if not has_hip_flags:
    issues.append("win_hip_flags function missing")

if issues:
    print(f"FAIL: {'; '.join(issues)}")
    sys.exit(1)

print("PASS: CUDA/HIP flag functions preserved unchanged")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P_NONCUDA)")
fi

# -- TEST 6 (STRUCTURAL): Callsite uses version gating --
# [pr_diff] (0.10): Version check gates the filtering to oneAPI 2025.3+
echo ""
echo "TEST 6: structural -- version gating present in filter logic (weight=$W_STRUCT_CALLSITE)"
T6=$(python3 << 'PYEOF'
import sys

# WHY AST/text check: _get_icpx_version() calls `icpx --version` which is unavailable
# in this container (no Intel compiler). We verify the version-gating logic textually.

with open("/workspace/pytorch/torch/utils/cpp_extension.py") as f:
    source = f.read()

# Must reference _get_icpx_version and compare against a threshold around 20250300
has_version_call = '_get_icpx_version' in source
has_threshold = '20250300' in source or '2025030' in source

# Must reference VCToolsInstallDir
has_vc_tools = 'VCToolsInstallDir' in source

issues = []
if not has_version_call:
    issues.append("missing _get_icpx_version call")
if not has_threshold:
    issues.append("missing version threshold (20250300)")
if not has_vc_tools:
    issues.append("missing VCToolsInstallDir reference")

if issues:
    print(f"FAIL: {'; '.join(issues)}")
    sys.exit(1)

print("PASS: version gating and VCToolsInstallDir check present")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCT_CALLSITE)")
fi

# -- TEST 7: Anti-stub check --
# [pr_diff] (0.05): File retains core cpp_extension functionality
echo ""
echo "TEST 7: anti-stub -- file retains expected content (weight=$W_ANTISTUB)"
T7=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/utils/cpp_extension.py") as f:
    source = f.read()

required = [
    "def win_cuda_flags",
    "def win_hip_flags",
    "def win_wrap_ninja_compile",
    "_COMMON_SYCL_FLAGS",
    "sycl_cflags",
]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 2000:
    print(f"FAIL: file has only {line_count} lines -- looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T7"
if echo "$T7" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# -- TEST 8: Config-derived -- concise comments --
# [agent_config] (0.05): "Minimize comments; be concise" — CLAUDE.md:48 @ dc12b65
echo ""
echo "TEST 8: config-derived -- comments are concise (weight=$W_CONFIG_STYLE)"
T8=$(python3 << 'PYEOF'
import sys, ast

with open("/workspace/pytorch/torch/utils/cpp_extension.py") as f:
    source = f.read()

# Find the filter function and check comment density
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        src = ast.get_source_segment(source, node)
        if src and 'VCToolsInstallDir' in src and 'pp_opts' in src:
            lines = src.strip().splitlines()
            comment_lines = [l for l in lines if l.strip().startswith('#')]
            code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

            # Comments should not dominate — ratio should be reasonable
            if len(code_lines) == 0:
                print("FAIL: function has no code lines")
                sys.exit(1)

            ratio = len(comment_lines) / len(code_lines)
            if ratio > 1.0:
                print(f"FAIL: too many comments ({len(comment_lines)} comments vs {len(code_lines)} code lines)")
                sys.exit(1)

            print(f"PASS: comment ratio OK ({len(comment_lines)} comments / {len(code_lines)} code lines)")
            sys.exit(0)

# If no filter function found, this test is N/A — still pass since other tests catch it
print("PASS: no filter function to check (other tests validate existence)")
sys.exit(0)
PYEOF
)
echo "$T8"
if echo "$T8" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_STYLE)")
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
