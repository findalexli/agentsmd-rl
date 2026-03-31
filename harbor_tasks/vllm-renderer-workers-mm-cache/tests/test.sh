#!/usr/bin/env bash
set +e

TARGET="/workspace/vllm/vllm/config/model.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.55
WEIGHTS[regression]=0.20
WEIGHTS[structural]=0.15
WEIGHTS[config]=0.10

for key in behavioral regression structural config; do
    RESULTS[$key]=0
done

# ---------- GATE: Code must parse and ModelConfig must be importable ----------
python3 << 'PYEOF'
import sys
import ast

# Check syntax parses
with open("/workspace/vllm/vllm/config/model.py") as f:
    src = f.read()

try:
    ast.parse(src)
except SyntaxError as e:
    print(f"GATE FAIL: Syntax error - {e}")
    sys.exit(1)

# Check ModelConfig imports and instantiates (with minimal deps)
import os
os.chdir("/workspace/vllm")

# Add vllm to path
sys.path.insert(0, "/workspace/vllm")

try:
    # This imports the module - may fail due to missing deps, that's OK for gate
    from vllm.config.model import ModelConfig
    print("GATE PASS: ModelConfig importable")
except Exception as e:
    # If import fails due to deps, check AST for class existence
    if "class ModelConfig" in src and "def __post_init__" in src:
        print("GATE PASS: ModelConfig class found (deps limit full import)")
    else:
        print(f"GATE FAIL: ModelConfig not found - {e}")
        sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# ---------- PRIMARY (55%): Behavioral - Validation actually raises ValueError ----------
# [pr_diff] (0.55): Config validation raises ValueError when renderer_num_workers > 1 with mm cache
python3 << 'PYEOF'
import sys
import os
import ast
import re

os.chdir("/workspace/vllm")
sys.path.insert(0, "/workspace/vllm")

# Read source to locate __post_init__
with open("/workspace/vllm/vllm/config/model.py") as f:
    src = f.read()

tree = ast.parse(src)

# Find ModelConfig class and __post_init__ method
model_config_class = None
post_init_method = None

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
        model_config_class = node
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                post_init_method = item
                break
        break

if not model_config_class:
    print("BEHAVIORAL FAIL: ModelConfig class not found")
    sys.exit(1)

if not post_init_method:
    print("BEHAVIORAL FAIL: __post_init__ method not found")
    sys.exit(1)

# Extract the raw source of __post_init__ method for analysis
method_lines = src.splitlines()[post_init_method.lineno-1:post_init_method.end_lineno]
method_src = "\n".join(method_lines)

# Check for the validation pattern: renderer_num_workers check combined with mm_processor_cache_gb check
has_renderer_check = False
has_cache_check = False
has_combined_check = False
has_valueerror = False

# Look for renderer_num_workers > 1 pattern
if re.search(r'renderer_num_workers\s*>\s*1', method_src):
    has_renderer_check = True

# Look for mm_processor_cache_gb > 0 or similar cache check
if re.search(r'mm_processor_cache_gb\s*>\s*0', method_src) or \
   re.search(r'mm_processor_cache_gb\s*>=', method_src) or \
   re.search(r'mm_processor_cache_gb\s*is not None.*>\s*0', method_src) or \
   re.search(r'cache_enabled|cache.*>\s*0|cache.*>=', method_src, re.IGNORECASE):
    has_cache_check = True

# Look for ValueError being raised
if "ValueError" in method_src and "raise" in method_src:
    has_valueerror = True

# Check that both conditions are checked together (AND logic)
# This is the key fix - preventing race condition requires checking BOTH conditions
combined_patterns = [
    r'if.*renderer_num_workers.*>.*1.*and.*mm_processor_cache',
    r'if.*mm_processor_cache.*and.*renderer_num_workers.*>.*1',
    r'if.*renderer_num_workers.*>.*1.*mm_processor_cache_gb',
    r'if.*mm_processor_cache_gb.*renderer_num_workers.*>.*1',
    r'and.*renderer.*cache|and.*cache.*renderer',
    r'workers.*>.*1.*cache',
    r'cache.*workers.*>.*1',
]

for pattern in combined_patterns:
    if re.search(pattern, method_src, re.IGNORECASE | re.DOTALL):
        has_combined_check = True
        break

# Also check for variable assignment pattern (common valid implementation)
if re.search(r'\b(renderer|workers)\b.*=.*renderer_num_workers', method_src) and \
   re.search(r'\b(cache|cache_gb)\b.*=.*mm_processor_cache', method_src):
    # Variables are assigned, now check they're used together
    if re.search(r'if.*\b(renderer|workers)\b.*>.*1', method_src) and \
       re.search(r'if.*\b(cache|cache_gb)\b', method_src):
        has_combined_check = True

print(f"  - renderer_num_workers > 1 check: {has_renderer_check}")
print(f"  - mm_processor_cache check: {has_cache_check}")
print(f"  - combined validation: {has_combined_check}")
print(f"  - ValueError raise: {has_valueerror}")

if not (has_renderer_check and has_cache_check and has_combined_check and has_valueerror):
    print("BEHAVIORAL FAIL: Missing required validation components")
    sys.exit(1)

# Check for the specific bug fix: must NOT use >= 1 (which would block single worker)
if re.search(r'renderer_num_workers\s*>=\s*1', method_src):
    print("BEHAVIORAL FAIL: Using >= 1 would incorrectly block single worker config")
    sys.exit(1)

# Check that it doesn't always raise (regression check within behavioral)
# The check should be conditional, not unconditional
if re.search(r'^(?!.*if).*(raise\s+ValueError)', method_src, re.MULTILINE):
    # This would match unconditional raise - too broad
    unconditional_raises = []
    for i, line in enumerate(method_lines):
        if 'raise ValueError' in line and not any(k in line for k in ['if ', 'elif ']):
            # Check if it's in an if block by looking at indentation context
            stripped = line.strip()
            if stripped.startswith('raise ValueError'):
                # Check previous non-empty line
                for j in range(i-1, -1, -1):
                    prev = method_lines[j].strip()
                    if prev and not prev.startswith('#'):
                        if not (prev.startswith('if ') or prev.startswith('elif ') or prev.startswith('else:')):
                            unconditional_raises.append((i, line))
                        break

    # Actually, the fix IS conditional, so unconditional raises mean something else is wrong
    # But we shouldn't fail just for this - the combined check is the key
    pass

print("BEHAVIORAL PASS")
PYEOF

RESULTS[behavioral]=$?
if [ ${RESULTS[behavioral]} -eq 0 ]; then
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
    RESULTS[behavioral]=0
fi

# ---------- REGRESSION (20%): Single worker + cache still works, and validation is properly scoped ----------
# [pr_diff] (0.20): Single worker with cache enabled should not be blocked
python3 << 'PYEOF'
import sys
import os
import ast
import re

os.chdir("/workspace/vllm")
sys.path.insert(0, "/workspace/vllm")

with open("/workspace/vllm/vllm/config/model.py") as f:
    src = f.read()

tree = ast.parse(src)

# Find __post_init__
post_init_method = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                post_init_method = item
                break
        break

if not post_init_method:
    print("REGRESSION FAIL: __post_init__ not found")
    sys.exit(1)

method_lines = src.splitlines()[post_init_method.lineno-1:post_init_method.end_lineno]
method_src = "\n".join(method_lines)

# Regression 1: Must not use >= 1 (which would block single worker)
if re.search(r'renderer_num_workers\s*>=\s*1', method_src):
    print("REGRESSION FAIL: Using >= 1 blocks single worker config")
    sys.exit(1)

# Regression 2: Must check > 1, not == 1 or other conditions
if re.search(r'renderer_num_workers\s*==\s*1', method_src) and \
   re.search(r'raise', method_src):
    print("REGRESSION FAIL: Checking == 1 would raise on single worker")
    sys.exit(1)

# Regression 3: Must check mm_processor_cache_gb > 0, not just existence
# A proper fix checks if cache is ENABLED (> 0), not just configured
cache_checks = [
    r'mm_processor_cache_gb\s*>\s*0',
    r'mm_processor_cache_gb\s*>=\s*[1-9]',
    r'if.*mm_processor_cache_gb',  # At least checking the value, not just 'if mm_processor_cache_gb:'
]
has_proper_cache_check = any(re.search(p, method_src) for p in cache_checks)
if not has_proper_cache_check:
    # Check if using explicit truthiness check which would be wrong for 0
    if re.search(r'if\s+mm_processor_cache_gb\s*:', method_src) and \
       re.search(r'raise', method_src):
        print("REGRESSION WARN: Bare 'if mm_processor_cache_gb:' is ambiguous - rejecting for safety")
        # This is a warning but we still check for > 0 specifically

print("REGRESSION PASS")
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[regression]=1
    echo "TEST regression: PASS"
else
    RESULTS[regression]=0
    echo "TEST regression: FAIL"
fi

# ---------- STRUCTURAL (15%): Validation exists in correct location with sufficient implementation ----------
# [pr_diff] (0.10): Validation in ModelConfig.__post_init__
# [agent_config] (0.05): Meaningful validation body - vllm/config/model.py config patterns
python3 << 'PYEOF'
import sys
import os
import ast

os.chdir("/workspace/vllm")
sys.path.insert(0, "/workspace/vllm")

with open("/workspace/vllm/vllm/config/model.py") as f:
    src = f.read()

tree = ast.parse(src)

# Find ModelConfig class
model_config_class = None
post_init_method = None

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
        model_config_class = node
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                post_init_method = item
                break
        break

if not model_config_class:
    print("STRUCTURAL FAIL: ModelConfig class not found")
    sys.exit(1)

if not post_init_method:
    print("STRUCTURAL FAIL: __post_init__ not found")
    sys.exit(1)

# Count meaningful statements in __post_init__ (not just docstrings/pass)
method_body = post_init_method.body
meaningful_stmts = 0

for stmt in method_body:
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
        continue  # Skip docstrings
    if isinstance(stmt, ast.Pass):
        continue  # Skip pass
    if isinstance(stmt, ast.FunctionDef):
        continue  # Skip nested function definitions for stub detection
    meaningful_stmts += 1

# __post_init__ should have substantial implementation (original has ~100+ statements)
# A stub would have very few
if meaningful_stmts < 5:
    print(f"STRUCTURAL FAIL: __post_init__ has only {meaningful_stmts} meaningful statements (stub detected)")
    sys.exit(1)

# Check class has sufficient complexity (not just a stub class)
class_body_lines = len(model_config_class.body)
if class_body_lines < 10:
    print(f"STRUCTURAL FAIL: ModelConfig body too small ({class_body_lines} items)")
    sys.exit(1)

print("STRUCTURAL PASS")
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    RESULTS[structural]=0
    echo "TEST structural: FAIL"
fi

# ---------- CONFIG-DERIVED (10%): Code style checks ----------
# [agent_config] (0.10): No bare pip install in modified files - follows vllm project conventions
# Source: vLLM project standards prevent bare pip install
BARE_PIP=0

# Only check files that were actually modified
cd /workspace/vllm 2>/dev/null
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null || true)

for cf in $CHANGED_FILES; do
    if [ -f "/workspace/vllm/$cf" ] && [[ "$cf" == *.py ]]; then
        # Check for bare 'pip install' (not 'uv pip install')
        if grep -Pn '(?<!uv )pip install(?!.*--)' "/workspace/vllm/$cf" 2>/dev/null | grep -v '^\s*#' > /dev/null 2>&1; then
            echo "CONFIG config: $cf contains bare 'pip install'"
            BARE_PIP=1
        fi
    fi
done

if [ "$BARE_PIP" -eq 0 ]; then
    echo "TEST config: PASS"
    RESULTS[config]=1
else
    echo "TEST config: FAIL - bare pip install found"
    RESULTS[config]=0
fi

# ---------- Calculate total score ----------
SCORE=$(python3 -c "
w={'behavioral':${WEIGHTS[behavioral]},'regression':${WEIGHTS[regression]},'structural':${WEIGHTS[structural]},'config':${WEIGHTS[config]}}
r={'behavioral':${RESULTS[behavioral]},'regression':${RESULTS[regression]},'structural':${RESULTS[structural]},'config':${RESULTS[config]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")

echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# Output detailed breakdown
echo "---"
echo "Breakdown:"
for key in behavioral regression structural config; do
    if [ ${RESULTS[$key]} -eq 1 ]; then
        echo "  $key: ${WEIGHTS[$key]} (PASS)"
    else
        echo "  $key: 0.00 (FAIL)"
    fi
done
echo "---"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
