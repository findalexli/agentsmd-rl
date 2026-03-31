#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/src/transformers/models/auto/processing_auto.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.55
WEIGHTS[regression]=0.20
WEIGHTS[structural]=0.15
WEIGHTS[antistub]=0.10

# LLM rubric is additive, not part of weighted sum
LLM_JUDGE_WEIGHT=0.10

for key in behavioral regression structural antistub; do
    RESULTS[$key]=0
done

# ---------- GATE 1: Python syntax validity ----------
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: file has syntax errors -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: syntax valid"

# ---------- GATE 2: File is not stubbed ----------
python3 << 'PYEOF'
import ast, sys
TARGET = "/workspace/transformers/src/transformers/models/auto/processing_auto.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find from_pretrained method in AutoProcessor
has_from_pretrained = False
has_cached_file_kwargs_logic = False
has_cached_file_call = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "AutoProcessor":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "from_pretrained":
                has_from_pretrained = True
                # Check for cached_file_kwargs assignment
                for stmt in ast.walk(item):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Name) and target.id == "cached_file_kwargs":
                                has_cached_file_kwargs_logic = True
                    if isinstance(stmt, ast.Call):
                        if isinstance(stmt.func, ast.Name) and stmt.func.id == "cached_file":
                            has_cached_file_call = True
                        elif isinstance(stmt.func, ast.Attribute) and stmt.func.attr == "get":
                            # cached_file.get() pattern
                            has_cached_file_call = True

if not has_from_pretrained:
    print("GATE FAIL: AutoProcessor.from_pretrained not found")
    sys.exit(1)

if not has_cached_file_kwargs_logic:
    print("GATE FAIL: cached_file_kwargs construction not found")
    sys.exit(1)

if not has_cached_file_call:
    print("GATE FAIL: cached_file call not found")
    sys.exit(1)

print("GATE PASS: from_pretrained method intact with cached_file_kwargs logic")
sys.exit(0)
PYEOF
if [ $? -ne 0 ]; then
    echo "STUB GATE FAIL: implementation incomplete -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

BEHAVIORAL_PASSED=0

# ---------- PRIMARY BEHAVIORAL (55%): Verify kwargs are forwarded correctly ----------
# [pr_diff] (0.55): Hub kwargs are correctly extracted and forwarded to cached_file
python3 << 'PYEOF'
import ast
import sys
import textwrap
import json

TARGET = "/workspace/transformers/src/transformers/models/auto/processing_auto.py"

with open(TARGET) as f:
    source = f.read()
    tree = ast.parse(source)

# Extract the from_pretrained method and related functions
# We need to create a test that verifies hub kwargs are forwarded

# First, verify inspect.signature is NOT used for filtering (this is the bug)
if "inspect.signature(cached_file)" in source or "inspect.signature" in source and "cached_file" in source:
    # Check if inspect is still actually used for cached_file filtering (bug not fixed)
    # Look for the specific buggy pattern: inspect.signature(cached_file).parameters
    if "inspect.signature(cached_file)" in source:
        print("BEHAVIORAL FAIL: Still using inspect.signature(cached_file) to filter kwargs (bug not fixed)")
        sys.exit(1)
    # If inspect.signature is used elsewhere, that's okay as long as not for cached_file filtering

# Verify there's an explicit tuple/list of hub kwargs being used
# AND that cached_file_kwargs uses that tuple for filtering

found_explicit_kwargs = False
filtered_kwargs_var = None

# Find the from_pretrained method
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "AutoProcessor":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "from_pretrained":
                # Look for a tuple/list of hub kwargs
                for stmt in ast.walk(item):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Name):
                                # Check if value is a tuple of hub-related strings
                                if isinstance(stmt.value, (ast.Tuple, ast.List)):
                                    hub_kw_names = ["cache_dir", "force_download", "proxies", "token",
                                                   "revision", "local_files_only", "subfolder", "repo_type", "user_agent"]
                                    found_items = []
                                    for elt in stmt.value.elts:
                                        if isinstance(elt, ast.Constant) and elt.value in hub_kw_names:
                                            found_items.append(elt.value)
                                    if len(found_items) >= 5:  # At least 5 of the 9 hub kwargs
                                        found_explicit_kwargs = True
                                        filtered_kwargs_var = target.id
                                        print(f"Found explicit kwargs tuple: {target.id} = {found_items}")

                    # Check that cached_file_kwargs is built using the explicit tuple
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Name) and target.id == "cached_file_kwargs":
                                # Look for pattern: {k: kwargs[k] for k in EXPLICIT_TUPLE if k in kwargs}
                                if isinstance(stmt.value, ast.DictComp):
                                    # Check if iterating over our explicit tuple
                                    iter_node = stmt.value.iter
                                    if isinstance(iter_node, ast.Name) and iter_node.id == filtered_kwargs_var:
                                        print(f"BEHAVIORAL PASS: cached_file_kwargs built from explicit tuple '{filtered_kwargs_var}'")
                                        sys.exit(0)
                                    # Also check for direct tuple usage
                                    if isinstance(iter_node, (ast.Tuple, ast.List)):
                                        print("BEHAVIORAL PASS: cached_file_kwargs built from explicit tuple literal")
                                        sys.exit(0)

if not found_explicit_kwargs:
    print("BEHAVIORAL FAIL: No explicit tuple/list of hub kwargs found")
    sys.exit(1)

print("BEHAVIORAL FAIL: Explicit kwargs found but cached_file_kwargs doesn't use it correctly")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    BEHAVIORAL_PASSED=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- REGRESSION (20%): cached_file still receives kwargs ----------
# [pr_diff] (0.20): cached_file is called with the filtered kwargs
if [ $BEHAVIORAL_PASSED -eq 1 ]; then
    python3 << 'PYEOF'
import ast, sys
TARGET = "/workspace/transformers/src/transformers/models/auto/processing_auto.py"

with open(TARGET) as f:
    source = f.read()
    tree = ast.parse(source)

# Find cached_file call with **cached_file_kwargs
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = node.func
        # Check for cached_file(...) or cached_file.get(...)
        is_cached_file_call = False
        if isinstance(func, ast.Name) and func.id == "cached_file":
            is_cached_file_call = True
        elif isinstance(func, ast.Attribute) and func.attr in ["get", "cached_file"]:
            is_cached_file_call = True

        if is_cached_file_call:
            # Check if **cached_file_kwargs is in the keywords
            for kw in node.keywords:
                if kw.arg is None:  # **kwargs syntax
                    if isinstance(kw.value, ast.Name) and kw.value.id == "cached_file_kwargs":
                        print("REGRESSION PASS: cached_file called with **cached_file_kwargs")
                        sys.exit(0)

print("REGRESSION PASS: cached_file call pattern found")
sys.exit(0)
PYEOF
    if [ $? -eq 0 ]; then
        RESULTS[regression]=1
        echo "TEST regression: PASS"
    else
        echo "TEST regression: FAIL"
    fi
else
    echo "TEST regression: SKIPPED (behavioral failed)"
fi

# ---------- STRUCTURAL (15%): Import inspect removed ----------
# [pr_diff] (0.15): Remove unused import inspect (only counts if behavioral passes)
if [ $BEHAVIORAL_PASSED -eq 1 ]; then
    python3 << 'PYEOF'
import ast, sys
TARGET = "/workspace/transformers/src/transformers/models/auto/processing_auto.py"

with open(TARGET) as f:
    source = f.read()
    tree = ast.parse(source)

# Check for import inspect
has_inspect_import = False
inspect_usage_count = 0

for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name == "inspect":
                has_inspect_import = True
    elif isinstance(node, ast.ImportFrom):
        if node.module == "inspect":
            has_inspect_import = True

# Count actual usages of inspect.
if has_inspect_import:
    # Count "inspect." usages (excluding comments)
    lines = source.split('\n')
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('#') and 'inspect.' in line:
            inspect_usage_count += 1

    if inspect_usage_count == 0:
        print("STRUCTURAL FAIL: 'import inspect' present but unused")
        sys.exit(1)
    else:
        print(f"STRUCTURAL PASS: 'import inspect' used {inspect_usage_count} time(s) elsewhere")
        sys.exit(0)
else:
    print("STRUCTURAL PASS: 'import inspect' not present")
    sys.exit(0)
PYEOF
    if [ $? -eq 0 ]; then
        RESULTS[structural]=1
        echo "TEST structural: PASS"
    else
        echo "TEST structural: FAIL"
    fi
else
    echo "TEST structural: SKIPPED (behavioral failed)"
fi

# ---------- ANTI-STUB (10%): Substantive implementation ----------
# [agent_config] (0.10): File has substantial non-trivial implementation
if [ $BEHAVIORAL_PASSED -eq 1 ]; then
    python3 << 'PYEOF'
import ast, sys
TARGET = "/workspace/transformers/src/transformers/models/auto/processing_auto.py"

with open(TARGET) as f:
    source = f.read()
    tree = ast.parse(source)

# Count meaningful AST nodes (not just comments/whitespace)
num_classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
num_functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
num_imports = len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])

# Check from_pretrained has substantial body
from_pretrained_size = 0
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "AutoProcessor":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "from_pretrained":
                from_pretrained_size = len(item.body)

if num_classes >= 1 and num_functions >= 2 and from_pretrained_size >= 10:
    print("ANTI-STUB PASS: Substantive implementation")
    sys.exit(0)
else:
    print(f"ANTI-STUB FAIL: classes={num_classes}, functions={num_functions}, from_pretrained stmts={from_pretrained_size}")
    sys.exit(1)
PYEOF
    if [ $? -eq 0 ]; then
        RESULTS[antistub]=1
        echo "TEST antistub: PASS"
    else
        echo "TEST antistub: FAIL"
    fi
else
    echo "TEST antistub: SKIPPED (behavioral failed)"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral': ${WEIGHTS[behavioral]}, 'regression': ${WEIGHTS[regression]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral': ${RESULTS[behavioral]}, 'regression': ${RESULTS[regression]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral (${WEIGHTS[behavioral]}): ${RESULTS[behavioral]}"
echo "  regression (${WEIGHTS[regression]}): ${RESULTS[regression]}"
echo "  structural (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub   (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  LLM_JUDGE  (+${LLM_JUDGE_WEIGHT} conditional): ${LLM_JUDGE}"
echo "  TOTAL (det): $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
