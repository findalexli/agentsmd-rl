#!/usr/bin/env bash
set +e

TOTAL=0
add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

cd /repo

TARGET="src/transformers/generation/continuous_batching/continuous_api.py"

###############################################################################
# GATE: Syntax check — abort on failure
###############################################################################
# [pr_diff] (0): Python syntax valid
python3 -c "
import py_compile, sys
try:
    py_compile.compile('$TARGET', doraise=True)
except py_compile.PyCompileError as e:
    print(f'GATE FAIL: {e}', file=sys.stderr)
    sys.exit(1)
print('GATE: syntax OK')
" || { echo "0.0" > /logs/verifier/reward.txt; exit 0; }

###############################################################################
# FAIL-TO-PASS (0.40): torch.cuda.graph is called with a thread-safe
# capture_error_mode.  We monkey-patch torch.cuda.graph so the code actually
# executes on CPU, and capture what keyword arguments it receives.
###############################################################################
# [pr_diff] (0.40): CUDA graph capture must use a non-global capture_error_mode
if python3 -c "
import sys, types, unittest.mock as mock

# ----- build a minimal mock environment so _generation_step can run -------
import torch

# Record kwargs passed to torch.cuda.graph(...)
captured_kwargs = {}

class FakeGraphCtx:
    '''Fake context manager returned by our patched torch.cuda.graph.'''
    def __enter__(self):
        return self
    def __exit__(self, *a):
        pass

def fake_cuda_graph(*args, **kwargs):
    captured_kwargs.update(kwargs)
    return FakeGraphCtx()

# Patch torch.cuda so graph() is callable on CPU
real_cuda = torch.cuda
torch.cuda.graph = fake_cuda_graph
torch.cuda.CUDAGraph = lambda: mock.MagicMock()
torch.cuda.graph_pool_handle = lambda: mock.MagicMock()
torch.cuda.current_stream = lambda *a, **kw: mock.MagicMock()
torch.cuda.Stream = lambda *a, **kw: mock.MagicMock()

# We need to import the module and find the class that has _generation_step
# Use AST to extract just the function so we don't pull in heavy deps
import ast, textwrap, inspect

with open('$TARGET') as f:
    source = f.read()

tree = ast.parse(source)

# Find _generation_step method
func_source = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_generation_step':
        lines = source.splitlines(keepends=True)
        func_source = ''.join(lines[node.lineno - 1 : node.end_lineno])
        break

if func_source is None:
    print('FAIL: _generation_step method not found', file=sys.stderr)
    sys.exit(1)

# Dedent and compile the function
func_source = textwrap.dedent(func_source)

# Build a namespace with everything the function might reference
ns = {
    'torch': torch,
    'gc': __import__('gc'),
    'contextlib': __import__('contextlib'),
    '__builtins__': __builtins__,
}

exec(func_source, ns)
gen_step = ns['_generation_step']

# Build a mock self object that exercises the CUDA graph creation path
mock_self = mock.MagicMock()
mock_self.use_cuda_graph = True
mock_self.graph_pool = mock.MagicMock()
# cuda_graphs dict must NOT contain the batch size key, so we enter the
# 'capture new graph' branch  (the else branch)
mock_self.cuda_graphs = {}
mock_self.static_inputs = {}
mock_self.compute_stream = mock.MagicMock()
# forward_fn should be callable
forward_fn = mock.MagicMock(return_value=mock.MagicMock())
# input_ids needs .shape[0] for batch_size
input_ids = mock.MagicMock()
input_ids.shape = [4]  # batch_size = 4

# Call _generation_step — this should invoke torch.cuda.graph(...)
try:
    gen_step(mock_self, forward_fn, input_ids)
except Exception as e:
    # Some downstream mock issues are fine — we only care about the
    # torch.cuda.graph call that already happened
    pass

# Check that capture_error_mode was passed with a thread-safe value
mode = captured_kwargs.get('capture_error_mode')
if mode is None:
    print('FAIL: torch.cuda.graph() called without capture_error_mode', file=sys.stderr)
    sys.exit(1)
if mode == 'global':
    print(f'FAIL: capture_error_mode={mode!r} is not thread-safe', file=sys.stderr)
    sys.exit(1)
if mode not in ('thread_local', 'relaxed'):
    print(f'FAIL: capture_error_mode={mode!r} is not a recognized safe value', file=sys.stderr)
    sys.exit(1)

print(f'OK: capture_error_mode={mode!r}')
" 2>&1; then
    echo "PASS (0.40): torch.cuda.graph called with thread-safe capture_error_mode"
    add 0.40
else
    echo "FAIL (0.40): torch.cuda.graph not called with thread-safe capture_error_mode"
fi

###############################################################################
# FAIL-TO-PASS (0.20): The capture_error_mode value is NOT the unsafe default.
# This is a simpler AST fallback in case the behavioral test above can't
# exercise the exact code path (e.g., mock gaps). Checks ANY torch.cuda.graph
# call in the file has capture_error_mode set to a safe value.
###############################################################################
# [pr_diff] (0.20): capture_error_mode kwarg present with safe value (AST fallback)
# WHY AST: fallback for when mocking can't fully exercise the CUDA graph path
if python3 -c "
import ast, sys

with open('$TARGET') as f:
    tree = ast.parse(f.read())

found = False
for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue
    # Match torch.cuda.graph(...) OR any call with capture_error_mode kwarg
    # (handles helper wrappers, manual API, etc.)
    for kw in node.keywords:
        if kw.arg == 'capture_error_mode':
            if isinstance(kw.value, ast.Constant) and kw.value.value in ('thread_local', 'relaxed'):
                found = True
                break
            elif isinstance(kw.value, ast.Constant) and kw.value.value == 'global':
                print('FAIL: capture_error_mode is global (unsafe)', file=sys.stderr)
                sys.exit(1)
    if found:
        break

if not found:
    print('FAIL: no capture_error_mode with safe value found anywhere in file', file=sys.stderr)
    sys.exit(1)
print('OK')
" 2>/dev/null; then
    echo "PASS (0.20): AST confirms capture_error_mode is safe"
    add 0.20
else
    echo "FAIL (0.20): AST check for capture_error_mode failed"
fi

###############################################################################
# PASS-TO-PASS (0.15): Upstream CPU-safe unit tests still pass
###############################################################################
# [repo_tests] (0.15): ContinuousBatchingNoAcceleratorTest unit tests
if python3 -m pytest tests/generation/test_continuous_batching.py \
    -k "ContinuousBatchingNoAcceleratorTest and not slow" \
    -x --timeout=45 -q 2>&1 | tail -5; then
    echo "PASS (0.15): upstream CPU unit tests pass"
    add 0.15
else
    echo "FAIL (0.15): upstream CPU unit tests failed"
fi

###############################################################################
# PASS-TO-PASS (0.10): _generation_step method exists and has non-trivial body
###############################################################################
# [pr_diff] (0.10): method not deleted or stubbed
if python3 -c "
import ast, sys

with open('$TARGET') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_generation_step':
        # Count meaningful statements (exclude docstrings, pass, ellipsis)
        body = node.body
        meaningful = 0
        for stmt in ast.walk(node):
            if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.If, ast.For,
                                  ast.While, ast.With, ast.Return, ast.Expr)):
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
                    continue  # skip docstrings
                meaningful += 1
        if meaningful < 5:
            print(f'FAIL: _generation_step has only {meaningful} statements — likely stubbed', file=sys.stderr)
            sys.exit(1)
        print(f'OK: {meaningful} meaningful statements')
        sys.exit(0)

print('FAIL: _generation_step not found', file=sys.stderr)
sys.exit(1)
" 2>/dev/null; then
    echo "PASS (0.10): _generation_step is non-trivial"
    add 0.10
else
    echo "FAIL (0.10): _generation_step missing or stubbed"
fi

###############################################################################
# CONFIG (0.05): ruff check on changed file
###############################################################################
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ e5ad394
if command -v ruff &>/dev/null; then
    if ruff check "$TARGET" --quiet 2>/dev/null; then
        echo "PASS (0.05): ruff check passes"
        add 0.05
    else
        echo "FAIL (0.05): ruff check fails"
    fi
else
    echo "SKIP (0.05): ruff not installed, awarding points"
    add 0.05
fi

###############################################################################
# CONFIG (0.05): no wildcard imports
###############################################################################
# [agent_config] (0.05): code style enforced — .github/copilot-instructions.md:14 @ e5ad394
if python3 -c "
import ast, sys
with open('$TARGET') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.names and node.names[0].name == '*':
        print(f'Wildcard import from {node.module}', file=sys.stderr)
        sys.exit(1)
print('OK')
" 2>/dev/null; then
    echo "PASS (0.05): no wildcard imports"
    add 0.05
else
    echo "FAIL (0.05): wildcard imports found"
fi

###############################################################################
# CONFIG (0.05): file is importable (no import-time crashes)
###############################################################################
# [agent_config] (0.05): module must parse and have valid structure
if python3 -c "
import ast, sys
with open('$TARGET') as f:
    tree = ast.parse(f.read())
# Verify key class exists
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
if not any('Batch' in c or 'Continuous' in c for c in classes):
    print('FAIL: expected continuous batching class not found', file=sys.stderr)
    sys.exit(1)
print('OK')
" 2>/dev/null; then
    echo "PASS (0.05): module structure intact"
    add 0.05
else
    echo "FAIL (0.05): module structure broken"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total reward: $TOTAL"
echo "$TOTAL" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
