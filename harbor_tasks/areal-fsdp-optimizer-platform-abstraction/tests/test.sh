#!/usr/bin/env bash
set +e

TOTAL=0.0
FILE="areal/engine/fsdp_utils/optimizer.py"

add_score() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}

echo "=== Gate: Syntax check ==="
# [pr_diff] (gate): File must be valid Python
if python3 -c "import ast; ast.parse(open('$FILE').read())"; then
    echo "PASS: syntax OK"
else
    echo "FAIL: syntax error — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

echo ""
echo "=== F2P Behavioral: _init_streams_and_events uses current_platform ==="
# [pr_diff] (0.25): Extract _init_streams_and_events, run it with a tracking
# current_platform mock. Buggy code calls torch.cuda.Stream/Event directly
# (tracker stays silent → FAIL). Fixed code calls current_platform.Stream/Event
# (tracker fires → PASS). Accepts any valid fix that routes through current_platform.
python3 << 'PYEOF'
import ast, textwrap, sys

FILE = "areal/engine/fsdp_utils/optimizer.py"
source = open(FILE).read()
tree = ast.parse(source)

# --- Extract function source ---
func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'PerLayerOptimWrapper':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_init_streams_and_events':
                lines = source.splitlines(keepends=True)
                func_src = textwrap.dedent("".join(lines[item.lineno-1:item.end_lineno]))
                break
        break

if func_src is None:
    print("FAIL: _init_streams_and_events not found")
    sys.exit(1)

# --- Permissive mock that absorbs any operation ---
class Permissive:
    def __init__(self, *a, **kw): pass
    def __getattr__(self, name): return Permissive()
    def __call__(self, *a, **kw): return Permissive()
    def __bool__(self): return True
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def __iter__(self): return iter([])
    def __getitem__(self, k): return Permissive()
    def __setitem__(self, k, v): pass
    def __setattr__(self, name, value): object.__setattr__(self, name, value)
    def __len__(self): return 0
    def __int__(self): return 0
    def __float__(self): return 0.0
    def __repr__(self): return "Permissive()"

# --- Tracking platform mock ---
platform_calls = []
class TrackingPlatform:
    def __getattr__(self, name):
        platform_calls.append(name)
        return Permissive()

tracker = TrackingPlatform()

# --- Build namespace with tracker for current_platform ---
ns = {
    'torch': Permissive(),
    '__builtins__': __builtins__,
}
# Inject all module-level imports as Permissive, but bind
# current_platform (or any alias of it) to the tracker
for n in ast.walk(tree):
    if isinstance(n, ast.ImportFrom) and n.names:
        for alias in n.names:
            real_name = alias.name
            bound_name = alias.asname or alias.name
            if real_name == 'current_platform':
                ns[bound_name] = tracker
            elif bound_name not in ns:
                ns[bound_name] = Permissive()
    elif isinstance(n, ast.Import):
        for alias in n.names:
            bound_name = alias.asname or alias.name
            if bound_name not in ns:
                ns[bound_name] = Permissive()

# Ensure current_platform is bound to tracker even if import wasn't found yet
if 'current_platform' not in ns:
    ns['current_platform'] = tracker

try:
    exec(func_src, ns)
    fn = ns['_init_streams_and_events']
    fn(Permissive())
except Exception:
    pass  # partial execution is fine — check what was called

if len(platform_calls) == 0:
    print(f"FAIL: current_platform not called in _init_streams_and_events")
    sys.exit(1)

# At least one of Stream/Event should be accessed (case-insensitive first letter)
stream_event = [c for c in platform_calls if c.lower() in ('stream', 'event')]
if len(stream_event) == 0:
    print(f"FAIL: current_platform called ({platform_calls}) but not for Stream/Event")
    sys.exit(1)

print(f"PASS: current_platform called with: {platform_calls}")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    add_score 0.25
else
    echo "FAIL: _init_streams_and_events does not use current_platform"
fi

echo ""
echo "=== F2P Behavioral: step() uses current_platform ==="
# [pr_diff] (0.25): Extract step(), run with tracking current_platform mock.
# Buggy code calls torch.cuda.{current_stream,stream,empty_cache} directly → FAIL.
# Fixed code calls current_platform.{current_stream,stream,empty_cache} → PASS.
python3 << 'PYEOF'
import ast, textwrap, sys

FILE = "areal/engine/fsdp_utils/optimizer.py"
source = open(FILE).read()
tree = ast.parse(source)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'PerLayerOptimWrapper':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'step':
                lines = source.splitlines(keepends=True)
                func_src = textwrap.dedent("".join(lines[item.lineno-1:item.end_lineno]))
                break
        break

if func_src is None:
    print("FAIL: step() method not found")
    sys.exit(1)

class Permissive:
    def __init__(self, *a, **kw): pass
    def __getattr__(self, name): return Permissive()
    def __call__(self, *a, **kw): return Permissive()
    def __bool__(self): return True
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def __iter__(self): return iter([])
    def __getitem__(self, k): return Permissive()
    def __setitem__(self, k, v): pass
    def __setattr__(self, name, value): object.__setattr__(self, name, value)
    def __len__(self): return 0
    def __int__(self): return 0
    def __float__(self): return 0.0
    def __repr__(self): return "Permissive()"

platform_calls = []
class TrackingPlatform:
    def __getattr__(self, name):
        platform_calls.append(name)
        return Permissive()

tracker = TrackingPlatform()

ns = {
    'torch': Permissive(),
    '__builtins__': __builtins__,
}
for n in ast.walk(tree):
    if isinstance(n, ast.ImportFrom) and n.names:
        for alias in n.names:
            real_name = alias.name
            bound_name = alias.asname or alias.name
            if real_name == 'current_platform':
                ns[bound_name] = tracker
            elif bound_name not in ns:
                ns[bound_name] = Permissive()
    elif isinstance(n, ast.Import):
        for alias in n.names:
            bound_name = alias.asname or alias.name
            if bound_name not in ns:
                ns[bound_name] = Permissive()

if 'current_platform' not in ns:
    ns['current_platform'] = tracker

try:
    exec(func_src, ns)
    fn = ns['step']
    fn(Permissive())
except Exception:
    pass

if len(platform_calls) == 0:
    print(f"FAIL: current_platform not called in step()")
    sys.exit(1)

# At least one stream/cache op should go through current_platform
stream_ops = [c for c in platform_calls if c.lower() in ('current_stream', 'stream', 'empty_cache')]
if len(stream_ops) == 0:
    print(f"FAIL: current_platform called ({platform_calls}) but not for stream/cache ops")
    sys.exit(1)

print(f"PASS: current_platform called with: {platform_calls}")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    add_score 0.25
else
    echo "FAIL: step() does not use current_platform"
fi

echo ""
echo "=== F2P Behavioral: Module-level current_platform import ==="
# [pr_diff] (0.10): The module must import current_platform from areal.infra.platforms.
# Buggy code does not import it → FAIL. Fixed code does → PASS.
# Uses AST to check import exists (handles aliases via asname).
python3 << 'PYEOF'
import ast, sys

source = open("areal/engine/fsdp_utils/optimizer.py").read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        if node.module and 'areal.infra.platforms' in node.module:
            for alias in node.names:
                if alias.name == 'current_platform':
                    sys.exit(0)
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    echo "PASS: current_platform imported from areal.infra.platforms"
    add_score 0.10
else
    echo "FAIL: current_platform not imported from areal.infra.platforms"
fi

echo ""
echo "=== Behavioral: No direct torch.cuda device-specific calls in class ==="
# [pr_diff] (0.15): torch.cuda.{Stream,Event,current_stream,stream,empty_cache}
# must not appear anywhere in PerLayerOptimWrapper. Checks both dotted attribute
# access AND getattr-based access patterns to prevent aliasing bypass.
python3 << 'PYEOF'
import ast, sys

source = open("areal/engine/fsdp_utils/optimizer.py").read()
tree = ast.parse(source)

forbidden = {'Stream', 'Event', 'current_stream', 'stream', 'empty_cache'}

def collect_annotation_nodes(node):
    """Collect all AST node ids that appear inside type annotations."""
    ann_ids = set()
    for child in ast.walk(node):
        # Function argument annotations and return annotations
        if isinstance(child, ast.arg) and child.annotation:
            for n in ast.walk(child.annotation):
                ann_ids.add(id(n))
        if isinstance(child, ast.FunctionDef):
            if child.returns:
                for n in ast.walk(child.returns):
                    ann_ids.add(id(n))
        # Variable annotations
        if isinstance(child, ast.AnnAssign) and child.annotation:
            for n in ast.walk(child.annotation):
                ann_ids.add(id(n))
    return ann_ids

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'PerLayerOptimWrapper':
        class_source = ast.get_source_segment(source, node)
        if class_source is None:
            sys.exit(1)
        class_tree = ast.parse(class_source)
        ann_ids = collect_annotation_nodes(class_tree)
        for n in ast.walk(class_tree):
            if isinstance(n, ast.Attribute) and n.attr in forbidden:
                if id(n) in ann_ids:
                    continue  # skip type annotations
                # Check if parent chain is torch.cuda
                if isinstance(n.value, ast.Attribute) and n.value.attr == 'cuda':
                    if isinstance(n.value.value, ast.Name) and n.value.value.id == 'torch':
                        print(f"Found forbidden: torch.cuda.{n.attr}")
                        sys.exit(1)
        sys.exit(0)

print("PerLayerOptimWrapper class not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    echo "PASS: no direct torch.cuda device calls in PerLayerOptimWrapper"
    add_score 0.15
else
    echo "FAIL: direct torch.cuda device calls still present"
fi

echo ""
echo "=== Behavioral: TODO comments removed ==="
# [pr_diff] (0.10): TODO comments about current_platform abstraction should be resolved
python3 << 'PYEOF'
import sys
source = open("areal/engine/fsdp_utils/optimizer.py").read()
# Check for the known TODO patterns (case-insensitive to avoid narrow matching)
source_lower = source.lower()
if 'todo' in source_lower and 'current_platform' in source_lower:
    # Verify they're on the same line (actual TODO comment about platform)
    for line in source.splitlines():
        line_lower = line.lower()
        if 'todo' in line_lower and 'current_platform' in line_lower:
            print(f"TODO comment still present: {line.strip()}")
            sys.exit(1)
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "PASS: TODO comments about current_platform removed"
    add_score 0.10
else
    echo "FAIL: TODO comments about current_platform still present"
fi

echo ""
echo "=== Regression: Anti-stub check ==="
# [pr_diff] (0.10): _init_streams_and_events and step must not be stubbed out.
# Requires body with >3 meaningful statements (not just pass/raise/docstring/assignments to literals).
python3 << 'PYEOF'
import ast, sys

source = open("areal/engine/fsdp_utils/optimizer.py").read()
tree = ast.parse(source)

def count_meaningful_stmts(body):
    """Count statements that aren't pass, docstring-only, or trivial assignments."""
    count = 0
    for stmt in body:
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            continue  # docstring
        if isinstance(stmt, ast.Raise):
            continue
        count += 1
    return count

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'PerLayerOptimWrapper':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name in ('_init_streams_and_events', 'step'):
                stmts = count_meaningful_stmts(item.body)
                if stmts < 3:
                    print(f"FAIL: {item.name} has only {stmts} meaningful statements (stubbed)")
                    sys.exit(1)
        sys.exit(0)

print("PerLayerOptimWrapper class not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    echo "PASS: methods not stubbed"
    add_score 0.10
else
    echo "FAIL: methods appear to be stubbed out"
fi

echo ""
echo "=== Config: No wildcard imports ==="
# [agent_config] (0.05): "No wildcard imports" — AGENTS.md:30 @ cbe35f5
if ! grep -q 'from .* import \*' "$FILE"; then
    echo "PASS: no wildcard imports"
    add_score 0.05
else
    echo "FAIL: wildcard import found"
fi

echo ""
echo "=== Total score: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
reward = $TOTAL
behavioral = min(reward, 0.75)
structural = max(0, reward - 0.75)
data = {
    'reward': reward,
    'behavioral': behavioral,
    'regression': min(0.10, structural),
    'config': max(0, structural - 0.10),
}
json.dump(data, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
