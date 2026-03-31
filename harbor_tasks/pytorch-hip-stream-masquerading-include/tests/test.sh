#!/usr/bin/env bash
set -uo pipefail

REPO="/workspace/pytorch"
CUDA_STREAM_H="$REPO/c10/cuda/CUDAStream.h"
HIP_MASQ_H="$REPO/aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h"

###############################################################################
# GATE: Both files must exist
###############################################################################
for f in "$CUDA_STREAM_H" "$HIP_MASQ_H"; do
  if [ ! -f "$f" ]; then
    echo "GATE FAIL: $f does not exist"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
  fi
done

###############################################################################
# All checks via Python for robust C++ source analysis
# C++ headers cannot be compiled in this CPU-only environment, so all checks
# are structural — but we strip comments and verify declaration+delegation
# patterns to resist gaming.
###############################################################################
python3 << 'PYEOF'
import re, json, sys

def strip_cpp_comments(text):
    """Remove // line comments and /* block comments */ from C++ source."""
    text = re.sub(r'//[^\n]*', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    return text

def extract_rocm_block(text):
    """Extract content between #ifdef USE_ROCM and matching #endif."""
    m = re.search(r'#ifdef\s+USE_ROCM\b(.*?)#endif', text, re.DOTALL)
    return m.group(1) if m else ''

cuda_h_raw = open('/workspace/pytorch/c10/cuda/CUDAStream.h').read()
hip_masq_raw = open('/workspace/pytorch/aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h').read()

cuda_h = strip_cpp_comments(cuda_h_raw)
hip_masq = strip_cpp_comments(hip_masq_raw)
rocm_block = extract_rocm_block(cuda_h)

scores = {}

# Detect fix approach: #include of masquerading header vs inline wrappers
include_approach = bool(re.search(
    r'#include\s*[<"].*HIPStreamMasqueradingAsCUDA', rocm_block))

###########################################################################
# BEHAVIORAL: Per-function declaration + delegation (0.14 each × 5 = 0.70)
#
# Each masquerading function must be:
#   (a) present as a DECLARATION (name followed by '(' or '=', in
#       comment-stripped source), AND
#   (b) backed by proper delegation to the underlying c10::cuda function.
#
# Two valid approaches are accepted:
#   A) #include the masquerading header inside USE_ROCM — functions checked
#      in the included header.
#   B) Declare wrapper functions / auto& aliases directly in CUDAStream.h
#      inside the USE_ROCM block, delegating to c10::cuda equivalents.
#
# Justification for structural checks: These are C++ headers requiring the
# full PyTorch build toolchain + GPU hardware to compile. Cannot be called.
###########################################################################

FUNCS = [
    # (masquerading_name, delegation_target_regex)
    # Delegation targets use negative lookahead to avoid matching the
    # masquerading name itself (e.g. getStreamFromPool != getStreamFromPoolMasq...)
    # [pr_diff] (0.14): getCurrentHIPStreamMasqueradingAsCUDA accessible via CUDAStream.h
    ('getCurrentHIPStreamMasqueradingAsCUDA', r'getCurrentCUDAStream'),
    # [pr_diff] (0.14): getDefaultHIPStreamMasqueradingAsCUDA accessible via CUDAStream.h
    ('getDefaultHIPStreamMasqueradingAsCUDA', r'getDefaultCUDAStream'),
    # [pr_diff] (0.14): getStreamFromPoolMasqueradingAsCUDA accessible via CUDAStream.h
    ('getStreamFromPoolMasqueradingAsCUDA',   r'getStreamFromPool(?!Masq)'),
    # [pr_diff] (0.14): getStreamFromExternalMasqueradingAsCUDA accessible via CUDAStream.h
    ('getStreamFromExternalMasqueradingAsCUDA', r'getStreamFromExternal(?!Masq)'),
    # [pr_diff] (0.14): setCurrentHIPStreamMasqueradingAsCUDA accessible via CUDAStream.h
    ('setCurrentHIPStreamMasqueradingAsCUDA', r'setCurrentCUDAStream'),
]

for func_name, delegate_re in FUNCS:
    if include_approach:
        # Include approach: verify function exists in the included header
        has_decl = bool(re.search(rf'{func_name}\s*[\(=]', hip_masq))
        has_delegate = bool(re.search(delegate_re, hip_masq))
        if has_decl and has_delegate:
            scores[func_name] = 0.14
            print(f"PASS: {func_name} available via #include (decl + delegation)")
        elif has_decl:
            scores[func_name] = 0.0
            print(f"FAIL: {func_name} declared but no delegation in included header")
        else:
            scores[func_name] = 0.0
            print(f"FAIL: {func_name} not found in included header")
    else:
        # Wrapper approach: verify declaration AND delegation in USE_ROCM block
        has_decl = bool(re.search(rf'{func_name}\s*[\(=]', rocm_block))
        has_delegate = bool(re.search(delegate_re, rocm_block))
        if has_decl and has_delegate:
            scores[func_name] = 0.14
            print(f"PASS: {func_name} declared with delegation in USE_ROCM block")
        elif has_decl:
            scores[func_name] = 0.0
            print(f"FAIL: {func_name} declared but no delegation to underlying function")
        else:
            scores[func_name] = 0.0
            print(f"FAIL: {func_name} not found as declaration in USE_ROCM block")

###########################################################################
# PASS-TO-PASS REGRESSION (0.15)
###########################################################################

# [pr_diff] (0.05): HIPStreamMasqueradingAsCUDA class preserved in original header
if 'class HIPStreamMasqueradingAsCUDA' in hip_masq_raw:
    scores['class_preserved'] = 0.05
    print("PASS: HIPStreamMasqueradingAsCUDA class preserved")
else:
    scores['class_preserved'] = 0.0
    print("FAIL: HIPStreamMasqueradingAsCUDA class removed")

# [pr_diff] (0.05): operator<< for HIPStreamMasqueradingAsCUDA preserved
if re.search(r'operator\s*<<.*HIPStreamMasqueradingAsCUDA', hip_masq_raw):
    scores['operator_preserved'] = 0.05
    print("PASS: operator<< preserved")
else:
    scores['operator_preserved'] = 0.0
    print("FAIL: operator<< removed")

# [pr_diff] (0.05): Non-masquerading HIP aliases still in CUDAStream.h
# Use negative lookahead so we don't match the Masquerading variants
has_get = bool(re.search(r'getCurrentHIPStream(?!Masq)\s*[\(=]', cuda_h))
has_set = bool(re.search(r'setCurrentHIPStream(?!Masq)\s*[\(=]', cuda_h))
if has_get and has_set:
    scores['nonmasq_preserved'] = 0.05
    print("PASS: Non-masquerading HIP aliases preserved")
else:
    scores['nonmasq_preserved'] = 0.0
    print("FAIL: Non-masquerading HIP aliases missing")

###########################################################################
# CONFIG-DERIVED (0.10)
###########################################################################

# [agent_config] (0.05): "Minimize comments; be concise" — CLAUDE.md:48
rocm_raw_block = extract_rocm_block(cuda_h_raw)  # with comments kept
comment_lines = len([l for l in rocm_raw_block.splitlines()
                     if l.strip().startswith('//')])
if comment_lines <= 5:
    scores['minimal_comments'] = 0.05
    print(f"PASS: Minimal comments in USE_ROCM block ({comment_lines} lines)")
else:
    scores['minimal_comments'] = 0.0
    print(f"FAIL: Too many comment lines in USE_ROCM block ({comment_lines})")

# [agent_config] (0.05): "Match existing code style" — CLAUDE.md:57
# Functions should be in c10::hip namespace (or accessible via include in that scope)
hip_ns_match = re.search(
    r'namespace\s+c10\s*(?:::\s*hip|[^{]*\{[^}]*namespace\s+hip)', cuda_h, re.DOTALL)
if hip_ns_match:
    # Check that masquerading content is inside or near the namespace block
    ns_start = hip_ns_match.start()
    ns_region = cuda_h[ns_start:ns_start+2000]
    if 'MasqueradingAsCUDA' in ns_region or include_approach:
        scores['namespace'] = 0.05
        print("PASS: Masquerading functions in c10::hip namespace")
    else:
        scores['namespace'] = 0.0
        print("FAIL: Masquerading functions not in c10::hip namespace")
else:
    if include_approach:
        scores['namespace'] = 0.05
        print("PASS: Include approach (namespace in original header)")
    else:
        scores['namespace'] = 0.0
        print("FAIL: c10::hip namespace not found")

# Totals per category for JSON breakdown
# Weight budget: behavioral >= 0.60, regression ~ 0.10-0.20, config <= 0.15
###########################################################################
# COMPUTE FINAL SCORE
###########################################################################
total = round(sum(scores.values()), 2)

behavioral_keys = [f[0] for f in FUNCS]
regression_keys = ['class_preserved', 'operator_preserved', 'nonmasq_preserved']
config_keys = ['minimal_comments', 'namespace']

behavioral = round(sum(scores.get(k, 0) for k in behavioral_keys), 2)
regression = round(sum(scores.get(k, 0) for k in regression_keys), 2)
config = round(sum(scores.get(k, 0) for k in config_keys), 2)

print(f"\nScore: {total}")
print(f"  Behavioral: {behavioral}  Regression: {regression}  Config: {config}")

with open('/logs/verifier/reward.txt', 'w') as f:
    f.write(str(total))

result = {
    'reward': total,
    'behavioral': behavioral,
    'regression': regression,
    'config': config,
    'style_rubric': 0.0,
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(result, f)

print(json.dumps(result))
PYEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
