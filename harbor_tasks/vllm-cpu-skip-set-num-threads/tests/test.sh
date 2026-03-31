#!/usr/bin/env bash
set +e

TARGET="/workspace/vllm/vllm/v1/worker/cpu_worker.py"
SCORE=0

add_score() {
    SCORE=$(python3 -c "print(round($SCORE + $1, 4))")
}

echo "=== GATE: Syntax check ==="
# [pr_diff] (0.00): cpu_worker.py must be valid Python
if ! python3 -c "
import ast, sys
try:
    ast.parse(open('$TARGET').read())
except SyntaxError as e:
    print(f'Syntax error: {e}'); sys.exit(1)
"; then
    echo "FAIL: syntax error — aborting"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "PASS: syntax ok"

# --- Extract monkey-patch code via AST (name-independent) ---
# Searches init_device for any reassignment of torch.set_num_threads,
# regardless of replacement function name, lambda, or setattr style.
echo ""
echo "=== Extracting patch code ==="
python3 << 'PYEOF'
import ast, textwrap, sys, json

TARGET = "/workspace/vllm/vllm/v1/worker/cpu_worker.py"
with open(TARGET) as f:
    source = f.read()
src_lines = source.splitlines(keepends=True)
tree = ast.parse(source)

meta = {"status": "fail", "init_env_line": -1, "patch_line": -1}

# Find CPUWorker.init_device
init_device = None
cpu_worker_cls = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CPUWorker":
        cpu_worker_cls = node
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "init_device":
                init_device = item
                break

if not init_device:
    with open("/tmp/patch_meta.json", "w") as f:
        meta["reason"] = "no_init_device"
        json.dump(meta, f)
    open("/tmp/patch_code.py", "w").close()
    print("init_device not found")
    sys.exit(0)

# Locate init_cpu_threads_env call line
for lineno in range(init_device.lineno, init_device.end_lineno + 1):
    if lineno <= len(src_lines) and "init_cpu_threads_env" in src_lines[lineno - 1]:
        meta["init_env_line"] = lineno
        break

def is_set_num_threads_assign(node):
    """Check if node assigns to torch.set_num_threads (direct or setattr)."""
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if (isinstance(t, ast.Attribute) and t.attr == "set_num_threads"
                    and isinstance(t.value, ast.Name) and t.value.id == "torch"):
                return True
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        func = node.value.func
        if isinstance(func, ast.Name) and func.id == "setattr":
            args = node.value.args
            if (len(args) >= 3
                    and isinstance(args[0], ast.Name) and args[0].id == "torch"
                    and isinstance(args[1], ast.Constant) and args[1].value == "set_num_threads"):
                return True
    return False

# Search for patch: first in init_device, then in the class, then module-level
search_scopes = [init_device]
if cpu_worker_cls:
    search_scopes.append(cpu_worker_cls)
search_scopes.append(tree)

nodes = []
has_patch = False
search_root = None

for scope in search_scopes:
    candidate_nodes = []
    found = False
    for node in ast.walk(scope):
        if isinstance(node, ast.FunctionDef) and node is not init_device and node is not scope:
            candidate_nodes.append(node)
        if is_set_num_threads_assign(node):
            candidate_nodes.append(node)
            found = True
            meta["patch_line"] = node.lineno
    if found:
        nodes = candidate_nodes
        has_patch = True
        search_root = scope
        break

if not has_patch:
    with open("/tmp/patch_meta.json", "w") as f:
        meta["reason"] = "no_patch"
        json.dump(meta, f)
    open("/tmp/patch_code.py", "w").close()
    print("No torch.set_num_threads patch found")
    sys.exit(0)

# Sort by line, extract and dedent
nodes.sort(key=lambda n: n.lineno)
parts = []
for node in nodes:
    chunk = "".join(src_lines[node.lineno - 1 : node.end_lineno])
    parts.append(textwrap.dedent(chunk))

code = "\n".join(parts)
with open("/tmp/patch_code.py", "w") as f:
    f.write(code)

meta["status"] = "ok"
with open("/tmp/patch_meta.json", "w") as f:
    json.dump(meta, f)
print(f"OK: extracted {len(nodes)} nodes, patch at line {meta['patch_line']}")
PYEOF

echo ""
echo "=== Behavioral: torch.set_num_threads becomes no-op ==="
# [pr_diff] (0.35): After monkey-patch, calling torch.set_num_threads must not change thread count
python3 << 'PYEOF'
import torch, logging, sys, json, os

if not os.path.exists("/tmp/patch_code.py") or os.path.getsize("/tmp/patch_code.py") == 0:
    print("FAIL: no patch code extracted")
    sys.exit(1)

with open("/tmp/patch_meta.json") as f:
    meta = json.load(f)
if meta["status"] != "ok":
    print(f"FAIL: extraction failed ({meta.get('reason', 'unknown')})")
    sys.exit(1)

with open("/tmp/patch_code.py") as f:
    code = f.read()

logger = logging.getLogger("vllm.worker.cpu_worker")
original_set = torch.set_num_threads

try:
    exec(code, {"torch": torch, "logger": logger, "__builtins__": __builtins__,
                "logging": logging})
except Exception as e:
    print(f"FAIL: patch code raised: {e}")
    torch.set_num_threads = original_set
    sys.exit(1)

# Behavioral: thread count must not change after patch
orig_count = torch.get_num_threads()
torch.set_num_threads(orig_count + 4)
after = torch.get_num_threads()
torch.set_num_threads = original_set

if after == orig_count:
    print(f"PASS: torch.set_num_threads is a no-op (threads stayed at {orig_count})")
else:
    print(f"FAIL: thread count changed from {orig_count} to {after}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then add_score 0.35; else echo "FAIL"; fi

echo ""
echo "=== Behavioral: warning logged on set_num_threads call ==="
# [pr_diff] (0.20): Patched set_num_threads must emit a log message when called
python3 << 'PYEOF'
import torch, logging, io, sys, json, os

if not os.path.exists("/tmp/patch_code.py") or os.path.getsize("/tmp/patch_code.py") == 0:
    print("FAIL: no patch code"); sys.exit(1)
with open("/tmp/patch_meta.json") as f:
    meta = json.load(f)
if meta["status"] != "ok":
    print("FAIL: extraction failed"); sys.exit(1)
with open("/tmp/patch_code.py") as f:
    code = f.read()

# Capture log output
log_buf = io.StringIO()
handler = logging.StreamHandler(log_buf)
handler.setLevel(logging.DEBUG)
logger = logging.getLogger("vllm.cpu_worker.warn_" + str(os.getpid()))
logger.handlers.clear()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.propagate = False

original_set = torch.set_num_threads
try:
    exec(code, {"torch": torch, "logger": logger, "__builtins__": __builtins__,
                "logging": logging})
except Exception:
    torch.set_num_threads = original_set
    print("FAIL: patch code raised"); sys.exit(1)

# Trigger the patched function
torch.set_num_threads(2)
torch.set_num_threads(8)
output = log_buf.getvalue()
torch.set_num_threads = original_set

if output.strip():
    print(f"PASS: log emitted: {output.strip()[:100]}")
else:
    print("FAIL: no log output when calling patched set_num_threads")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then add_score 0.20; else echo "FAIL"; fi

echo ""
echo "=== Behavioral: patched function handles various inputs ==="
# [pr_diff] (0.15): Replacement must handle various thread-count arguments without crashing
python3 << 'PYEOF'
import torch, logging, sys, os, json

if not os.path.exists("/tmp/patch_code.py") or os.path.getsize("/tmp/patch_code.py") == 0:
    print("FAIL: no patch code"); sys.exit(1)
with open("/tmp/patch_meta.json") as f:
    meta = json.load(f)
if meta["status"] != "ok":
    print("FAIL: extraction failed"); sys.exit(1)
with open("/tmp/patch_code.py") as f:
    code = f.read()

logger = logging.getLogger("vllm.cpu_worker.robust")
original_set = torch.set_num_threads
try:
    exec(code, {"torch": torch, "logger": logger, "__builtins__": __builtins__,
                "logging": logging})
except Exception:
    torch.set_num_threads = original_set
    print("FAIL: patch code raised"); sys.exit(1)

# Call with various values — must not crash and must preserve thread count
baseline = torch.get_num_threads()
for arg in [1, 2, 4, 8, 16, 32]:
    try:
        torch.set_num_threads(arg)
    except Exception as e:
        torch.set_num_threads = original_set
        print(f"FAIL: patched set_num_threads({arg}) raised: {e}")
        sys.exit(1)

final = torch.get_num_threads()
torch.set_num_threads = original_set

if final == baseline:
    print(f"PASS: handled 6 different args, threads stable at {final}")
else:
    print(f"FAIL: thread count drifted from {baseline} to {final}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then add_score 0.15; else echo "FAIL"; fi

echo ""
echo "=== Pass-to-pass: CPUWorker.init_device exists ==="
# [pr_diff] (0.10): CPUWorker class and init_device method must still exist
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/v1/worker/cpu_worker.py") as f:
    tree = ast.parse(f.read())

found_class = found_method = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CPUWorker":
        found_class = True
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "init_device":
                found_method = True

if not found_class:
    print("FAIL: CPUWorker class not found"); sys.exit(1)
if not found_method:
    print("FAIL: init_device method not found"); sys.exit(1)
print("PASS: CPUWorker.init_device exists")
PYEOF
if [ $? -eq 0 ]; then add_score 0.10; else echo "FAIL"; fi

echo ""
echo "=== Pass-to-pass: key init_device functionality preserved ==="
# [pr_diff] (0.10): Distributed init and seed setting must remain in the file
python3 << 'PYEOF'
import sys

with open("/workspace/vllm/vllm/v1/worker/cpu_worker.py") as f:
    content = f.read()

for pattern, desc in [
    ("init_worker_distributed_environment", "distributed init"),
    ("set_random_seed", "random seed setting"),
]:
    if pattern not in content:
        print(f"FAIL: {desc} ({pattern}) missing"); sys.exit(1)

print("PASS: key init_device functionality preserved")
PYEOF
if [ $? -eq 0 ]; then add_score 0.10; else echo "FAIL"; fi

echo ""
echo "=== Structural: patch placement after init_cpu_threads_env ==="
# [pr_diff] (0.10): Monkey-patch must come after init_cpu_threads_env in source order
python3 << 'PYEOF'
import json, sys

with open("/tmp/patch_meta.json") as f:
    meta = json.load(f)

if meta["status"] != "ok":
    print("FAIL: no patch found"); sys.exit(1)

init_line = meta.get("init_env_line", -1)
patch_line = meta.get("patch_line", -1)

if init_line < 0:
    # init_cpu_threads_env might have been refactored; skip this check gracefully
    print("SKIP: init_cpu_threads_env not found (may be refactored)")
    sys.exit(1)
if patch_line < 0:
    print("FAIL: patch line unknown"); sys.exit(1)

if patch_line > init_line:
    print(f"PASS: patch (L{patch_line}) after init_cpu_threads_env (L{init_line})")
else:
    print(f"FAIL: patch (L{patch_line}) must come after init_cpu_threads_env (L{init_line})")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then add_score 0.10; else echo "FAIL"; fi

echo ""
echo "=== Final Score ==="
echo "Score: $SCORE"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
