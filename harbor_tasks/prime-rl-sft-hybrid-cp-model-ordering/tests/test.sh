#!/usr/bin/env bash
set +e

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-/workspace}"
FILE="$REPO_ROOT/src/prime_rl/trainer/sft/train.py"
REWARD=0

echo "=== GATE: Syntax check ==="
# [pr_diff] (0.00): File must be valid Python
if ! python3 -c "import ast; ast.parse(open('$FILE').read())"; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
fi
echo "GATE PASSED"

echo ""
echo "=== F2P Behavioral: Execute train() with mocked deps — no NameError on model ==="
# [pr_diff] (0.40): The core bug: setup_hybrid_cp(model, ...) runs before model = setup_model().
# We exec the module with auto-mocked imports, call train(), and check for NameError.
# Buggy code: NameError because 'model' is referenced before assignment.
# Fixed code: model is assigned first, no NameError.
F2P_EXEC=$(timeout 30 python3 << 'PYEOF'
import sys, types
from unittest.mock import MagicMock

class _FallbackFinder:
    """Auto-mock any import that fails normally."""
    @staticmethod
    def find_module(name, path=None):
        return _FallbackFinder
    @staticmethod
    def load_module(name):
        if name not in sys.modules:
            m = MagicMock()
            m.__name__ = name
            m.__path__ = [name]
            m.__file__ = '<mock:' + name + '>'
            m.__loader__ = _FallbackFinder
            m.__package__ = name.rsplit('.', 1)[0] if '.' in name else name
            sys.modules[name] = m
        return sys.modules[name]

sys.meta_path.append(_FallbackFinder)
sys.path.insert(0, '/workspace/src')

import ast

FILE = '/workspace/src/prime_rl/trainer/sft/train.py'
source = open(FILE).read()

# Try exec-ing the whole module to populate namespace (including train def)
ns = {'__builtins__': __builtins__, '__name__': '__test__', '__file__': FILE}
try:
    exec(compile(source, FILE, 'exec'), ns)
except Exception:
    pass

# Fallback: extract train() via AST if whole-module exec didn't define it
if 'train' not in ns or not callable(ns.get('train')):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'train':
            lines = source.splitlines(keepends=True)
            func_src = ''.join(lines[node.lineno-1:node.end_lineno])
            try:
                exec(compile(func_src, FILE, 'exec'), ns)
            except Exception:
                pass
            break

train_fn = ns.get('train')
if train_fn is None or not callable(train_fn):
    print('SKIP')
    sys.exit(0)

config = MagicMock()
try:
    train_fn(config)
except NameError as e:
    if 'model' in str(e).lower():
        print('FAIL_NAMEERROR')
        sys.exit(0)
    # Other NameErrors from incomplete mocking — not our bug
except (SystemExit, KeyboardInterrupt):
    raise
except Exception:
    pass  # Other errors expected with mocked deps

print('PASS')
PYEOF
)

if [ "$F2P_EXEC" = "PASS" ]; then
    echo "PASS: No NameError on model during mock execution"
    REWARD=$(python3 -c "print($REWARD + 0.40)")
elif [ "$F2P_EXEC" = "FAIL_NAMEERROR" ]; then
    echo "FAIL: NameError on model — setup_hybrid_cp called before model assignment"
elif [ "$F2P_EXEC" = "SKIP" ]; then
    echo "SKIP: Could not extract/exec train function"
else
    echo "WARN: Behavioral test inconclusive (output: $F2P_EXEC)"
fi

echo ""
echo "=== F2P Structural: setup_hybrid_cp called after setup_model ==="
# [pr_diff] (0.15): Backup ordering check via AST (justified: mocked exec may not reach all paths)
ORDER_OK=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'train':
        sm_line = shcp_line = None
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                name = getattr(child.func, 'id', None) or getattr(child.func, 'attr', None)
                if name == 'setup_model' and sm_line is None:
                    sm_line = child.lineno
                elif name == 'setup_hybrid_cp' and shcp_line is None:
                    shcp_line = child.lineno
        if sm_line and shcp_line and shcp_line > sm_line:
            print('1')
        else:
            print('0')
        sys.exit(0)
print('0')
" 2>&1 | tail -1)

if [ "$ORDER_OK" = "1" ]; then
    echo "PASS: setup_hybrid_cp line > setup_model line in train()"
    REWARD=$(python3 -c "print($REWARD + 0.15)")
else
    echo "FAIL: setup_hybrid_cp must appear after setup_model in train()"
fi

echo ""
echo "=== P2P: substitute_ring_attn still called ==="
# [pr_diff] (0.10): Fix must not remove existing ring attention substitution
P2P_RING=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        name = getattr(node.func, 'id', None) or getattr(node.func, 'attr', None)
        if name == 'substitute_ring_attn':
            print('1'); sys.exit(0)
print('0')
" 2>&1 | tail -1)

if [ "$P2P_RING" = "1" ]; then
    echo "PASS: substitute_ring_attn is present"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "FAIL: substitute_ring_attn was removed"
fi

echo ""
echo "=== P2P: setup_model call still present ==="
# [pr_diff] (0.05): setup_model must still be called
P2P_MODEL=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        name = getattr(node.func, 'id', None) or getattr(node.func, 'attr', None)
        if name == 'setup_model':
            print('1'); sys.exit(0)
print('0')
" 2>&1 | tail -1)

if [ "$P2P_MODEL" = "1" ]; then
    echo "PASS: setup_model is present"
    REWARD=$(python3 -c "print($REWARD + 0.05)")
else
    echo "FAIL: setup_model was removed"
fi

echo ""
echo "=== Anti-stub: train() body has >= 20 top-level statements ==="
# [pr_diff] (0.10): Reject trivial stub replacements of the entire function
BODY_SIZE=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'train':
        print(len(node.body)); sys.exit(0)
print('0')
" 2>&1 | tail -1)

if [ "${BODY_SIZE:-0}" -ge 20 ] 2>/dev/null; then
    echo "PASS: train() has $BODY_SIZE statements (>= 20)"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "FAIL: train() body too small ($BODY_SIZE stmts, need >= 20) — likely a stub"
fi

echo ""
echo "=== Anti-stub: setup_hybrid_cp call still present ==="
# [pr_diff] (0.05): Must not just delete setup_hybrid_cp to avoid NameError
SHCP=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        name = getattr(node.func, 'id', None) or getattr(node.func, 'attr', None)
        if name == 'setup_hybrid_cp':
            print('1'); sys.exit(0)
print('0')
" 2>&1 | tail -1)

if [ "$SHCP" = "1" ]; then
    echo "PASS: setup_hybrid_cp call is present"
    REWARD=$(python3 -c "print($REWARD + 0.05)")
else
    echo "FAIL: setup_hybrid_cp was removed (stub/deletion fix)"
fi

echo ""
echo "=== Anti-stub: file retains original functions ==="
# [pr_diff] (0.05): Original train() calls setup_ckpt_managers; reject total rewrites
CKPT_MGR=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        name = getattr(node.func, 'id', None) or getattr(node.func, 'attr', None)
        if name == 'setup_ckpt_managers':
            print('1'); sys.exit(0)
print('0')
" 2>&1 | tail -1)

if [ "$CKPT_MGR" = "1" ]; then
    echo "PASS: setup_ckpt_managers call retained"
    REWARD=$(python3 -c "print($REWARD + 0.05)")
else
    echo "FAIL: setup_ckpt_managers removed — file appears gutted"
fi

echo ""
echo "=== Config: no unnecessary try/except around fix ==="
# [agent_config] (0.05): "Avoid try/except blocks unless really necessary" — AGENTS.md:5
NO_TRY=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Try):
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                name = getattr(child.func, 'id', None) or getattr(child.func, 'attr', None)
                if name == 'setup_hybrid_cp':
                    print('0'); sys.exit(0)
print('1')
" 2>&1 | tail -1)

if [ "$NO_TRY" = "1" ]; then
    echo "PASS: setup_hybrid_cp not wrapped in try/except"
    REWARD=$(python3 -c "print($REWARD + 0.05)")
else
    echo "FAIL: setup_hybrid_cp should not be in a try/except block"
fi

echo ""
echo "=== Final Score ==="
echo "Score: $REWARD"
echo "$REWARD" > "/logs/verifier/reward.txt"

python3 -c "
import json
score = float('$REWARD')
json.dump({
    'reward': score,
    'behavioral': min(score, 0.40),
    'regression': min(max(score - 0.40, 0), 0.35),
    'config': min(max(score - 0.95, 0), 0.05),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source "$TASK_DIR/tests/judge_hook.sh" 2>/dev/null || true
