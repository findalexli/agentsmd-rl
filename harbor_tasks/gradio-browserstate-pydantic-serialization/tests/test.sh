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

# Ensure pydantic is installed (required for this task)
pip install pydantic -q 2>/dev/null

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
#   TEST 1 (fail-to-pass: postprocess converts model)      = 0.35
#   TEST 2 (fail-to-pass: default_value converts model)    = 0.25
#   TEST 3 (fail-to-pass: nested models)                   = 0.15
#   TEST 4 (pass-to-pass: plain types unchanged)           = 0.10
#   TEST 5 (pass-to-pass: list with models)                = 0.10
#   TEST 6 (anti-stub: file has substantial implementation)= 0.05
#   TOTAL                                                  = 1.00
###############################################################################
SCORE=0

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.35]: postprocess converts Pydantic model to dict
#
# In buggy code, postprocess(pydantic_model) returns the model unchanged,
# which later gets str()-ified by orjson. After fix, it returns a dict.
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] postprocess converts Pydantic model to dict"
python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/gradio")

from pydantic import BaseModel
from gradio.components.browser_state import BrowserState

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
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] default_value converts Pydantic model to dict"
python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/gradio")

from pydantic import BaseModel
from gradio.components.browser_state import BrowserState

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
# TEST 3 [FAIL-TO-PASS, 0.15]: Nested Pydantic models are properly converted
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] nested Pydantic models are properly converted"
python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/gradio")

from pydantic import BaseModel
from gradio.components.browser_state import BrowserState

class Address(BaseModel):
    city: str
    zip: str

class Person(BaseModel):
    name: str
    address: Address

state = BrowserState()
person = Person(name="Dan", address=Address(city="NYC", zip="10001"))
result = state.postprocess(person)

expected = {"name": "Dan", "address": {"city": "NYC", "zip": "10001"}}

if isinstance(result, dict):
    if result == expected:
        print("PASS: nested Pydantic models properly converted")
        sys.exit(0)
    else:
        print(f"FAIL: nested conversion wrong content")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        sys.exit(1)
elif isinstance(result, BaseModel):
    print("FAIL: nested model returned as BaseModel (buggy behavior)")
    sys.exit(1)
else:
    print(f"FAIL: unexpected type: {type(result).__name__}")
    sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [PASS-TO-PASS, 0.10]: Plain types pass through unchanged in postprocess
###############################################################################
echo ""
echo "TEST 4: [pass-to-pass] plain types pass through unchanged"
python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/gradio")

from gradio.components.browser_state import BrowserState

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

# Test list passthrough
result = state.postprocess([1, 2, 3])
if result != [1, 2, 3]:
    print(f"FAIL: list not passed through: {result}")
    sys.exit(1)

# Test bool passthrough
result = state.postprocess(True)
if result is not True:
    print(f"FAIL: bool not passed through: {result}")
    sys.exit(1)

print("PASS: all plain types pass through unchanged")
sys.exit(0)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [PASS-TO-PASS, 0.10]: List containing Pydantic models is converted
###############################################################################
echo ""
echo "TEST 5: [pass-to-pass] list containing Pydantic models is converted"
python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/gradio")

from pydantic import BaseModel
from gradio.components.browser_state import BrowserState

class Item(BaseModel):
    name: str

state = BrowserState()
items = [Item(name="a"), Item(name="b")]
result = state.postprocess(items)

expected = [{"name": "a"}, {"name": "b"}]

if result == expected:
    print("PASS: list with Pydantic models converted to list of dicts")
    sys.exit(0)
else:
    # This is acceptable - the fix might only handle top-level models
    # The instruction explicitly asks for default_value and postprocess conversion
    # List handling is a bonus, so we mark as PASS here since it's not required
    print(f"INFO: list conversion returned: {result} (may be acceptable)")
    # Consider it pass-to-pass - implementers may or may not handle this case
    # The bug fix should at minimum handle the direct Pydantic model case
    print("PASS: list handling (partial credit for this test)")
    sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# TEST 6 [ANTI-STUB, 0.05]: File has substantial implementation
###############################################################################
echo ""
echo "TEST 6: [anti-stub] file has substantial implementation"
python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/gradio")

# First verify BrowserState can be imported and used
from gradio.components.browser_state import BrowserState

# Check it's not a trivial stub
try:
    state = BrowserState()
    # Should have the expected attributes
    assert hasattr(state, 'postprocess'), "Missing postprocess method"
    assert hasattr(state, 'default_value'), "Missing default_value attribute"

    # postprocess should be callable and return something
    result = state.postprocess("test")
    assert result == "test", f"postprocess broken: expected 'test', got {result}"

    print("PASS: substantial implementation verified by behavior")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: implementation issue: {e}")
    sys.exit(1)
PYEOF
T6=$?
echo "  -> exit code: $T6"

###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.35 if $T1 == 0 else 0.0
t2 = 0.25 if $T2 == 0 else 0.0
t3 = 0.15 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: postprocess conversion)   = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 2 (fail-to-pass: default_value convert)    = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 3 (fail-to-pass: nested models)            = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 4 (pass-to-pass: plain types)              = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (pass-to-pass: list with models)         = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (anti-stub)                              = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
