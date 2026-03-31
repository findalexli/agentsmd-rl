#!/usr/bin/env bash
# Verifier for vllm-model-loader-device-context
#
# Bug: In base_loader.py, log_model_inspection() runs inside the target_device
# context manager (combined `with dtype, device:` block), causing GPU memory
# CI failures. The fix ensures log_model_inspection runs outside the device
# context but still inside the dtype context.
#
# Approach: We extract the load_model function via AST and re-execute it with
# lightweight mocks, tracking which context managers are active when each
# operation runs. This is BEHAVIORAL — it tests call-order semantics, not
# code structure.
#
set +e

TARGET="/workspace/vllm/vllm/model_executor/model_loader/base_loader.py"
mkdir -p /logs/verifier

###############################################################################
# GATE: Python syntax validity
###############################################################################
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/vllm/vllm/model_executor/model_loader/base_loader.py") as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f"GATE FAIL: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass behavioral: log_model_inspection outside device)  = 0.35
#   TEST 2 (fail-to-pass behavioral: initialize_model inside device)       = 0.25
#   TEST 3 (pass-to-pass: key classes/methods/calls preserved)             = 0.15
#   TEST 4 (anti-stub: file has real content)                              = 0.15
#   TEST 5 (config-derived: no bare pip install) — AGENTS.md:42           = 0.10
#                                                                   TOTAL = 1.00
###############################################################################
SCORE=0

###############################################################################
# TEST 1 [pr_diff] (0.35): log_model_inspection must NOT run while the
#   target_device context manager is active.
#
# This is a BEHAVIORAL test. We extract load_model via AST, replace heavy
# dependencies with mocks that track context-manager state, then execute
# the function and check whether log_model_inspection was called while the
# device context was entered.
###############################################################################
echo ""
echo "TEST 1: [pr_diff] log_model_inspection must be outside the device context (behavioral)"
python3 << 'PYEOF'
import ast, sys, textwrap, types

TARGET = "/workspace/vllm/vllm/model_executor/model_loader/base_loader.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find load_model method
load_model_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'load_model':
        load_model_node = node
        break

if load_model_node is None:
    print("FAIL: load_model method not found")
    sys.exit(1)

# Extract load_model source
src_lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(src_lines[load_model_node.lineno - 1:load_model_node.end_lineno]))

# Build mock environment to track context manager state
call_log = []  # list of (func_name, device_ctx_active)
device_ctx_active = False

class DeviceCtx:
    """Mock for torch.device that tracks enter/exit."""
    def __enter__(self):
        global device_ctx_active
        device_ctx_active = True
        return self
    def __exit__(self, *a):
        global device_ctx_active
        device_ctx_active = False

class DtypeCtx:
    """Mock for set_default_torch_dtype — just a passthrough context."""
    def __enter__(self):
        return self
    def __exit__(self, *a):
        pass

class FakeModel:
    """Stand-in for the model object."""
    def named_parameters(self):
        return []
    def __repr__(self):
        return "FakeModel()"

class FakeLogger:
    def debug(self, *a, **kw): pass
    def info(self, *a, **kw): pass
    def warning(self, *a, **kw): pass

def mock_initialize_model(**kwargs):
    call_log.append(("initialize_model", device_ctx_active))
    return FakeModel()

def mock_log_model_inspection(model, **kwargs):
    call_log.append(("log_model_inspection", device_ctx_active))

def mock_set_default_torch_dtype(dtype):
    return DtypeCtx()

class FakeConfig:
    dtype = "float32"
    device = None
    quantization = None
    model = "test"
    revision = None
    load_format = "auto"
    is_attention_free = False
    trust_remote_code = False
    tokenizer = "test"
    enforce_eager = False
    max_model_len = 100
    def __getattr__(self, name):
        return None

class FakeTorch:
    class device:
        def __init__(self, d):
            self._ctx = DeviceCtx()
        def __enter__(self):
            return self._ctx.__enter__()
        def __exit__(self, *a):
            return self._ctx.__exit__(*a)

# Build namespace for exec
ns = {
    "__builtins__": __builtins__,
    "initialize_model": mock_initialize_model,
    "log_model_inspection": mock_log_model_inspection,
    "set_default_torch_dtype": mock_set_default_torch_dtype,
    "torch": FakeTorch,
    "logger": FakeLogger(),
    "process_weights_after_loading": lambda model, vllm_config, load_config: None,
}

# Rewrite the function as a standalone (remove 'self' dependency)
# We need to supply self-like attributes
class FakeSelf:
    def __getattr__(self, name):
        return FakeConfig()

# Try executing it — wrap in a class to keep self
exec_src = f"""
class _Wrapper:
{textwrap.indent(func_src, '    ')}
"""

try:
    exec(compile(exec_src, "<test>", "exec"), ns)
    wrapper = ns["_Wrapper"]()
    # Call load_model with fake configs
    fc = FakeConfig()

    # Build a minimal vllm_config-like object
    class VllmConfig:
        model_config = fc
        load_config = fc
        device_config = fc
        parallel_config = fc
        scheduler_config = fc
        cache_config = fc
        def __getattr__(self, name):
            return FakeConfig()

    wrapper.load_model(vllm_config=VllmConfig(), model_config=fc, prefix="")
except Exception as e:
    # If exec fails, that's fine — fall back to AST analysis
    print(f"INFO: Could not execute load_model directly ({type(e).__name__}: {e})")
    print("Falling back to AST nesting analysis...")

    # AST fallback: check that log_model_inspection is NOT nested under the
    # same With that contains target_device/torch.device
    # This is more permissive than indent checking — accepts ExitStack, extract-method, etc.

    def find_calls_under_device_with(node, in_device_ctx=False):
        """Walk AST, tracking whether we're inside a With that uses target_device."""
        results = {}
        if isinstance(node, ast.With):
            has_device = any(
                'target_device' in ast.dump(item.context_expr) or
                'device' in ast.dump(item.context_expr).lower()
                for item in node.items
                if 'set_default_torch_dtype' not in ast.dump(item.context_expr)
            )
            for child in ast.iter_child_nodes(node):
                r = find_calls_under_device_with(child, in_device_ctx or has_device)
                results.update(r)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            fname = ""
            if isinstance(func, ast.Name):
                fname = func.id
            elif isinstance(func, ast.Attribute):
                fname = func.attr
            if fname in ("log_model_inspection", "initialize_model"):
                results[fname] = in_device_ctx
            for child in ast.iter_child_nodes(node):
                r = find_calls_under_device_with(child, in_device_ctx)
                results.update(r)
        else:
            for child in ast.iter_child_nodes(node):
                r = find_calls_under_device_with(child, in_device_ctx)
                results.update(r)
        return results

    call_contexts = find_calls_under_device_with(load_model_node)
    if "log_model_inspection" in call_contexts:
        call_log.append(("log_model_inspection", call_contexts["log_model_inspection"]))
    if "initialize_model" in call_contexts:
        call_log.append(("initialize_model", call_contexts["initialize_model"]))

# Check results
log_inspect_calls = [c for c in call_log if c[0] == "log_model_inspection"]
if not log_inspect_calls:
    print("FAIL: log_model_inspection was never called/found")
    sys.exit(1)

# The key assertion: log_model_inspection must NOT be inside the device context
if log_inspect_calls[0][1]:  # device_ctx_active was True
    print("FAIL: log_model_inspection runs inside the device context")
    sys.exit(1)

print("PASS: log_model_inspection runs outside the device context")
sys.exit(0)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [pr_diff] (0.25): initialize_model must still run INSIDE the device
#   context. The fix separates the contexts but doesn't remove the device
#   context — model init still needs it.
###############################################################################
echo ""
echo "TEST 2: [pr_diff] initialize_model must still be inside the device context (behavioral)"
python3 << 'PYEOF'
import ast, sys, textwrap

TARGET = "/workspace/vllm/vllm/model_executor/model_loader/base_loader.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

load_model_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'load_model':
        load_model_node = node
        break

if load_model_node is None:
    print("FAIL: load_model method not found")
    sys.exit(1)

# Re-use the AST nesting analysis from T1's fallback — more robust than indent checks
def find_calls_under_device_with(node, in_device_ctx=False):
    results = {}
    if isinstance(node, ast.With):
        has_device = any(
            'target_device' in ast.dump(item.context_expr) or
            ('device' in ast.dump(item.context_expr).lower()
             and 'set_default_torch_dtype' not in ast.dump(item.context_expr))
            for item in node.items
        )
        for child in ast.iter_child_nodes(node):
            r = find_calls_under_device_with(child, in_device_ctx or has_device)
            results.update(r)
    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        func = node.value.func
        fname = ""
        if isinstance(func, ast.Name):
            fname = func.id
        elif isinstance(func, ast.Attribute):
            fname = func.attr
        if fname == "initialize_model":
            results[fname] = in_device_ctx
        for child in ast.iter_child_nodes(node):
            r = find_calls_under_device_with(child, in_device_ctx)
            results.update(r)
    elif isinstance(node, ast.Assign):
        # Handle: model = initialize_model(...)
        if isinstance(node.value, ast.Call):
            func = node.value.func
            fname = ""
            if isinstance(func, ast.Name):
                fname = func.id
            elif isinstance(func, ast.Attribute):
                fname = func.attr
            if fname == "initialize_model":
                results[fname] = in_device_ctx
        for child in ast.iter_child_nodes(node):
            r = find_calls_under_device_with(child, in_device_ctx)
            results.update(r)
    else:
        for child in ast.iter_child_nodes(node):
            r = find_calls_under_device_with(child, in_device_ctx)
            results.update(r)
    return results

call_contexts = find_calls_under_device_with(load_model_node)

if "initialize_model" not in call_contexts:
    print("FAIL: initialize_model call not found in load_model")
    sys.exit(1)

if not call_contexts["initialize_model"]:
    print("FAIL: initialize_model is NOT inside a device context (it should be)")
    sys.exit(1)

print("PASS: initialize_model runs inside the device context")
sys.exit(0)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [pr_diff] (0.15): Key functions and class structure preserved
#   (pass-to-pass regression check)
###############################################################################
echo ""
echo "TEST 3: [pr_diff] key functions and class structure preserved"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/model_executor/model_loader/base_loader.py") as f:
    source = f.read()

tree = ast.parse(source)

found_class = False
found_load_model = False
found_load_weights = False
found_log_inspection = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'BaseModelLoader':
        found_class = True
        for item in ast.walk(node):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name == 'load_model':
                    found_load_model = True
                if item.name == 'load_weights':
                    found_load_weights = True
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'log_model_inspection':
            found_log_inspection = True

errors = []
if not found_class:
    errors.append("BaseModelLoader class missing")
if not found_load_model:
    errors.append("load_model method missing")
if not found_load_weights:
    errors.append("load_weights method missing")
if not found_log_inspection:
    errors.append("log_model_inspection function missing")

if errors:
    print(f"FAIL: {', '.join(errors)}")
    sys.exit(1)

# Verify key calls exist in load_model body
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'load_model':
        func_node = node
        break

func_source = '\n'.join(source.splitlines()[func_node.lineno - 1:func_node.end_lineno])
required = ['initialize_model', 'log_model_inspection', 'load_weights', 'process_weights_after_loading']
missing = [r for r in required if r not in func_source]
if missing:
    print(f"FAIL: load_model missing key calls: {missing}")
    sys.exit(1)

print("PASS: all key classes, methods, and calls preserved")
sys.exit(0)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [pr_diff] (0.15): Anti-stub — file has real content, not gutted
###############################################################################
echo ""
echo "TEST 4: [pr_diff] file is not a stub"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/model_executor/model_loader/base_loader.py") as f:
    source = f.read()

tree = ast.parse(source)
line_count = len(source.splitlines())

if line_count < 60:
    print(f"FAIL: only {line_count} lines (expected 60+, original is ~100)")
    sys.exit(1)

funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
if len(funcs) < 3:
    print(f"FAIL: only {len(funcs)} functions (expected 3+)")
    sys.exit(1)

# Check that load_model has non-trivial body (>10 statements when walked)
for n in ast.walk(tree):
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == 'load_model':
        stmts = [s for s in ast.walk(n) if isinstance(s, (ast.Assign, ast.Expr, ast.Return, ast.With, ast.If, ast.For))]
        if len(stmts) < 5:
            print(f"FAIL: load_model has only {len(stmts)} statements (stub)")
            sys.exit(1)
        break

print(f"PASS: {line_count} lines, {len(funcs)} functions, load_model non-trivial")
sys.exit(0)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [agent_config] (0.10): No bare pip install in changed files
# "Never use system python3 or bare pip/pip install" — AGENTS.md:42
# @ af89140efc06c462ae531999b9f2db6ba0c7a528
###############################################################################
echo ""
echo "TEST 5: [agent_config] no bare pip install in changed files"
cd /workspace/vllm 2>/dev/null
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null || true)
T5=0
BARE_PIP=0
for cf in $CHANGED_FILES; do
    if [ -f "/workspace/vllm/$cf" ]; then
        if grep -Pn '(?<!uv )pip install' "/workspace/vllm/$cf" 2>/dev/null | grep -v '^.*#' | grep -v 'uv pip' > /dev/null 2>&1; then
            echo "  FAIL: $cf contains bare 'pip install'"
            BARE_PIP=1
        fi
    fi
done
if [ "$BARE_PIP" -eq 1 ]; then
    T5=1
else
    echo "  PASS"
fi
echo "  -> exit code: $T5"

###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.35 if $T1 == 0 else 0.0
t2 = 0.25 if $T2 == 0 else 0.0
t3 = 0.15 if $T3 == 0 else 0.0
t4 = 0.15 if $T4 == 0 else 0.0
t5 = 0.10 if ${T5:-1} == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (F2P: log_inspect outside device ctx)  = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 2 (F2P: initialize_model inside device)  = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 3 (P2P: structure preserved)              = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 4 (anti-stub: file not gutted)            = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 5 (config: no bare pip)                   = $([ ${T5:-1} -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "$SCORE" > /logs/verifier/reward.txt

cat > /logs/verifier/reward.json << JSONEOF
{"reward": $SCORE, "behavioral": $(python3 -c "print(f'{(0.35 if $T1==0 else 0)+(0.25 if $T2==0 else 0):.2f}')"), "regression": $(python3 -c "print(f'{(0.15 if $T3==0 else 0)+(0.15 if $T4==0 else 0):.2f}')"), "config": $(python3 -c "print(f'{0.10 if ${T5:-1}==0 else 0:.2f}'")}
JSONEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
