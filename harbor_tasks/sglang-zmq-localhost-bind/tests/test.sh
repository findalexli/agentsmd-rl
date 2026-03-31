#!/usr/bin/env bash
set +e

NETWORK_PY="/workspace/sglang/python/sglang/srt/utils/network.py"
SCHEDULER_CLIENT="/workspace/sglang/python/sglang/multimodal_gen/runtime/scheduler_client.py"
ENCODE_RECEIVER="/workspace/sglang/python/sglang/srt/disaggregation/encode_receiver.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# behavioral >= 0.60, structural <= 0.40
WEIGHTS[behav_f2p_default]=0.35
WEIGHTS[p2p_explicit_host]=0.15
WEIGHTS[p2p_explicit_wild]=0.10
WEIGHTS[structural_broker]=0.10
WEIGHTS[structural_no_wildcard]=0.10
WEIGHTS[structural_receiver]=0.10
WEIGHTS[config_safe_default]=0.05
WEIGHTS[antistub]=0.05

for key in behav_f2p_default p2p_explicit_host p2p_explicit_wild structural_broker structural_no_wildcard structural_receiver config_safe_default antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: Syntax check ----------
for f in "$NETWORK_PY" "$SCHEDULER_CLIENT" "$ENCODE_RECEIVER"; do
    python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "GATE FAIL: $(basename $f) syntax error"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
done
echo "GATE PASS: All files parse"

# ---------- BEHAVIORAL FAIL-TO-PASS (0.35): Default binding is localhost ----------
# [pr_diff] (0.35): get_zmq_socket_on_host binds to localhost by default instead of tcp://*
python3 << 'PYEOF'
import sys, zmq
sys.path.insert(0, "/workspace/sglang/python")
from sglang.srt.utils.network import get_zmq_socket_on_host

# Call without host argument — must bind to localhost, not wildcard
port, sock = get_zmq_socket_on_host(zmq.Context(), zmq.PULL)
endpoint = sock.getsockopt_string(zmq.LAST_ENDPOINT)
sock.close()

# Must NOT bind to wildcard (0.0.0.0 or *)
if "0.0.0.0" in endpoint or "*" in endpoint:
    print(f"FAIL: bound to wildcard: {endpoint}")
    sys.exit(1)

# Accept any localhost representation (127.0.0.1, ::1)
if "127.0.0.1" in endpoint or "::1" in endpoint:
    print(f"PASS: bound to localhost: {endpoint}")
    sys.exit(0)

# Any other non-wildcard binding is acceptable
print(f"PASS: non-wildcard endpoint: {endpoint}")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_f2p_default]=1; echo "behav_f2p_default: PASS"; else echo "behav_f2p_default: FAIL"; fi

# ---------- PASS-TO-PASS (0.15): Explicit host still works ----------
# [pr_diff] (0.15): Passing an explicit host binds correctly (regression check)
python3 << 'PYEOF'
import sys, zmq
sys.path.insert(0, "/workspace/sglang/python")
from sglang.srt.utils.network import get_zmq_socket_on_host

port, sock = get_zmq_socket_on_host(zmq.Context(), zmq.PULL, host="127.0.0.1")
endpoint = sock.getsockopt_string(zmq.LAST_ENDPOINT)
sock.close()

if "127.0.0.1" in endpoint and port > 0:
    print(f"PASS: explicit host works, port={port}")
    sys.exit(0)
else:
    print(f"FAIL: endpoint={endpoint}, port={port}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[p2p_explicit_host]=1; echo "p2p_explicit_host: PASS"; else echo "p2p_explicit_host: FAIL"; fi

# ---------- PASS-TO-PASS (0.10): Explicit wildcard host for cross-machine reachability ----------
# [pr_diff] (0.10): Callers that need cross-machine access can still pass explicit "0.0.0.0"
python3 << 'PYEOF'
import sys, zmq
sys.path.insert(0, "/workspace/sglang/python")
from sglang.srt.utils.network import get_zmq_socket_on_host

# Explicit "0.0.0.0" must still be allowed for cross-machine use cases
port, sock = get_zmq_socket_on_host(zmq.Context(), zmq.PULL, host="0.0.0.0")
endpoint = sock.getsockopt_string(zmq.LAST_ENDPOINT)
sock.close()

if port > 0:
    print(f"PASS: explicit wildcard bind works: {endpoint}")
    sys.exit(0)
else:
    print("FAIL: explicit wildcard bind failed")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[p2p_explicit_wild]=1; echo "p2p_explicit_wild: PASS"; else echo "p2p_explicit_wild: FAIL"; fi

# ---------- STRUCTURAL (0.10): Broker no longer binds to tcp://* ----------
# [pr_diff] (0.10): run_zeromq_broker does not bind to tcp://*
# WHY NOT BEHAVIORAL: run_zeromq_broker is async, requires ServerArgs with heavy sglang imports
python3 << 'PYEOF'
import sys

with open("/workspace/sglang/python/sglang/multimodal_gen/runtime/scheduler_client.py") as f:
    lines = f.readlines()

# Negative check only: tcp://* must not appear in non-comment code
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if "tcp://*" in stripped and not stripped.startswith("#"):
        print(f"FAIL: wildcard bind at line {i}: {stripped}")
        sys.exit(1)

# Accept ANY safe binding (127.0.0.1, localhost, variable, config) — no literal required
print("PASS: broker does not bind to tcp://*")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural_broker]=1; echo "structural_broker: PASS"; else echo "structural_broker: FAIL"; fi

# ---------- STRUCTURAL (0.10): No tcp://* wildcard defaults in affected files ----------
# [pr_diff] (0.10): No remaining tcp://* wildcard binds as defaults
python3 << 'PYEOF'
import sys

violations = []
files_to_check = [
    "/workspace/sglang/python/sglang/srt/utils/network.py",
    "/workspace/sglang/python/sglang/multimodal_gen/runtime/scheduler_client.py",
]

for fpath in files_to_check:
    with open(fpath) as f:
        for i, line in enumerate(f, 1):
            stripped = line.strip()
            if "tcp://*" in stripped and not stripped.startswith("#"):
                violations.append(f"{fpath}:{i}: {stripped}")

if violations:
    print("FAIL: wildcard binds found:")
    for v in violations:
        print(f"  {v}")
    sys.exit(1)
else:
    print("PASS: no wildcard binds")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural_no_wildcard]=1; echo "structural_no_wildcard: PASS"; else echo "structural_no_wildcard: FAIL"; fi

# ---------- STRUCTURAL (0.10): Encode receiver call sites are safe ----------
# [pr_diff] (0.10): Encode receiver get_zmq_socket_on_host calls are safe
# WHY AST: encode_receiver.py imports torch, sglang.srt — can't import on CPU-only image
python3 << 'PYEOF'
import ast, sys

# Strategy: if the default in network.py is safe (localhost), then receiver calls
# are safe even without explicit host args. This avoids penalizing a valid alternative fix.

with open("/workspace/sglang/python/sglang/srt/utils/network.py") as f:
    net_src = f.read()
net_tree = ast.parse(net_src)

# Check if get_zmq_socket_on_host defaults to localhost
default_is_safe = False
func_body_safe = False
for node in ast.walk(net_tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_zmq_socket_on_host":
        # Check if host param has a safe default literal
        for arg, default in zip(reversed(node.args.args), reversed(node.args.defaults)):
            if arg.arg == "host" and isinstance(default, ast.Constant):
                if default.value in ("127.0.0.1", "localhost", "::1"):
                    default_is_safe = True
        # Check function body for None -> localhost pattern
        func_lines = net_src.splitlines()[node.lineno-1:node.end_lineno]
        func_text = "\n".join(func_lines)
        if "127.0.0.1" in func_text or "localhost" in func_text:
            func_body_safe = True
        break

if default_is_safe or func_body_safe:
    # Default is safe — receiver calls are protected even without explicit host
    print("PASS: get_zmq_socket_on_host defaults to localhost, receiver calls are safe")
    sys.exit(0)

# Default is NOT safe — check that receiver call sites pass host explicitly
with open("/workspace/sglang/python/sglang/srt/disaggregation/encode_receiver.py") as f:
    recv_src = f.read()
recv_tree = ast.parse(recv_src)

calls_found = 0
calls_with_host = 0

for node in ast.walk(recv_tree):
    if isinstance(node, ast.Call):
        func = node.func
        name = None
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name == "get_zmq_socket_on_host":
            calls_found += 1
            has_host_kw = any(kw.arg == "host" for kw in node.keywords)
            has_3_plus_args = len(node.args) >= 3
            if has_host_kw or has_3_plus_args:
                calls_with_host += 1

if calls_found == 0:
    print("WARN: no calls found — function may have been refactored")
    sys.exit(0)
elif calls_with_host == calls_found:
    print(f"PASS: all {calls_found} calls pass host explicitly")
    sys.exit(0)
else:
    print(f"FAIL: {calls_with_host}/{calls_found} calls pass host, default is not safe")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural_receiver]=1; echo "structural_receiver: PASS"; else echo "structural_receiver: FAIL"; fi

# ---------- CONFIG-DERIVED (0.05): Safe default in function ----------
# [agent_config] (0.05): "Security-sensitive defaults" — python/sglang/multimodal_gen/.claude/CLAUDE.md
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/utils/network.py") as f:
    src = f.read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_zmq_socket_on_host":
        func_lines = src.splitlines()[node.lineno-1:node.end_lineno]
        func_src = "\n".join(func_lines)
        # Accept any localhost reference in the function body
        if "127.0.0.1" in func_src or "localhost" in func_src or "::1" in func_src:
            print("PASS: function references localhost")
            sys.exit(0)
        else:
            print("FAIL: no localhost reference in function")
            sys.exit(1)

print("FAIL: get_zmq_socket_on_host not found")
sys.exit(1)
PYEOF
# WHY AST: verifying function-level default pattern — behavioral test already covers runtime
if [ $? -eq 0 ]; then RESULTS[config_safe_default]=1; echo "config_safe_default: PASS"; else echo "config_safe_default: FAIL"; fi

# ---------- ANTI-STUB (0.05): Files not hollowed out ----------
# [pr_diff] (0.05): Files are not stubbed out
python3 << 'PYEOF'
import sys

min_lines = {
    "/workspace/sglang/python/sglang/srt/utils/network.py": 150,
    "/workspace/sglang/python/sglang/multimodal_gen/runtime/scheduler_client.py": 30,
    "/workspace/sglang/python/sglang/srt/disaggregation/encode_receiver.py": 500,
}

for fpath, threshold in min_lines.items():
    with open(fpath) as f:
        lines = len(f.readlines())
    if lines < threshold:
        print(f"FAIL: {fpath} only has {lines} lines (expected >= {threshold})")
        sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "antistub: PASS"; else echo "antistub: FAIL"; fi

# ---------- COMPUTE SCORE ----------
SCORE="0.0"
for key in "${!WEIGHTS[@]}"; do
    if [ "${RESULTS[$key]}" -eq 1 ]; then
        SCORE=$(python3 -c "print(round($SCORE + ${WEIGHTS[$key]}, 4))")
    fi
done

echo ""
echo "=== FINAL SCORE ==="
for key in behav_f2p_default p2p_explicit_host p2p_explicit_wild structural_broker structural_no_wildcard structural_receiver config_safe_default antistub; do
    STATUS="FAIL"
    if [ "${RESULTS[$key]}" -eq 1 ]; then STATUS="PASS"; fi
    echo "  $key (${WEIGHTS[$key]}): $STATUS"
done
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
