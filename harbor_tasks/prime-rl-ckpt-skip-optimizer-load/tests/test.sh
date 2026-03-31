#!/usr/bin/env bash
set +e

BASE="/workspace/prime-rl/src/prime_rl"
CONFIG_PY="$BASE/configs/trainer.py"
CKPT_PY="$BASE/trainer/ckpt.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# Weight budget: behavioral=0.60, regression=0.10, structural=0.30
WEIGHTS[config_field_exists]=0.20
WEIGHTS[config_default_false]=0.15
WEIGHTS[config_accepts_true]=0.15
WEIGHTS[config_consistent]=0.10
WEIGHTS[p2p_existing_fields]=0.10
WEIGHTS[ckpt_conditional_skip]=0.15
WEIGHTS[ckpt_stores_flag]=0.05
WEIGHTS[antistub]=0.05
WEIGHTS[config_no_try_except]=0.05

for key in config_field_exists config_default_false config_accepts_true config_consistent p2p_existing_fields ckpt_conditional_skip ckpt_stores_flag antistub config_no_try_except; do
    RESULTS[$key]=0
done

# ========== Shared config loader ==========
cat > /tmp/load_config.py << 'PYEOF'
from pydantic import BaseModel, Field, model_validator
from typing import Annotated, Literal, Any, TypeAlias
from pathlib import Path

class BaseConfig(BaseModel):
    pass

class BaseModelConfig(BaseConfig):
    name: str = "stub"
    trust_remote_code: bool = False

def load_checkpoint_config():
    ns = {
        "BaseModel": BaseModel, "BaseConfig": BaseConfig, "BaseModelConfig": BaseModelConfig,
        "Field": Field, "Annotated": Annotated, "Literal": Literal, "Any": Any,
        "TypeAlias": TypeAlias, "Path": Path, "model_validator": model_validator,
        "__name__": "__main__",
    }
    with open("/workspace/prime-rl/src/prime_rl/configs/trainer.py") as f:
        src = f.read()
    lines = src.split("\n")
    clean = []
    skip = False
    for line in lines:
        if "from prime_rl." in line:
            skip = True
            continue
        if skip and (line.startswith("    ") or line.startswith(")")):
            if line.strip() == ")":
                skip = False
            continue
        skip = False
        clean.append(line)
    try:
        exec(compile("\n".join(clean), "trainer.py", "exec"), ns)
    except Exception:
        pass
    return ns.get("CheckpointConfig")
PYEOF

# ========== GATE: Syntax check ==========
python3 -c "
import ast
for f in ['$CONFIG_PY','$CKPT_PY']:
    ast.parse(open(f).read())
" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS: all files parse"

# ========== BEHAVIORAL F2P: CheckpointConfig has skip_optimizer field (0.20) ==========
# [pr_diff] (0.20): CheckpointConfig must have a boolean field for skipping optimizer loading
python3 << 'PYEOF'
import sys, typing
sys.path.insert(0, '/tmp')
from load_config import load_checkpoint_config

Cfg = load_checkpoint_config()
if Cfg is None:
    print("FAIL: CheckpointConfig not found"); sys.exit(1)

fields = Cfg.model_fields
if "skip_optimizer" not in fields:
    print(f"FAIL: skip_optimizer not in fields: {list(fields.keys())}"); sys.exit(1)

ann = fields["skip_optimizer"].annotation
origin = getattr(ann, '__origin__', None)
if ann is not bool:
    if origin is not None:
        args = getattr(ann, '__args__', ())
        if not args or args[0] is not bool:
            print(f"FAIL: skip_optimizer base type is not bool, got {ann}"); sys.exit(1)
    else:
        print(f"FAIL: skip_optimizer is not bool, got {ann}"); sys.exit(1)

print("PASS: CheckpointConfig has skip_optimizer bool field")
PYEOF
[ $? -eq 0 ] && RESULTS[config_field_exists]=1 && echo "TEST config_field_exists: PASS" || echo "TEST config_field_exists: FAIL"

# ========== BEHAVIORAL F2P: skip_optimizer defaults to False (0.15) ==========
# [pr_diff] (0.15): skip_optimizer must default to False so existing behavior is preserved
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from load_config import load_checkpoint_config

Cfg = load_checkpoint_config()
if Cfg is None:
    print("FAIL: CheckpointConfig not found"); sys.exit(1)

cfg = Cfg()
if not hasattr(cfg, "skip_optimizer"):
    print("FAIL: no skip_optimizer attr on instance"); sys.exit(1)
if cfg.skip_optimizer is not False:
    print(f"FAIL: default is {cfg.skip_optimizer}, expected False"); sys.exit(1)

print("PASS: skip_optimizer defaults to False")
PYEOF
[ $? -eq 0 ] && RESULTS[config_default_false]=1 && echo "TEST config_default_false: PASS" || echo "TEST config_default_false: FAIL"

# ========== BEHAVIORAL F2P: skip_optimizer accepts True and serializes (0.15) ==========
# [pr_diff] (0.15): CheckpointConfig(skip_optimizer=True) must work and round-trip
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from load_config import load_checkpoint_config

Cfg = load_checkpoint_config()
if Cfg is None:
    print("FAIL: CheckpointConfig not found"); sys.exit(1)

cfg = Cfg(skip_optimizer=True)
if cfg.skip_optimizer is not True:
    print(f"FAIL: skip_optimizer={cfg.skip_optimizer} after setting True"); sys.exit(1)

dumped = cfg.model_dump()
if dumped.get("skip_optimizer") is not True:
    print(f"FAIL: model_dump skip_optimizer={dumped.get('skip_optimizer')}"); sys.exit(1)

# Round-trip: create from dumped dict
cfg2 = Cfg(**dumped)
if cfg2.skip_optimizer is not True:
    print(f"FAIL: round-trip skip_optimizer={cfg2.skip_optimizer}"); sys.exit(1)

print("PASS: skip_optimizer=True works and round-trips")
PYEOF
[ $? -eq 0 ] && RESULTS[config_accepts_true]=1 && echo "TEST config_accepts_true: PASS" || echo "TEST config_accepts_true: FAIL"

# ========== BEHAVIORAL F2P: Consistent with sibling skip_* fields (0.10) ==========
# [pr_diff] (0.10): New field follows same pattern as skip_progress, skip_scheduler, skip_dataloader
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from load_config import load_checkpoint_config

Cfg = load_checkpoint_config()
if Cfg is None:
    print("FAIL: CheckpointConfig not found"); sys.exit(1)

skip_fields = ["skip_progress", "skip_scheduler", "skip_dataloader", "skip_optimizer"]
cfg = Cfg()
for fname in skip_fields:
    if fname not in Cfg.model_fields:
        print(f"FAIL: {fname} missing from CheckpointConfig"); sys.exit(1)
    if getattr(cfg, fname) is not False:
        print(f"FAIL: {fname} default is not False"); sys.exit(1)

cfg2 = Cfg(**{f: True for f in skip_fields})
for fname in skip_fields:
    if getattr(cfg2, fname) is not True:
        print(f"FAIL: {fname} not True after setting"); sys.exit(1)

print("PASS: skip_optimizer follows sibling skip_* pattern")
PYEOF
[ $? -eq 0 ] && RESULTS[config_consistent]=1 && echo "TEST config_consistent: PASS" || echo "TEST config_consistent: FAIL"

# ========== REGRESSION P2P: Existing fields still work (0.10) ==========
# [repo_tests] (0.10): pass-to-pass — existing CheckpointConfig fields unchanged
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from load_config import load_checkpoint_config

Cfg = load_checkpoint_config()
if Cfg is None:
    print("FAIL: CheckpointConfig not found"); sys.exit(1)

cfg = Cfg(skip_progress=True, skip_scheduler=True, skip_dataloader=True)
assert cfg.skip_progress is True, "skip_progress broken"
assert cfg.skip_scheduler is True, "skip_scheduler broken"
assert cfg.skip_dataloader is True, "skip_dataloader broken"

cfg2 = Cfg(interval=5, keep_last=3)
assert cfg2.interval == 5, "interval field broken"
assert cfg2.keep_last == 3, "keep_last field broken"

print("PASS: existing CheckpointConfig fields still work")
PYEOF
[ $? -eq 0 ] && RESULTS[p2p_existing_fields]=1 && echo "TEST p2p_existing_fields: PASS" || echo "TEST p2p_existing_fields: FAIL"

# ========== STRUCTURAL: load_from_path has conditional skip logic (0.15) ==========
# [pr_diff] (0.15): load_from_path must conditionally pass empty optimizers when skip_optimizer is set
# WHY AST: load_from_path requires torch.distributed checkpoint infrastructure — cannot call on CPU
python3 << 'PYEOF'
import ast, sys

with open("/workspace/prime-rl/src/prime_rl/trainer/ckpt.py") as f:
    src = f.read()

tree = ast.parse(src)

def has_skip_optimizer_attr(node):
    """Check if any descendant is ast.Attribute with attr='skip_optimizer'."""
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute) and n.attr == "skip_optimizer":
            return True
    return False

def has_empty_collection(node):
    """Check if any descendant is an empty list [] or tuple ()."""
    for n in ast.walk(node):
        if isinstance(n, ast.List) and len(n.elts) == 0:
            return True
        if isinstance(n, ast.Tuple) and len(n.elts) == 0:
            return True
    return False

# Find load_from_path and verify it contains a conditional (IfExp or If)
# whose test references skip_optimizer (as an Attribute, not a string/comment)
# and whose branches include an empty collection (the [] replacing optimizers)
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "load_from_path":
        for child in ast.walk(node):
            # Pattern: optimizers if not self.skip_optimizer else []
            # or:      [] if self.skip_optimizer else optimizers
            if isinstance(child, ast.IfExp):
                if has_skip_optimizer_attr(child.test):
                    if has_empty_collection(child.body) or has_empty_collection(child.orelse):
                        found = True
                        break
            # Pattern: if self.skip_optimizer: optimizers = []
            elif isinstance(child, ast.If):
                if has_skip_optimizer_attr(child.test):
                    if has_empty_collection(child):
                        found = True
                        break
        break

if not found:
    print("FAIL: load_from_path has no conditional skip_optimizer logic with empty collection")
    sys.exit(1)

print("PASS: load_from_path conditionally skips optimizers via skip_optimizer")
PYEOF
[ $? -eq 0 ] && RESULTS[ckpt_conditional_skip]=1 && echo "TEST ckpt_conditional_skip: PASS" || echo "TEST ckpt_conditional_skip: FAIL"

# ========== STRUCTURAL: CheckpointManager references skip_optimizer (0.05) ==========
# [pr_diff] (0.05): CheckpointManager must store or access skip_optimizer from config
# WHY AST: class requires torch.distributed — cannot instantiate on CPU
python3 << 'PYEOF'
import ast, sys

with open("/workspace/prime-rl/src/prime_rl/trainer/ckpt.py") as f:
    src = f.read()

tree = ast.parse(src)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CheckpointManager":
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute) and child.attr == "skip_optimizer":
                found = True
                break
        break

if not found:
    print("FAIL: CheckpointManager does not reference skip_optimizer as attribute")
    sys.exit(1)

print("PASS: CheckpointManager references skip_optimizer")
PYEOF
[ $? -eq 0 ] && RESULTS[ckpt_stores_flag]=1 && echo "TEST ckpt_stores_flag: PASS" || echo "TEST ckpt_stores_flag: FAIL"

# ========== STRUCTURAL: Anti-stub (0.05) ==========
# [pr_diff] (0.05): Changed files must not be stubbed out
python3 << 'PYEOF'
import sys

for fpath, min_lines, must_contain in [
    ("/workspace/prime-rl/src/prime_rl/configs/trainer.py", 50,
     ["CheckpointConfig", "skip_progress", "skip_scheduler"]),
    ("/workspace/prime-rl/src/prime_rl/trainer/ckpt.py", 50,
     ["CheckpointManager", "load_from_path", "AppState"]),
]:
    with open(fpath) as f:
        content = f.read()
    lines = [l for l in content.strip().split("\n") if l.strip()]
    if len(lines) < min_lines:
        print(f"FAIL: {fpath} has only {len(lines)} non-blank lines (stubbed)")
        sys.exit(1)
    for token in must_contain:
        if token not in content:
            print(f"FAIL: {fpath} missing {token} (stubbed)")
            sys.exit(1)

print("PASS: files have expected content (not stubbed)")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ========== CONFIG: No unnecessary try/except in config file (0.05) ==========
# [agent_config] (0.05): "Avoid try/except blocks unless really necessary" — AGENTS.md:5 @ d8030652
python3 << 'PYEOF'
import ast, sys

with open("/workspace/prime-rl/src/prime_rl/configs/trainer.py") as f:
    tree = ast.parse(f.read())

try_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
if try_count > 0:
    print(f"FAIL: trainer.py has {try_count} try/except blocks")
    sys.exit(1)

print("PASS: no unnecessary try/except in configs/trainer.py")
PYEOF
[ $? -eq 0 ] && RESULTS[config_no_try_except]=1 && echo "TEST config_no_try_except: PASS" || echo "TEST config_no_try_except: FAIL"

# ========== SCORE ==========
SCORE=$(python3 -c "
w={
    'config_field_exists':${WEIGHTS[config_field_exists]},
    'config_default_false':${WEIGHTS[config_default_false]},
    'config_accepts_true':${WEIGHTS[config_accepts_true]},
    'config_consistent':${WEIGHTS[config_consistent]},
    'p2p_existing_fields':${WEIGHTS[p2p_existing_fields]},
    'ckpt_conditional_skip':${WEIGHTS[ckpt_conditional_skip]},
    'ckpt_stores_flag':${WEIGHTS[ckpt_stores_flag]},
    'antistub':${WEIGHTS[antistub]},
    'config_no_try_except':${WEIGHTS[config_no_try_except]},
}
r={
    'config_field_exists':${RESULTS[config_field_exists]},
    'config_default_false':${RESULTS[config_default_false]},
    'config_accepts_true':${RESULTS[config_accepts_true]},
    'config_consistent':${RESULTS[config_consistent]},
    'p2p_existing_fields':${RESULTS[p2p_existing_fields]},
    'ckpt_conditional_skip':${RESULTS[ckpt_conditional_skip]},
    'ckpt_stores_flag':${RESULTS[ckpt_stores_flag]},
    'antistub':${RESULTS[antistub]},
    'config_no_try_except':${RESULTS[config_no_try_except]},
}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
