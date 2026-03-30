#!/usr/bin/env bash
# Verifier for gradio-browserstate-pydantic-serialization
#
# Bug: BrowserState converts Pydantic BaseModel instances to str() repr
# instead of proper JSON dicts, because orjson can't serialize them and
# falls back to str(). Fix: convert via model_dump() in __init__ and postprocess.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/gradio/gradio/components/browser_state.py"

###############################################################################
# GATE: Python syntax validity
###############################################################################
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/gradio/gradio/components/browser_state.py") as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f"GATE FAIL: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: behavioral postprocess)          = 0.30
#   TEST 2 (fail-to-pass: behavioral default_value)        = 0.25
#   TEST 3 (fail-to-pass: behavioral plain types pass)     = 0.15
#   TEST 4 (pass-to-pass: class structure preserved)       = 0.10
#   TEST 5 (structural: model_dump or dict conversion)     = 0.10
#   TEST 6 (anti-stub)                                     = 0.05
#   TOTAL                                                  = 1.00
###############################################################################
SCORE=0

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.30]: postprocess converts Pydantic model to dict
#
# In buggy code, postprocess(pydantic_model) returns the model unchanged,
# which later gets str()-ified by orjson. After fix, it returns a dict.
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] postprocess converts Pydantic model to dict"
python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/gradio")

try:
    from pydantic import BaseModel
except ImportError:
    print("SKIP: pydantic not installed")
    sys.exit(0)

try:
    from gradio.components.browser_state import BrowserState
except Exception as e:
    print(f"FAIL: could not import BrowserState: {e}")
    sys.exit(1)

class Person(BaseModel):
    name: str
    age: int

state = BrowserState()
person = Person(name="Dan", age=20)
result = state.postprocess(person)

if isinstance(result, dict):
    if result == {"name": "Dan", "age": 20}:
        print("PASS: postprocess converted Pydantic model to correct dict")
        sys.exit(0)
    else:
        print(f"FAIL: postprocess returned dict but with wrong content: {result}")
        sys.exit(1)
elif isinstance(result, BaseModel):
    print("FAIL: postprocess returned Pydantic model unchanged (buggy behavior)")
    sys.exit(1)
else:
    print(f"FAIL: postprocess returned unexpected type: {type(result).__name__}: {result}")
    sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.25]: default_value converts Pydantic model to dict
#
# In buggy code, __init__ stores default_value as-is. After fix, Pydantic
# models are converted to dicts.
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] default_value converts Pydantic model to dict"
python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/gradio")

try:
    from pydantic import BaseModel
except ImportError:
    print("SKIP: pydantic not installed")
    sys.exit(0)

try:
    from gradio.components.browser_state import BrowserState
except Exception as e:
    print(f"FAIL: could not import BrowserState: {e}")
    sys.exit(1)

class Person(BaseModel):
    name: str
    age: int

state = BrowserState(default_value=Person(name="Dan", age=20))

if isinstance(state.default_value, dict):
    if state.default_value == {"name": "Dan", "age": 20}:
        print("PASS: default_value converted Pydantic model to correct dict")
        sys.exit(0)
    else:
        print(f"FAIL: default_value is dict but wrong content: {state.default_value}")
        sys.exit(1)
elif isinstance(state.default_value, BaseModel):
    print("FAIL: default_value stored Pydantic model unchanged (buggy behavior)")
    sys.exit(1)
else:
    print(f"FAIL: default_value is unexpected type: {type(state.default_value).__name__}")
    sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.15]: Plain types pass through unchanged
###############################################################################
echo ""
echo "TEST 3: [pass-to-pass] plain types pass through unchanged in postprocess"
python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/gradio")

try:
    from gradio.components.browser_state import BrowserState
except Exception as e:
    print(f"FAIL: could not import BrowserState: {e}")
    sys.exit(1)

state = BrowserState()

# Test dict passthrough
result = state.postprocess({"key": "value"})
if result != {"key": "value"}:
    print(f"FAIL: dict not passed through: {result}")
    sys.exit(1)

# Test string passthrough
result = state.postprocess("hello")
if result != "hello":
    print(f"FAIL: string not passed through: {result}")
    sys.exit(1)

# Test int passthrough
result = state.postprocess(42)
if result != 42:
    print(f"FAIL: int not passed through: {result}")
    sys.exit(1)

# Test None passthrough
result = state.postprocess(None)
if result is not None:
    print(f"FAIL: None not passed through: {result}")
    sys.exit(1)

print("PASS: all plain types pass through unchanged")
sys.exit(0)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [PASS-TO-PASS, 0.10]: BrowserState class structure preserved
###############################################################################
echo ""
echo "TEST 4: [pass-to-pass] BrowserState class structure preserved"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/components/browser_state.py") as f:
    source = f.read()

tree = ast.parse(source)

found_class = False
found_init = False
found_postprocess = False
found_preprocess = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'BrowserState':
        found_class = True
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name == '__init__':
                    found_init = True
                if item.name == 'postprocess':
                    found_postprocess = True
                if item.name == 'preprocess':
                    found_preprocess = True

missing = []
if not found_class:
    missing.append("BrowserState class")
if not found_init:
    missing.append("__init__")
if not found_postprocess:
    missing.append("postprocess")
if not found_preprocess:
    missing.append("preprocess")

if missing:
    print(f"FAIL: missing: {', '.join(missing)}")
    sys.exit(1)

print("PASS: BrowserState class with all expected methods")
sys.exit(0)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [STRUCTURAL, 0.10]: model_dump or dict conversion present
###############################################################################
echo ""
echo "TEST 5: [structural] Pydantic model conversion code present"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/components/browser_state.py") as f:
    source = f.read()

# Check for model_dump() or .dict() or BaseModel import
has_conversion = False
indicators = []

if 'model_dump' in source:
    has_conversion = True
    indicators.append("model_dump()")
if '.dict()' in source:
    has_conversion = True
    indicators.append(".dict()")
if 'BaseModel' in source and ('isinstance' in source or 'model_dump' in source or '.dict()' in source):
    has_conversion = True
    indicators.append("BaseModel isinstance check")

if has_conversion:
    print(f"PASS: Pydantic conversion code found: {', '.join(indicators)}")
    sys.exit(0)
else:
    print("FAIL: no Pydantic model conversion code found (model_dump, .dict(), etc.)")
    sys.exit(1)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# TEST 6 [ANTI-STUB, 0.05]: File not replaced with stub
###############################################################################
echo ""
echo "TEST 6: [anti-stub] file is not a stub"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/components/browser_state.py") as f:
    source = f.read()

line_count = len(source.splitlines())
if line_count < 30:
    print(f"FAIL: only {line_count} lines (expected 30+)")
    sys.exit(1)

tree = ast.parse(source)
classes = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
if classes < 1:
    print(f"FAIL: no classes found")
    sys.exit(1)

if 'BrowserState' not in source:
    print("FAIL: BrowserState not found in source")
    sys.exit(1)

print(f"PASS: {line_count} lines, {classes} class(es)")
sys.exit(0)
PYEOF
T6=$?
echo "  -> exit code: $T6"


# ---------- Config-derived test (0.05): "Python code formatted with ruff" ----------
# Source: AGENTS.md line 43 @ commit 77e7871176e50a894190ac98aa9de8fbdbf3620f
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/components/browser_state.py 2>/dev/null
RUFF_EXIT=$?
cd /
if [ $RUFF_EXIT -eq 0 ]; then T7=0; echo "TEST 7: config ruff format PASS"; else T7=1; echo "TEST 7: config ruff format FAIL"; fi
###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.30 if $T1 == 0 else 0.0
t2 = 0.25 if $T2 == 0 else 0.0
t3 = 0.15 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
t7 = 0.05 if $T7 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6 + t7
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: postprocess conversion) = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 2 (fail-to-pass: default_value convert)  = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 3 (pass-to-pass: plain types)             = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 4 (pass-to-pass: class structure)         = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (structural: conversion code)           = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (anti-stub)                             = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 7 (config: ruff format)                   = $([ $T7 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
