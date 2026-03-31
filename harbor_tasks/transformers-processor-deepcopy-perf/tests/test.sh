#!/usr/bin/env bash
# Verifier for transformers-processor-deepcopy-perf
# Bug: ProcessorMixin.to_dict() deepcopies tokenizer unnecessarily (huge perf hit)
# File: src/transformers/processing_utils.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/transformers/src/transformers/processing_utils.py"

echo "=== transformers-processor-deepcopy-perf verifier ==="

# ── GATE: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/transformers/src/transformers/processing_utils.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# ── GATE: ProcessorMixin.to_dict can be imported ─────────────────────────
echo ""
echo "GATE: ProcessorMixin.to_dict can be imported"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers')
try:
    from transformers.processing_utils import ProcessorMixin
    assert hasattr(ProcessorMixin, 'to_dict'), "ProcessorMixin missing to_dict method"
    print("  OK: ProcessorMixin.to_dict imported successfully")
    sys.exit(0)
except Exception as e:
    print(f"  FAIL: Import error: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: cannot import to_dict — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_BEHAV_SKIP_TOKENIZER_DEEPCOPY=0.35  # Primary fail-to-pass: tokenizer not deepcopied
W_BEHAV_CORRECT_OUTPUT=0.25           # Correctness: output dict is correct
W_P2P_STRUCTURE=0.15                  # P2P: method structure preserved
W_P2P_FUNCTIONAL=0.15                 # P2P: functional tests still pass
W_ANTISTUB=0.10                       # Anti-stub: real implementation

echo ""
echo "Weight distribution:"
echo "  - F2P (skip tokenizer deepcopy): $W_BEHAV_SKIP_TOKENIZER_DEEPCOPY"
echo "  - F2P (correct output): $W_BEHAV_CORRECT_OUTPUT"
echo "  - P2P (structure): $W_P2P_STRUCTURE"
echo "  - P2P (functional): $W_P2P_FUNCTIONAL"
echo "  - Anti-stub: $W_ANTISTUB"

SCORE="0.0"

# ── TEST 1 (PRIMARY FAIL-TO-PASS): Behavioral - tokenizer not deepcopied ──
# [pr_diff] (0.35): Tokenizer attributes excluded before deepcopy
echo ""
echo "TEST 1: behavioral - tokenizer not deepcopied (weight=$W_BEHAV_SKIP_TOKENIZER_DEEPCOPY)"
T1=$(python3 << 'PYEOF'
import sys
import copy

# Track all deepcopy calls
deepcopy_calls = []
original_deepcopy = copy.deepcopy

def tracking_deepcopy(obj, *args, **kwargs):
    deepcopy_calls.append(type(obj).__name__)
    return original_deepcopy(obj, *args, **kwargs)

copy.deepcopy = tracking_deepcopy

sys.path.insert(0, '/workspace/transformers')

# Import after patching deepcopy
from transformers.processing_utils import ProcessorMixin

# Create mock objects to test to_dict behavior
class MockTokenizer:
    """Mock tokenizer that would be expensive to deepcopy"""
    def __init__(self):
        # Simulate large vocabulary
        self.vocab = {f"token_{i}": i for i in range(10000)}
        self.name_or_path = "mock/tokenizer"

class MockImageProcessor:
    """Mock image processor that should be preserved"""
    def __init__(self):
        self.size = {"height": 224, "width": 224}
        self.name_or_path = "mock/image_processor"

# Create a minimal ProcessorMixin instance
class TestProcessor(ProcessorMixin):
    attributes = ["tokenizer", "image_processor"]

    @classmethod
    def get_attributes(cls):
        return cls.attributes

    def __init__(self):
        self.tokenizer = MockTokenizer()
        self.image_processor = MockImageProcessor()
        self.chat_template = None
        self._processor_class = "TestProcessor"

# Instantiate and call to_dict
processor = TestProcessor()

# Clear any deepcopy calls from initialization
deepcopy_calls.clear()

try:
    result = processor.to_dict()
except Exception as e:
    print(f"FAIL: to_dict raised exception: {e}")
    sys.exit(1)

# Check that no tokenizer was deepcopied
tokenizer_copied = any("Tokenizer" in call or call == "MockTokenizer" for call in deepcopy_calls)

if tokenizer_copied:
    print(f"FAIL: tokenizer was deepcopied (calls: {deepcopy_calls})")
    sys.exit(1)

# Check that something WAS deepcopied (otherwise deepcopy was removed entirely)
if not deepcopy_calls:
    print("FAIL: deepcopy was not called at all - must still deepcopy non-tokenizer attrs")
    sys.exit(1)

print(f"PASS: tokenizer not deepcopied (copied types: {deepcopy_calls})")
print(f"  Output keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
sys.exit(0)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_SKIP_TOKENIZER_DEEPCOPY)")
fi

# ── TEST 2 (PRIMARY): Behavioral - correct output from to_dict ──
# [pr_diff] (0.25): to_dict returns correct output structure
echo ""
echo "TEST 2: behavioral - correct to_dict output (weight=$W_BEHAV_CORRECT_OUTPUT)"
T2=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers')

from transformers.processing_utils import ProcessorMixin

class MockTokenizer:
    def __init__(self):
        self.vocab = {"hello": 1, "world": 2}
        self.name_or_path = "mock/tokenizer"

class MockImageProcessor:
    def __init__(self):
        self.size = {"height": 224, "width": 224}
        self.name_or_path = "mock/image_processor"

# Test processor
class TestProcessor(ProcessorMixin):
    attributes = ["tokenizer", "image_processor"]

    @classmethod
    def get_attributes(cls):
        return cls.attributes

    def __init__(self):
        self.tokenizer = MockTokenizer()
        self.image_processor = MockImageProcessor()
        self.chat_template = "{{ messages }}"
        self._processor_class = "TestProcessor"
        self.auto_map = None

processor = TestProcessor()

try:
    result = processor.to_dict()
except Exception as e:
    print(f"FAIL: to_dict raised exception: {e}")
    sys.exit(1)

# Verify output is a dict
if not isinstance(result, dict):
    print(f"FAIL: to_dict did not return a dict, got {type(result)}")
    sys.exit(1)

# Verify processor_class is set
if "processor_class" not in result:
    print("FAIL: processor_class not in output")
    sys.exit(1)

# Verify chat_template is NOT in output (should be deleted)
if "chat_template" in result:
    print("FAIL: chat_template should be excluded from output")
    sys.exit(1)

# Verify image_processor info is preserved (as it's not a tokenizer)
# The image_processor may or may not be in output depending on attrs_to_save logic
# but the key thing is tokenizer is NOT in output
if "tokenizer" in result:
    print("FAIL: tokenizer should not be in output dict")
    sys.exit(1)

print(f"PASS: to_dict returns correct structure")
print(f"  Keys: {list(result.keys())}")
sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_CORRECT_OUTPUT)")
fi

# ── TEST 3: Pass-to-pass - method structure preserved ──
# [pr_diff] (0.15): to_dict method exists with proper signature
echo ""
echo "TEST 3: pass-to-pass - method structure (weight=$W_P2P_STRUCTURE)"
T3=$(python3 << 'PYEOF'
import sys
import inspect
sys.path.insert(0, '/workspace/transformers')

from transformers.processing_utils import ProcessorMixin

# Verify to_dict exists
if not hasattr(ProcessorMixin, 'to_dict'):
    print("FAIL: ProcessorMixin.to_dict not found")
    sys.exit(1)

# Get signature
sig = inspect.signature(ProcessorMixin.to_dict)
params = list(sig.parameters.keys())

if 'self' not in params:
    print("FAIL: to_dict missing self parameter")
    sys.exit(1)

# Verify _get_modality_for_attribute still exists (used by the fix)
from transformers.processing_utils import _get_modality_for_attribute

if not callable(_get_modality_for_attribute):
    print("FAIL: _get_modality_for_attribute not callable")
    sys.exit(1)

print("PASS: method structure preserved")
sys.exit(0)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P_STRUCTURE)")
fi

# ── TEST 4: Pass-to-pass - functional tests ──
# [pr_diff] (0.15): Existing behavior still works
echo ""
echo "TEST 4: pass-to-pass - functional (weight=$W_P2P_FUNCTIONAL)"
T4=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers')

from transformers.processing_utils import ProcessorMixin

class MockImageProcessor:
    """Non-tokenizer processor component that should be preserved"""
    def __init__(self):
        self.size = 224

    def to_dict(self):
        return {"size": self.size}

class TestProcessor(ProcessorMixin):
    attributes = ["image_processor"]

    @classmethod
    def get_attributes(cls):
        return cls.attributes

    def __init__(self):
        self.image_processor = MockImageProcessor()
        self.chat_template = None

processor = TestProcessor()

try:
    result = processor.to_dict()
except Exception as e:
    print(f"FAIL: to_dict raised: {e}")
    sys.exit(1)

# Verify basic functionality
if not isinstance(result, dict):
    print("FAIL: result not a dict")
    sys.exit(1)

if "processor_class" not in result:
    print("FAIL: missing processor_class")
    sys.exit(1)

if result.get("processor_class") != "TestProcessor":
    print(f"FAIL: wrong processor_class: {result.get('processor_class')}")
    sys.exit(1)

print("PASS: functional P2P tests pass")
sys.exit(0)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P_FUNCTIONAL)")
fi

# ── TEST 5: Anti-stub - real implementation ──
# [agent_config] (0.10): Substantial implementation, not a stub
echo ""
echo "TEST 5: anti-stub (weight=$W_ANTISTUB)"
T5=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers')

import ast

# Read and parse the source
with open("/workspace/transformers/src/transformers/processing_utils.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find to_dict method
found_method = False
method_node = None

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ProcessorMixin":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "to_dict":
                found_method = True
                method_node = item
                break
        break

if not found_method:
    print("FAIL: to_dict method not found")
    sys.exit(1)

# Count actual statements in the method (not comments/docstrings)
def count_statements(node):
    """Count non-docstring statements in function"""
    count = 0
    for item in node.body:
        if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
            # Skip docstring
            continue
        if isinstance(item, ast.Pass):
            continue
        count += 1
    return count

stmt_count = count_statements(method_node)

if stmt_count < 5:
    print(f"FAIL: to_dict has only {stmt_count} statements - looks like a stub")
    sys.exit(1)

# Verify it does something meaningful (has loops, conditionals, or comprehensions)
has_meaningful_logic = False

for child in ast.walk(method_node):
    if isinstance(child, (ast.For, ast.If, ast.comprehension, ast.DictComp)):
        has_meaningful_logic = True
        break

if not has_meaningful_logic:
    print("FAIL: to_dict lacks meaningful control structures")
    sys.exit(1)

print(f"PASS: to_dict has {stmt_count} statements with control structures")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# ── Final score ──────────────────────────────────────────────────────────
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
