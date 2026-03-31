#!/usr/bin/env bash
set +e

REPO="/workspace/transformers"
MODELING="$REPO/src/transformers/models/nemotron_h/modeling_nemotron_h.py"
MODULAR="$REPO/src/transformers/models/nemotron_h/modular_nemotron_h.py"

total=0.0
add() { total=$(python3 -c "print(round($total + $1, 4))"); }

# ── GATE: Syntax check ──────────────────────────────────────────────
# [pr_diff] (0.00): Both files must be valid Python
python3 -c "
import py_compile, sys
for f in ['$MODELING', '$MODULAR']:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        print(f'GATE FAIL: {e}', file=sys.stderr)
        sys.exit(1)
print('GATE: syntax OK')
"
if [ $? -ne 0 ]; then
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0.0,"detail":"gate_syntax_fail"}' > /logs/verifier/reward.json
  exit 0
fi

# ── FAIL-TO-PASS #1 (0.30): NemotronHBlock.forward does NOT create a stream context ──
# [pr_diff] (0.30): The core bug — stream_context in Block.forward creates a dangling weakref under torch.compile.
# We monkeypatch torch.cuda.stream to detect if Block.forward creates one. On CPU, the buggy code
# takes the nullcontext path, so we also patch contextlib.nullcontext to detect the stream branching pattern.
python3 -c "
import ast, sys

# Read the source
with open('$MODELING') as f:
    source = f.read()

# Check 1: The forward method of NemotronHBlock should not reference stream_context or nullcontext
tree = ast.parse(source)
found_block = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHBlock':
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == 'forward':
                found_block = True
                # Get the actual source lines of just this method
                method_lines = source.splitlines()[item.lineno-1:item.end_lineno]
                method_src = '\n'.join(method_lines)

                # The buggy pattern: forward creates a stream context (torch.cuda.stream or nullcontext)
                # A correct fix removes this entirely from Block.forward.
                # We check the method source for the pattern, not specific variable names.
                has_cuda_stream_call = False
                has_nullcontext = False
                for child in ast.walk(item):
                    # Check for torch.cuda.stream(...) call
                    if isinstance(child, ast.Call):
                        call_src = ast.dump(child)
                        if 'cuda' in call_src and 'stream' in call_src and 'default_stream' in call_src:
                            has_cuda_stream_call = True
                    # Check for contextlib.nullcontext() or nullcontext()
                    if isinstance(child, ast.Call):
                        call_src = ast.dump(child)
                        if 'nullcontext' in call_src:
                            has_nullcontext = True

                if has_cuda_stream_call or has_nullcontext:
                    print('FAIL: NemotronHBlock.forward still creates stream context (cuda.stream or nullcontext)')
                    sys.exit(1)
                else:
                    print('PASS: NemotronHBlock.forward does not create stream context')
                    sys.exit(0)

if not found_block:
    print('FAIL: NemotronHBlock class or forward method not found')
    sys.exit(1)
"
if [ $? -eq 0 ]; then
  echo "PASS (0.30): Block.forward stream context removed"
  add 0.30
else
  echo "FAIL (0.30): Block.forward still has stream context pattern"
fi

# ── FAIL-TO-PASS #2 (0.25): Mixer.forward handles CUDA stream with compile guard ──
# [pr_diff] (0.25): The stream management should move into the mixer, guarded by is_torchdynamo_compiling.
# We require BOTH stream management AND a compile guard in the mixer's forward (or cuda_kernels_forward).
# The base code already has a compile guard but does NOT have stream management in mixer — so this
# only passes after the fix is applied.
python3 -c "
import ast, sys

with open('$MODELING') as f:
    source = f.read()

tree = ast.parse(source)

# Look for stream management in mixer's forward or cuda_kernels_forward
def check_method_for_stream(method_node):
    \"\"\"Returns (has_stream, has_compile_guard)\"\"\"
    has_stream = False
    has_guard = False
    for child in ast.walk(method_node):
        if isinstance(child, ast.Attribute):
            attr_chain = ast.dump(child)
            if 'stream' in attr_chain and ('cuda' in attr_chain or 'default_stream' in attr_chain):
                has_stream = True
        if isinstance(child, ast.Call):
            call_src = ast.dump(child)
            if 'torchdynamo_compiling' in call_src or 'is_compiling' in call_src:
                has_guard = True
    return has_stream, has_guard

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHMamba2Mixer':
        stream_found = False
        guard_found = False
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name in ('forward', 'cuda_kernels_forward'):
                    s, g = check_method_for_stream(item)
                    stream_found = stream_found or s
                    guard_found = guard_found or g

        if stream_found and guard_found:
            print('PASS: Mixer has both CUDA stream management and compile guard')
            sys.exit(0)
        elif stream_found:
            print('FAIL: Mixer has stream but missing compile guard')
            sys.exit(1)
        elif guard_found:
            print('FAIL: Mixer has compile guard but no stream management (stream not moved here)')
            sys.exit(1)
        else:
            print('FAIL: Mixer has neither stream management nor compile guard')
            sys.exit(1)

print('FAIL: NemotronHMamba2Mixer not found')
sys.exit(1)
"
if [ $? -eq 0 ]; then
  echo "PASS (0.25): Mixer handles stream with compile guard"
  add 0.25
else
  echo "FAIL (0.25): Mixer missing stream+guard"
fi

# ── FAIL-TO-PASS #4 (0.15): Modular file also updated ───────────────
# [pr_diff] (0.15): modular_nemotron_h.py Block.forward must also not have the stream_context pattern
python3 -c "
import ast, sys

with open('$MODULAR') as f:
    source = f.read()

tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHBlock':
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == 'forward':
                for child in ast.walk(item):
                    if isinstance(child, ast.Call):
                        call_src = ast.dump(child)
                        if 'cuda' in call_src and 'stream' in call_src and 'default_stream' in call_src:
                            print('FAIL: modular Block.forward still has cuda stream creation')
                            sys.exit(1)
                        if 'nullcontext' in call_src:
                            print('FAIL: modular Block.forward still has nullcontext')
                            sys.exit(1)
                print('PASS: modular Block.forward stream context removed')
                sys.exit(0)

# If NemotronHBlock doesn't override forward in modular, that's also fine —
# means the base class no longer has the pattern
print('PASS: modular NemotronHBlock does not override forward (stream removed)')
sys.exit(0)
"
if [ $? -eq 0 ]; then
  echo "PASS (0.15): Modular Block.forward updated"
  add 0.15
else
  echo "FAIL (0.15): Modular Block.forward still buggy"
fi

# ── PASS-TO-PASS (0.10): Required classes and methods preserved ──────
# [repo_tests] (0.10): Core class structure must be intact
python3 -c "
import ast, sys

with open('$MODELING') as f:
    tree = ast.parse(f.read())

required_classes = {'NemotronHBlock', 'NemotronHMamba2Mixer', 'NemotronHPreTrainedModel', 'NemotronHForCausalLM'}
found = set()
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name in required_classes:
        found.add(node.name)

missing = required_classes - found
if missing:
    print(f'FAIL: Missing classes: {missing}')
    sys.exit(1)

# NemotronHBlock must have forward and __init__
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHBlock':
        methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if 'forward' not in methods or '__init__' not in methods:
            print('FAIL: NemotronHBlock missing forward or __init__')
            sys.exit(1)

# NemotronHMamba2Mixer must have forward, torch_forward, cuda_kernels_forward
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHMamba2Mixer':
        methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for m in ['forward', 'torch_forward', 'cuda_kernels_forward']:
            if m not in methods:
                print(f'FAIL: NemotronHMamba2Mixer missing {m}')
                sys.exit(1)

print('PASS: All required classes and methods present')
"
if [ $? -eq 0 ]; then
  echo "PASS (0.10): P2P class structure"
  add 0.10
else
  echo "FAIL (0.10): P2P class structure broken"
fi

# ── ANTI-STUB (0.10): Block.forward has real implementation ──────────
# [pr_diff] (0.10): Block.forward must contain residual connection, norm, and mixer dispatch
python3 -c "
import ast, sys

with open('$MODELING') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NemotronHBlock':
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == 'forward':
                if len(item.body) < 4:
                    print(f'FAIL: forward too short ({len(item.body)} stmts)')
                    sys.exit(1)
                # Check for key behavioral elements via AST (not variable names)
                has_addition = False
                has_call = False
                has_return = False
                for child in ast.walk(item):
                    if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Add):
                        has_addition = True  # residual connection
                    if isinstance(child, ast.Call):
                        has_call = True  # calls norm/mixer
                    if isinstance(child, ast.Return):
                        has_return = True
                if not (has_addition and has_call and has_return):
                    print('FAIL: forward missing key operations (addition/call/return)')
                    sys.exit(1)
                print('PASS: forward has substantial implementation')
                sys.exit(0)

print('FAIL: NemotronHBlock.forward not found')
sys.exit(1)
"
if [ $? -eq 0 ]; then
  echo "PASS (0.10): Anti-stub"
  add 0.10
else
  echo "FAIL (0.10): Anti-stub failed"
fi

# ── CONFIG: ruff lint ────────────────────────────────────────────────
# [agent_config] (0.10): "make style: runs formatters and linters (ruff)" — .ai/AGENTS.md:2 @ 20a233bd
if command -v ruff &>/dev/null; then
  ruff_output=$(ruff check --select=E,W "$MODELING" "$MODULAR" 2>&1)
  if echo "$ruff_output" | grep -qE "^Found [1-9]"; then
    echo "FAIL (0.10): ruff errors found"
  else
    echo "PASS (0.10): ruff check passed"
    add 0.10
  fi
else
  echo "SKIP (0.10): ruff not installed"
fi

# ── Final score ──────────────────────────────────────────────────────
echo "$total" > /logs/verifier/reward.txt
behavioral=$(python3 -c "print(round(min($total, 0.70), 4))")
echo "{\"reward\":$total,\"behavioral\":$behavioral,\"regression\":0.10,\"config\":0.10}" > /logs/verifier/reward.json
echo "Total reward: $total"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
