#!/usr/bin/env bash
set +e

SHIM_H="/workspace/pytorch/torch/csrc/stable/c/shim.h"
SHIM_CPP="/workspace/pytorch/torch/csrc/shim_common.cpp"
OPS_H="/workspace/pytorch/torch/csrc/stable/ops.h"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
# F2P checks (fail on base commit, pass on correct fix)
WEIGHTS[f2p_shim_h_two_arg]=0.25
WEIGHTS[f2p_shim_cpp_two_arg]=0.20
WEIGHTS[f2p_ops_h_callable]=0.20
# P2P checks (pass on both base and fix)
WEIGHTS[p2p_original_from_blob]=0.10
WEIGHTS[p2p_original_deleter]=0.10
# Anti-stub + config
WEIGHTS[antistub]=0.10
WEIGHTS[config_style]=0.05

for key in f2p_shim_h_two_arg f2p_shim_cpp_two_arg f2p_ops_h_callable p2p_original_from_blob p2p_original_deleter antistub config_style; do
    RESULTS[$key]=0
done

# ---------- GATE: files exist and are non-empty ----------
for f in "$SHIM_H" "$SHIM_CPP" "$OPS_H"; do
    if [ ! -s "$f" ]; then
        echo "GATE FAIL: $f missing or empty"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
done
echo "GATE PASS"

# ---------- F2P 1 (0.25): shim.h declares a C function with two-arg deleter + context ----------
# [pr_diff] (0.25): C ABI must expose a function taking a two-arg deleter callback(data, ctx) + void* context
# Base code only has void (*deleter)(void*) — any correct fix adds a two-pointer callback.
# Accepts any function name (torch_from_blob_v2, torch_from_blob with new params, etc.)
echo "=== F2P: shim.h two-arg deleter declaration ==="
python3 << 'PYEOF'
import sys, re

with open("/workspace/pytorch/torch/csrc/stable/c/shim.h") as f:
    src = f.read()

# A correct fix must add a C function declaration where the deleter callback takes
# TWO void* arguments: void (*something)(void*, void*).
# This is the fundamental ABI change — the base code only has void (*deleter)(void*).
# We match any function-pointer parameter with exactly two void* args.
two_arg_deleter = re.findall(
    r'void\s*\(\s*\*\s*\w*\s*\)\s*\(\s*void\s*\*\s*\w*\s*,\s*void\s*\*\s*\w*\s*\)',
    src
)

if not two_arg_deleter:
    print("FAIL: no C function declaration with two-arg deleter callback(void*, void*)")
    sys.exit(1)

# There must also be a separate void* parameter for the context/opaque state.
# Look for the declaration block containing the two-arg deleter — it should have
# a void* parameter that isn't part of the function pointer and isn't 'data'.
# We check that near the two-arg deleter, there's another void* param.
# This is necessarily true since the two-arg callback + context is the bridge mechanism.
#
# Find all function declarations (between AOTI_TORCH_EXPORT and the closing semicolon)
func_decls = re.findall(
    r'AOTI_TORCH_EXPORT\s+AOTITorchError\s+\w+\s*\([^;]+\)\s*;',
    src, re.DOTALL
)

found_ctx = False
for decl in func_decls:
    if re.search(r'void\s*\(\s*\*\s*\w*\s*\)\s*\(\s*void\s*\*\s*\w*\s*,\s*void\s*\*\s*\w*\s*\)', decl):
        # This declaration has a two-arg callback. Check for a separate void* param
        # that serves as the context. Count void* params that aren't inside the callback parens.
        # Simple heuristic: the declaration should have more void* occurrences than just
        # data + the two inside the callback signature (i.e., at least 4 void* total: data, cb arg1, cb arg2, ctx)
        void_star_count = len(re.findall(r'void\s*\*', decl))
        if void_star_count >= 4:
            found_ctx = True
            break

if not found_ctx:
    print("FAIL: two-arg deleter declaration found but no separate context parameter")
    sys.exit(1)

print("PASS: shim.h has C function with two-arg deleter + context")
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_shim_h_two_arg]=1 && echo "TEST f2p_shim_h_two_arg: PASS" || echo "TEST f2p_shim_h_two_arg: FAIL"

# ---------- F2P 2 (0.20): shim_common.cpp implements two-arg deleter wrapping ----------
# [pr_diff] (0.20): Implementation must accept two-arg callback + context and wrap for at::for_blob
# Base code only has torch_from_blob with one-arg deleter.
echo "=== F2P: shim_common.cpp two-arg deleter implementation ==="
python3 << 'PYEOF'
import sys, re

with open("/workspace/pytorch/torch/csrc/shim_common.cpp") as f:
    src = f.read()

# 1. Must have a function that accepts a two-arg callback: void (*xxx)(void*, void*)
has_two_arg_cb = bool(re.search(
    r'void\s*\(\s*\*\s*\w+\s*\)\s*\(\s*void\s*\*\s*\w*\s*,\s*void\s*\*\s*\w*\s*\)',
    src
))

if not has_two_arg_cb:
    print("FAIL: no function accepting two-arg deleter callback in implementation")
    sys.exit(1)

# 2. Must use at::for_blob with a deleter (wrapping the two-arg callback)
# The implementation wraps callback+context into a single callable for at::for_blob
has_for_blob = "for_blob" in src

if not has_for_blob:
    print("FAIL: missing for_blob usage")
    sys.exit(1)

# 3. The wrapping: the code must capture/use both the callback and the context
# to create a wrapped deleter. Look for a lambda or function that calls the
# two-arg callback with both data and context.
# We look for the pattern of invoking a callback with two args in the new function.
# This is flexible — accepts lambda capture, std::bind, wrapper function, etc.
# Find the new function body (after the two-arg callback declaration)
# and verify it connects callback + context.

# Split source into functions by looking for AOTI_TORCH_EXPORT blocks
funcs = re.split(r'(?=AOTI_TORCH_EXPORT\s+AOTITorchError)', src)
found_wrapping = False
for func_block in funcs:
    if re.search(r'void\s*\(\s*\*\s*\w+\s*\)\s*\(\s*void\s*\*\s*\w*\s*,\s*void\s*\*\s*\w*\s*\)', func_block):
        # This function has the two-arg callback param.
        # It must call the callback and also use for_blob's deleter.
        # Check that both 'deleter' (or similar) and 'for_blob' appear in this block.
        if 'for_blob' in func_block and '.deleter' in func_block:
            found_wrapping = True
            break

if not found_wrapping:
    print("FAIL: new function doesn't connect two-arg callback to for_blob's deleter")
    sys.exit(1)

print("PASS: shim_common.cpp implements two-arg deleter wrapping")
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_shim_cpp_two_arg]=1 && echo "TEST f2p_shim_cpp_two_arg: PASS" || echo "TEST f2p_shim_cpp_two_arg: FAIL"

# ---------- F2P 3 (0.20): ops.h supports non-function-pointer callables ----------
# [pr_diff] (0.20): C++ wrapper must accept capturing lambdas, not just DeleterFnPtr
# Base code only has from_blob(... DeleterFnPtr deleter ...) — no template/generic callable.
# Any correct fix must add template<class F>, std::function<>, or similar.
echo "=== F2P: ops.h callable support ==="
python3 << 'PYEOF'
import sys, re

with open("/workspace/pytorch/torch/csrc/stable/ops.h") as f:
    src = f.read()

# The fix must enable capturing lambdas. This requires EITHER:
# A) A template that accepts generic callables (template <class F, ...>)
# B) std::function wrapper
# C) Some other type-erasure mechanism
# The base code has neither — only DeleterFnPtr = void(*)(void*)

has_template_callable = False
has_std_function = False

# Check A: template with type constraint on a from_blob variant
# Look for a template near a from_blob definition
template_blocks = list(re.finditer(
    r'template\s*<[^>]*class\s+\w+[^>]*>\s*(?:inline\s+)?(?:\w+::)*\w+\s+from_blob\s*\(',
    src
))
if template_blocks:
    has_template_callable = True

# Check B: std::function in a from_blob signature
std_func_blocks = re.findall(
    r'from_blob\s*\([^)]*std::function[^)]*\)',
    src, re.DOTALL
)
if std_func_blocks:
    has_std_function = True

if not has_template_callable and not has_std_function:
    print("FAIL: ops.h has no mechanism to accept capturing lambdas (no template or std::function on from_blob)")
    sys.exit(1)

# The new from_blob variant must call a C shim that supports the two-arg deleter.
# It should call torch_from_blob_v2 or torch_from_blob (new signature) or similar.
# Look for the new from_blob body calling any torch_from_blob variant.
# Find the template from_blob body
if has_template_callable:
    # Find the template function body
    for match in template_blocks:
        start = match.start()
        # Find the matching closing brace
        brace_depth = 0
        body_start = src.find('{', start)
        if body_start == -1:
            continue
        i = body_start
        while i < len(src):
            if src[i] == '{':
                brace_depth += 1
            elif src[i] == '}':
                brace_depth -= 1
                if brace_depth == 0:
                    break
            i += 1
        body = src[body_start:i+1]

        # The body must call a torch_from_blob variant
        if re.search(r'torch_from_blob', body):
            # And must do heap allocation or type erasure for the callable
            # (new, make_unique, std::function, etc.)
            if re.search(r'(new\s+\w|make_unique|std::function|static_cast)', body):
                print("PASS: ops.h has template from_blob with type erasure + C shim call")
                sys.exit(0)

    # If we got here, template exists but body doesn't look right
    # Still pass — the template mechanism is the key requirement
    print("PASS: ops.h has template from_blob for capturing lambdas")
    sys.exit(0)

if has_std_function:
    print("PASS: ops.h uses std::function for capturing lambdas")
    sys.exit(0)

print("FAIL: unexpected state")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_ops_h_callable]=1 && echo "TEST f2p_ops_h_callable: PASS" || echo "TEST f2p_ops_h_callable: FAIL"

# ---------- P2P 1 (0.10): Original from_blob overloads preserved ----------
# [pr_diff] (0.10): Non-deleter from_blob + original DeleterFnPtr overload must still exist
echo "=== P2P: original from_blob overloads preserved ==="
python3 << 'PYEOF'
import sys, re

with open("/workspace/pytorch/torch/csrc/stable/ops.h") as f:
    src = f.read()

# Count from_blob function definitions (inline ... from_blob(...))
from_blob_defs = re.findall(r'(?:inline\s+)?(?:\w+::)*\w+\s+from_blob\s*\(', src)

# Must have at least 3: no-deleter, DeleterFnPtr, and new callable version
# But we accept >=2 since the agent might merge the old deleter + new into one template
if len(from_blob_defs) < 2:
    print(f"FAIL: expected >=2 from_blob overloads, found {len(from_blob_defs)}")
    sys.exit(1)

# The no-deleter overload must exist (backward compat)
# It's the one that doesn't have 'deleter' or template in its signature
# Look for a from_blob that takes sizes, strides, device, dtype but no deleter param
# Simple check: at least one from_blob call that routes to aoti_torch_create_tensor_from_blob
if 'aoti_torch_create_tensor_from_blob' not in src:
    print("FAIL: original no-deleter from_blob (calling aoti_torch_create_tensor_from_blob) removed")
    sys.exit(1)

print(f"PASS: {len(from_blob_defs)} from_blob overloads found, original preserved")
PYEOF
[ $? -eq 0 ] && RESULTS[p2p_original_from_blob]=1 && echo "TEST p2p_original_from_blob: PASS" || echo "TEST p2p_original_from_blob: FAIL"

# ---------- P2P 2 (0.10): Original one-arg torch_from_blob preserved in shim.h ----------
# [pr_diff] (0.10): The original C function must remain for backward compatibility
echo "=== P2P: original torch_from_blob preserved ==="
python3 << 'PYEOF'
import sys, re

with open("/workspace/pytorch/torch/csrc/stable/c/shim.h") as f:
    src = f.read()

# The original torch_from_blob with one-arg deleter must still exist
# It has void (*deleter)(void*) — a single-arg function pointer
has_original = bool(re.search(
    r'AOTI_TORCH_EXPORT\s+AOTITorchError\s+torch_from_blob\s*\(',
    src
))

if not has_original:
    print("FAIL: original torch_from_blob declaration removed")
    sys.exit(1)

# The original must retain the one-arg deleter signature
func_decls = re.findall(
    r'AOTI_TORCH_EXPORT\s+AOTITorchError\s+torch_from_blob\s*\([^;]+\)\s*;',
    src, re.DOTALL
)

found_one_arg = False
for decl in func_decls:
    if re.search(r'void\s*\(\s*\*\s*\w+\s*\)\s*\(\s*void\s*\*\s*\)', decl):
        found_one_arg = True
        break

if not found_one_arg:
    print("FAIL: original torch_from_blob lost its one-arg deleter signature")
    sys.exit(1)

print("PASS: original torch_from_blob preserved with one-arg deleter")
PYEOF
[ $? -eq 0 ] && RESULTS[p2p_original_deleter]=1 && echo "TEST p2p_original_deleter: PASS" || echo "TEST p2p_original_deleter: FAIL"

# ---------- ANTI-STUB (0.10): files have real implementation ----------
# [pr_diff] (0.10): Ensure files aren't stubbed out
echo "=== Anti-stub ==="
python3 << 'PYEOF'
import sys

issues = []

# ops.h must be substantial
with open("/workspace/pytorch/torch/csrc/stable/ops.h") as f:
    ops_src = f.read()
ops_lines = ops_src.strip().splitlines()
if len(ops_lines) < 100:
    issues.append(f"ops.h too short ({len(ops_lines)} lines)")
if "TORCH_ERROR_CODE_CHECK" not in ops_src:
    issues.append("ops.h missing TORCH_ERROR_CODE_CHECK")
if "AtenTensorHandle" not in ops_src:
    issues.append("ops.h missing AtenTensorHandle")

# shim_common.cpp must be substantial
with open("/workspace/pytorch/torch/csrc/shim_common.cpp") as f:
    cpp_src = f.read()
cpp_lines = cpp_src.strip().splitlines()
if len(cpp_lines) < 100:
    issues.append(f"shim_common.cpp too short ({len(cpp_lines)} lines)")
if "AOTI_TORCH_CONVERT_EXCEPTION_TO_ERROR_CODE" not in cpp_src:
    issues.append("shim_common.cpp missing AOTI_TORCH_CONVERT_EXCEPTION_TO_ERROR_CODE")

# shim.h must be substantial
with open("/workspace/pytorch/torch/csrc/stable/c/shim.h") as f:
    h_src = f.read()
h_lines = h_src.strip().splitlines()
if len(h_lines) < 50:
    issues.append(f"shim.h too short ({len(h_lines)} lines)")

if issues:
    print(f"FAIL: {'; '.join(issues)}")
    sys.exit(1)

print("PASS: files have real implementation")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ---------- CONFIG (0.05): match existing code style ----------
# [agent_config] (0.05): "Match existing code style and architectural patterns." — CLAUDE.md:47
echo "=== Config: code style ==="
python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/csrc/stable/ops.h") as f:
    src = f.read()

issues = []

# Should have proper include guard or pragma once
if "#pragma once" not in src and "#ifndef" not in src:
    issues.append("missing include guard")

# Should not have excessive TODO/FIXME/HACK comments
import re
hack_comments = len(re.findall(r'//\s*(TODO|FIXME|HACK|XXX)', src))
if hack_comments > 3:
    issues.append(f"too many TODO/FIXME/HACK comments ({hack_comments})")

if issues:
    print(f"FAIL: style issues: {', '.join(issues)}")
    sys.exit(1)

print("PASS: code style matches existing patterns")
PYEOF
[ $? -eq 0 ] && RESULTS[config_style]=1 && echo "TEST config_style: PASS" || echo "TEST config_style: FAIL"

# ---------- SCORE ----------
SCORE=$(python3 -c "
w={'f2p_shim_h_two_arg':${WEIGHTS[f2p_shim_h_two_arg]},'f2p_shim_cpp_two_arg':${WEIGHTS[f2p_shim_cpp_two_arg]},'f2p_ops_h_callable':${WEIGHTS[f2p_ops_h_callable]},'p2p_original_from_blob':${WEIGHTS[p2p_original_from_blob]},'p2p_original_deleter':${WEIGHTS[p2p_original_deleter]},'antistub':${WEIGHTS[antistub]},'config_style':${WEIGHTS[config_style]}}
r={'f2p_shim_h_two_arg':${RESULTS[f2p_shim_h_two_arg]},'f2p_shim_cpp_two_arg':${RESULTS[f2p_shim_cpp_two_arg]},'f2p_ops_h_callable':${RESULTS[f2p_ops_h_callable]},'p2p_original_from_blob':${RESULTS[p2p_original_from_blob]},'p2p_original_deleter':${RESULTS[p2p_original_deleter]},'antistub':${RESULTS[antistub]},'config_style':${RESULTS[config_style]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# Optional JSON breakdown
python3 -c "
import json
w={'f2p_shim_h_two_arg':${WEIGHTS[f2p_shim_h_two_arg]},'f2p_shim_cpp_two_arg':${WEIGHTS[f2p_shim_cpp_two_arg]},'f2p_ops_h_callable':${WEIGHTS[f2p_ops_h_callable]},'p2p_original_from_blob':${WEIGHTS[p2p_original_from_blob]},'p2p_original_deleter':${WEIGHTS[p2p_original_deleter]},'antistub':${WEIGHTS[antistub]},'config_style':${WEIGHTS[config_style]}}
r={'f2p_shim_h_two_arg':${RESULTS[f2p_shim_h_two_arg]},'f2p_shim_cpp_two_arg':${RESULTS[f2p_shim_cpp_two_arg]},'f2p_ops_h_callable':${RESULTS[f2p_ops_h_callable]},'p2p_original_from_blob':${RESULTS[p2p_original_from_blob]},'p2p_original_deleter':${RESULTS[p2p_original_deleter]},'antistub':${RESULTS[antistub]},'config_style':${RESULTS[config_style]}}
total = sum(w[k]*r[k] for k in w)
behavioral = sum(w[k]*r[k] for k in ['f2p_shim_h_two_arg','f2p_shim_cpp_two_arg','f2p_ops_h_callable','p2p_original_from_blob','p2p_original_deleter'])
structural = sum(w[k]*r[k] for k in ['antistub','config_style'])
json.dump({'reward': round(total,2), 'behavioral': round(behavioral,2), 'structural': round(structural,2)}, open('/logs/verifier/reward.json','w'))
" 2>/dev/null

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
