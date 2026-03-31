#!/usr/bin/env bash
set +e

BASE="/workspace/prime-rl/src/prime_rl"
CONFIG_PY="$BASE/utils/config.py"
RL_PY="$BASE/entrypoints/rl.py"
SFT_PY="$BASE/entrypoints/sft.py"
INFERENCE_PY="$BASE/entrypoints/inference.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# Weight budget: behavioral=0.75 (F2P=0.55, P2P=0.10, behavioral-removal=0.10), structural=0.25
WEIGHTS[core_serialize]=0.40
WEIGHTS[helpers_gone]=0.15
WEIGHTS[entrypoints_clean]=0.10
WEIGHTS[p2p_get_all_fields]=0.10
WEIGHTS[config_no_try_except]=0.10
WEIGHTS[antistub]=0.15

for key in core_serialize helpers_gone entrypoints_clean p2p_get_all_fields config_no_try_except antistub; do
    RESULTS[$key]=0
done

# ========== GATE: Syntax check ==========
python3 -c "
import ast
for f in ['$CONFIG_PY','$RL_PY','$SFT_PY','$INFERENCE_PY']:
    ast.parse(open(f).read())
" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS: all files parse"

# ========== BEHAVIORAL F2P: Actual write_config produces clean TOML (0.40) ==========
# [pr_diff] (0.40): write_config must serialize configs without "None" strings
python3 << 'PYEOF'
import ast, sys, tempfile
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import tomli_w

CONFIG_PY = "/workspace/prime-rl/src/prime_rl/utils/config.py"
SFT_PY = "/workspace/prime-rl/src/prime_rl/entrypoints/sft.py"

# Step 1: Extract helper functions from config.py (none_to_none_str if still present)
with open(CONFIG_PY) as f:
    config_src = f.read()
config_tree = ast.parse(config_src)
helpers = {"__builtins__": __builtins__}
for node in ast.iter_child_nodes(config_tree):
    if isinstance(node, ast.FunctionDef) and node.name in ("none_to_none_str", "_convert_none"):
        func_src = "".join(config_src.splitlines(keepends=True)[node.lineno-1:node.end_lineno])
        exec(func_src, helpers)

# Step 2: Extract write_config from sft.py
with open(SFT_PY) as f:
    sft_src = f.read()
sft_tree = ast.parse(sft_src)
write_config_node = None
for node in ast.iter_child_nodes(sft_tree):
    if isinstance(node, ast.FunctionDef) and node.name == "write_config":
        write_config_node = node
        break

if write_config_node is None:
    print("FAIL: write_config not found in sft.py"); sys.exit(1)

func_src = "".join(sft_src.splitlines(keepends=True)[write_config_node.lineno-1:write_config_node.end_lineno])

# Provide dependencies — type annotation stubs and helpers from config.py
ns = {
    "tomli_w": tomli_w,
    "Path": Path,
    "set": set,
    "__builtins__": __builtins__,
}
for name in ("SFTConfig", "RLConfig", "InferenceConfig"):
    ns[name] = BaseModel
for k, v in helpers.items():
    if callable(v) and k != "__builtins__":
        ns[k] = v

exec(func_src, ns)
write_config = ns["write_config"]

# Step 3: Create test config with None values (including nested)
class SubConfig(BaseModel):
    enabled: bool = True
    threshold: Optional[float] = None

class TestConfig(BaseModel):
    name: str = "test"
    batch_size: int = 32
    learning_rate: Optional[float] = None
    optional_field: Optional[str] = None
    sub: SubConfig = SubConfig()

config = TestConfig()
tmpdir = tempfile.mkdtemp()
config_path = Path(tmpdir) / "config.toml"

# Step 4: Call the actual extracted write_config
try:
    write_config(config, config_path)
except Exception as e:
    print(f"FAIL: write_config raised: {e}"); sys.exit(1)

# Step 5: Read and check TOML output
with open(config_path) as f:
    content = f.read()

# No "None" strings in TOML output (the core bug)
if '"None"' in content or "'None'" in content or "= None" in content:
    print(f"FAIL: TOML contains None strings:\n{content}"); sys.exit(1)

# None-valued fields must be excluded, not serialized
if "learning_rate" in content:
    print(f"FAIL: None-valued 'learning_rate' present in TOML"); sys.exit(1)
if "optional_field" in content:
    print(f"FAIL: None-valued 'optional_field' present in TOML"); sys.exit(1)
if "threshold" in content:
    print(f"FAIL: Nested None-valued 'threshold' present in TOML"); sys.exit(1)

# Non-None fields must be preserved
if "name" not in content or "batch_size" not in content:
    print(f"FAIL: Non-None fields missing from TOML:\n{content}"); sys.exit(1)
if "enabled" not in content:
    print(f"FAIL: Nested non-None field 'enabled' missing from TOML"); sys.exit(1)

print("PASS: write_config produces clean TOML without None strings")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[core_serialize]=1 && echo "TEST core_serialize: PASS" || echo "TEST core_serialize: FAIL"

# ========== BEHAVIORAL F2P: none_to_none_str helper removed from config.py (0.15) ==========
# [pr_diff] (0.15): Custom None-to-string helpers must be removed
python3 << 'PYEOF'
import ast, sys

CONFIG_PY = "/workspace/prime-rl/src/prime_rl/utils/config.py"
with open(CONFIG_PY) as f:
    src = f.read()
tree = ast.parse(src)

# Check via AST that the helper functions are truly gone (not just renamed/commented)
bad_funcs = []
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name in ("none_to_none_str", "_convert_none"):
        bad_funcs.append(node.name)

if bad_funcs:
    print(f"FAIL: helper functions still defined: {bad_funcs}"); sys.exit(1)

# Verify get_all_fields wasn't accidentally removed
found = any(
    isinstance(node, ast.FunctionDef) and node.name == "get_all_fields"
    for node in ast.iter_child_nodes(tree)
)
if not found:
    print("FAIL: get_all_fields was accidentally removed"); sys.exit(1)

print("PASS: none_to_none_str/_convert_none removed, get_all_fields preserved")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[helpers_gone]=1 && echo "TEST helpers_gone: PASS" || echo "TEST helpers_gone: FAIL"

# ========== BEHAVIORAL: Entrypoints don't call none_to_none_str (0.10) ==========
# [pr_diff] (0.10): All entrypoints must stop using the removed helper
python3 << 'PYEOF'
import ast, sys

entrypoints = {
    "rl.py": "/workspace/prime-rl/src/prime_rl/entrypoints/rl.py",
    "sft.py": "/workspace/prime-rl/src/prime_rl/entrypoints/sft.py",
    "inference.py": "/workspace/prime-rl/src/prime_rl/entrypoints/inference.py",
}

for name, path in entrypoints.items():
    with open(path) as f:
        src = f.read()
    tree = ast.parse(src)

    # Check via AST that none_to_none_str is not called (handles aliases too)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "none_to_none_str":
                print(f"FAIL: {name} still calls none_to_none_str"); sys.exit(1)
            if isinstance(func, ast.Attribute) and func.attr == "none_to_none_str":
                print(f"FAIL: {name} still calls none_to_none_str"); sys.exit(1)

    # Check that none_to_none_str is not imported
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "none_to_none_str":
                    print(f"FAIL: {name} still imports none_to_none_str"); sys.exit(1)

print("PASS: no entrypoint calls or imports none_to_none_str")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[entrypoints_clean]=1 && echo "TEST entrypoints_clean: PASS" || echo "TEST entrypoints_clean: FAIL"

# ========== P2P BEHAVIORAL: get_all_fields still works (0.10) ==========
# [repo_tests] (0.10): pass-to-pass — get_all_fields must still be callable and correct
python3 << 'PYEOF'
import ast, sys
from pydantic import BaseModel
from typing import Optional

CONFIG_PY = "/workspace/prime-rl/src/prime_rl/utils/config.py"
with open(CONFIG_PY) as f:
    src = f.read()
tree = ast.parse(src)

func_src = None
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_all_fields":
        func_src = "".join(src.splitlines(keepends=True)[node.lineno-1:node.end_lineno])
        break

if func_src is None:
    print("FAIL: get_all_fields not found"); sys.exit(1)

ns = {"BaseModel": BaseModel, "__builtins__": __builtins__}
exec(func_src, ns)
get_all_fields = ns["get_all_fields"]

class MyModel(BaseModel):
    name: str = "test"
    value: int = 42
    optional: Optional[float] = None

# Test with class
fields = get_all_fields(MyModel)
if "name" not in fields or "value" not in fields:
    print(f"FAIL: get_all_fields(class) returned {fields}"); sys.exit(1)

# Test with instance
fields2 = get_all_fields(MyModel())
if "name" not in fields2 or "value" not in fields2:
    print(f"FAIL: get_all_fields(instance) returned {fields2}"); sys.exit(1)

print("PASS: get_all_fields works correctly")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[p2p_get_all_fields]=1 && echo "TEST p2p_get_all_fields: PASS" || echo "TEST p2p_get_all_fields: FAIL"

# ========== CONFIG: No unnecessary try/except in config.py (0.10) ==========
# [agent_config] (0.10): "Avoid try/except blocks unless really necessary" — AGENTS.md:5 @ 4f612601
python3 << 'PYEOF'
import ast, sys

with open("/workspace/prime-rl/src/prime_rl/utils/config.py") as f:
    tree = ast.parse(f.read())
try_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
if try_count > 0:
    print(f"FAIL: config.py has {try_count} try/except blocks"); sys.exit(1)

print("PASS: no unnecessary try/except in config.py")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[config_no_try_except]=1 && echo "TEST config_no_try_except: PASS" || echo "TEST config_no_try_except: FAIL"

# ========== STRUCTURAL: Anti-stub (0.15) ==========
# [pr_diff] (0.15): Changed files must not be stubbed out
python3 << 'PYEOF'
import sys

# config.py should have substantial content
with open("/workspace/prime-rl/src/prime_rl/utils/config.py") as f:
    lines = [l for l in f.read().strip().split("\n") if l.strip()]
if len(lines) < 5:
    print(f"FAIL: config.py has only {len(lines)} non-blank lines (stubbed)"); sys.exit(1)

# Entrypoints should still have write_config and tomli_w.dump
for name, path in [
    ("rl.py", "/workspace/prime-rl/src/prime_rl/entrypoints/rl.py"),
    ("sft.py", "/workspace/prime-rl/src/prime_rl/entrypoints/sft.py"),
    ("inference.py", "/workspace/prime-rl/src/prime_rl/entrypoints/inference.py"),
]:
    with open(path) as f:
        src = f.read()
    if "def write_config" not in src:
        print(f"FAIL: {name} missing write_config function (stubbed)"); sys.exit(1)
    if "tomli_w.dump" not in src:
        print(f"FAIL: {name} missing tomli_w.dump call (stubbed)"); sys.exit(1)

# rl.py should still have write_subconfigs
with open("/workspace/prime-rl/src/prime_rl/entrypoints/rl.py") as f:
    if "def write_subconfigs" not in f.read():
        print("FAIL: rl.py missing write_subconfigs (stubbed)"); sys.exit(1)

print("PASS: all files have expected content")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ========== SCORE ==========
SCORE=$(python3 -c "
w={
    'core_serialize':${WEIGHTS[core_serialize]},
    'helpers_gone':${WEIGHTS[helpers_gone]},
    'entrypoints_clean':${WEIGHTS[entrypoints_clean]},
    'p2p_get_all_fields':${WEIGHTS[p2p_get_all_fields]},
    'config_no_try_except':${WEIGHTS[config_no_try_except]},
    'antistub':${WEIGHTS[antistub]},
}
r={
    'core_serialize':${RESULTS[core_serialize]},
    'helpers_gone':${RESULTS[helpers_gone]},
    'entrypoints_clean':${RESULTS[entrypoints_clean]},
    'p2p_get_all_fields':${RESULTS[p2p_get_all_fields]},
    'config_no_try_except':${RESULTS[config_no_try_except]},
    'antistub':${RESULTS[antistub]},
}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
