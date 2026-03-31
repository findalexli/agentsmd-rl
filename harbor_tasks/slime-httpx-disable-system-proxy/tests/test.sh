#!/usr/bin/env bash
#
# Verification for slime-httpx-disable-system-proxy
# Tests that httpx.AsyncClient instances ignore system proxy settings.
#
# Checks:
# - [pr_diff] (0.40): init_http_client returns AsyncClient with trust_env=False
# - [pr_diff] (0.40): Ray actor's _HttpPosterActor creates AsyncClient with trust_env=False
# - [agent_config] (0.10): No wildcard imports - .claude/skills/add-tests-and-ci/SKILL.md
# - [agent_config] (0.10): No bare print() - .claude/skills/add-tests-and-ci/SKILL.md
#
set +e

TARGET="/workspace/slime/slime/utils/http_utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

pip install --quiet httpx 2>/dev/null

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.40
WEIGHTS[behavioral2]=0.40
WEIGHTS[config_no_wildcard]=0.10
WEIGHTS[config_no_bare_print]=0.10

for key in behavioral behavioral2 config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

# ---------- GATE: Python syntax validity ----------
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (40%): Behavioral - init_http_client ----------
python3 << 'PYEOF'
import sys
import os
import httpx

os.environ["HTTP_PROXY"] = "http://fake-proxy:8080"
os.environ["HTTPS_PROXY"] = "http://fake-proxy:8080"

sys.path.insert(0, "/workspace/slime")
from slime.utils.http_utils import init_http_client

client = init_http_client()

if not isinstance(client, httpx.AsyncClient):
    print("BEHAVIORAL FAIL: did not return AsyncClient")
    sys.exit(1)

if hasattr(client, "_trust_env") and client._trust_env:
    print("BEHAVIORAL FAIL: trust_env is True (should be False)")
    sys.exit(1)

print("BEHAVIORAL PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral]=1; fi

# ---------- PRIMARY 2 (40%): Behavioral - _HttpPosterActor ----------
python3 << 'PYEOF'
import sys
import os
import httpx
import types
import ast

os.environ["HTTP_PROXY"] = "http://fake-proxy:8080"
os.environ["HTTPS_PROXY"] = "http://fake-proxy:8080"

# Mock Ray before importing
sys.modules["ray"] = types.SimpleNamespace(
    get_runtime_context=lambda: types.SimpleNamespace(job_id="test"),
    get_gpu_ids=lambda: []
)
sys.modules["ray.util"] = types.ModuleType("ray.util")
sys.modules["ray.util.scheduling_strategies"] = types.ModuleType("scheduling_strategies")
sys.modules["ray.util.scheduling_strategies"].PlacementGroupSchedulingStrategy = object

sys.path.insert(0, "/workspace/slime")

# Parse and extract the _HttpPosterActor class
target_file = "/workspace/slime/slime/utils/http_utils.py"
with open(target_file) as f:
    source = f.read()

tree = ast.parse(source)

# Find _HttpPosterActor class - it's nested in _init_ray_distributed_post
actor_class_node = None
outer_func = None

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_init_ray_distributed_post":
        outer_func = node
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef) and "HttpPoster" in child.name:
                actor_class_node = child
                break
        break

if actor_class_node is None:
    print("BEHAVIORAL2 FAIL: _HttpPosterActor not found")
    sys.exit(1)

# Get lines for the class
lines = source.splitlines(keepends=True)
class_source = "".join(lines[actor_class_node.lineno-1:actor_class_node.end_lineno])

# Execute class definition in isolated namespace with required imports
namespace = {
    "httpx": httpx,
    "ray": sys.modules["ray"],
    "__builtins__": __builtins__,
}
exec(class_source, namespace)

ActorClass = None
for name, obj in namespace.items():
    if isinstance(obj, type) and "HttpPoster" in name:
        ActorClass = obj
        break

if ActorClass is None:
    print("BEHAVIORAL2 FAIL: Could not extract actor class")
    sys.exit(1)

# Try to instantiate - bypass __init__ issues by setting client manually first
class TestActor(ActorClass):
    def __init__(self):
        self.client = None
        try:
            super().__init__()
        except:
            pass
        # If client wasn't set, extract from AST what should be set
        if self.client is None:
            # Parse __init__ to find AsyncClient call
            for node in ast.walk(actor_class_node):
                if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Assign):
                            # Check if assigning to self.client
                            for target in subnode.targets:
                                if isinstance(target, ast.Attribute) and target.attr == "client":
                                    # Found self.client = ...
                                    if isinstance(subnode.value, ast.Call):
                                        call = subnode.value
                                        is_async_client = False
                                        if isinstance(call.func, ast.Attribute) and call.func.attr == "AsyncClient":
                                            is_async_client = True
                                        elif isinstance(call.func, ast.Name) and call.func.id == "AsyncClient":
                                            is_async_client = True

                                        if is_async_client:
                                            # Build kwargs from the AST
                                            kwargs = {}
                                            for kw in call.keywords:
                                                if isinstance(kw.value, ast.Constant):
                                                    if isinstance(kw.value.value, bool):
                                                        kwargs[kw.arg] = kw.value.value
                                                    else:
                                                        kwargs[kw.arg] = kw.value.value
                                                elif kw.arg == "trust_env":
                                                    kwargs[kw.arg] = False
                                            # Create client with those kwargs
                                            self.client = httpx.AsyncClient(**kwargs)
                                            break

if not hasattr(TestActor(), "client") or TestActor().client is None:
    print("BEHAVIORAL2 FAIL: could not determine client")
    sys.exit(1)

instance = TestActor()
if not isinstance(instance.client, httpx.AsyncClient):
    print("BEHAVIORAL2 FAIL: client is not AsyncClient")
    sys.exit(1)

if hasattr(instance.client, "_trust_env") and instance.client._trust_env:
    print("BEHAVIORAL2 FAIL: trust_env is True")
    sys.exit(1)

print("BEHAVIORAL2 PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral2]=1; fi

# ---------- Config-derived (10%): No wildcard imports ----------
python3 << 'PYEOF'
import ast, sys
with open("/workspace/slime/slime/utils/http_utils.py") as f:
    for node in ast.walk(ast.parse(f.read())):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    sys.exit(1)
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[config_no_wildcard]=1; fi

# ---------- Config-derived (10%): No bare print() ----------
python3 << 'PYEOF'
import ast, sys
with open("/workspace/slime/slime/utils/http_utils.py") as f:
    for node in ast.walk(ast.parse(f.read())):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            sys.exit(1)
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[config_no_bare_print]=1; fi

# ---------- SCORE ----------
python3 -c "
w = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral2': ${WEIGHTS[behavioral2]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
r = {'behavioral': ${RESULTS[behavioral]}, 'behavioral2': ${RESULTS[behavioral2]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
print(f'{{sum(w[k]*r[k] for k in w):.4f}}')
" > "$REWARD_FILE"

for key in behavioral behavioral2 config_no_wildcard config_no_bare_print; do
    echo "  $key: ${RESULTS[$key]} (weight ${WEIGHTS[$key]})"
done
echo "Final: $(cat $REWARD_FILE)"

source /tests/judge_hook.sh 2>/dev/null || true
