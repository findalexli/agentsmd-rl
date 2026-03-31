#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/tests/models/smollm3/test_modeling_smollm3.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[f2p_dosample_in_generate]=0.30
WEIGHTS[f2p_no_temperature]=0.20
WEIGHTS[f2p_expected_text_changed]=0.10
WEIGHTS[regression_structure]=0.10
WEIGHTS[antistub]=0.10
WEIGHTS[config_ruff]=0.05
WEIGHTS[config_tests_existing]=0.10
WEIGHTS[p2p_syntax]=0.05

for key in f2p_dosample_in_generate f2p_no_temperature f2p_expected_text_changed regression_structure antistub config_ruff config_tests_existing p2p_syntax; do
    RESULTS[$key]=0
done

# ========== GATE: Syntax check ==========
python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error in test file"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: syntax OK"

# ========== PASS-TO-PASS (0.05): File parses and imports don't break ==========
# [regression] (0.05): File must be valid Python that parses cleanly
echo "=== P2P: syntax valid ==="
RESULTS[p2p_syntax]=1
echo "TEST p2p_syntax: PASS (covered by gate)"

# ========== FAIL-TO-PASS 1 (0.30): All generate() calls in integration tests use do_sample=False ==========
# [pr_diff] (0.30): Integration tests must pass do_sample=False as a keyword arg to generate()
# to ensure greedy decoding, because the model's generation_config has do_sample=True by default.
# Cannot call generate() — requires 3B model weights + GPU. AST check justified.
echo "=== F2P: do_sample=False in all generate() calls ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/tests/models/smollm3/test_modeling_smollm3.py") as f:
    src = f.read()
tree = ast.parse(src)

# Find SmolLM3IntegrationTest class
integration_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SmolLM3IntegrationTest":
        integration_class = node
        break

if integration_class is None:
    print("FAIL: SmolLM3IntegrationTest class not found")
    sys.exit(1)

# Collect all .generate() calls inside the integration test class
generate_calls = []
for node in ast.walk(integration_class):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "generate":
        generate_calls.append(node)

if len(generate_calls) == 0:
    print("FAIL: no generate() calls found in SmolLM3IntegrationTest")
    sys.exit(1)

# Every generate() call must have do_sample=False as a keyword argument
for call in generate_calls:
    kw_names = {kw.arg for kw in call.keywords if kw.arg is not None}
    if "do_sample" not in kw_names:
        print(f"FAIL: generate() at line {call.lineno} missing do_sample keyword arg")
        sys.exit(1)
    for kw in call.keywords:
        if kw.arg == "do_sample":
            # Must be the literal False
            if not (isinstance(kw.value, ast.Constant) and kw.value.value is False):
                print(f"FAIL: generate() at line {call.lineno} has do_sample but not set to False")
                sys.exit(1)

print(f"PASS: all {len(generate_calls)} generate() calls have do_sample=False")
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_dosample_in_generate]=1 && echo "TEST f2p_dosample_in_generate: PASS" || echo "TEST f2p_dosample_in_generate: FAIL"

# ========== FAIL-TO-PASS 2 (0.20): No temperature kwarg in generate() calls ==========
# [pr_diff] (0.20): temperature=0 doesn't override do_sample=True from generation_config.
# The fix must remove temperature and use do_sample=False instead.
# Cannot call generate() — requires 3B model weights + GPU. AST check justified.
echo "=== F2P: no temperature in generate() calls ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/tests/models/smollm3/test_modeling_smollm3.py") as f:
    src = f.read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SmolLM3IntegrationTest":
        for item in ast.walk(node):
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute) and item.func.attr == "generate":
                for kw in item.keywords:
                    if kw.arg == "temperature":
                        print(f"FAIL: generate() at line {item.lineno} still uses temperature kwarg")
                        sys.exit(1)
print("PASS: no temperature kwarg in integration test generate() calls")
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_no_temperature]=1 && echo "TEST f2p_no_temperature: PASS" || echo "TEST f2p_no_temperature: FAIL"

# ========== FAIL-TO-PASS 3 (0.10): Buggy expected text removed ==========
# [pr_diff] (0.10): The old expected text was generated with temperature=0 + do_sample=True
# (non-deterministic). Any correct fix must update the expected text to match true greedy output.
# We check the OLD text is gone — we don't require a specific constant name or new value.
echo "=== F2P: buggy expected text removed ==="
python3 << 'PYEOF'
import sys

with open("/workspace/transformers/tests/models/smollm3/test_modeling_smollm3.py") as f:
    src = f.read()

# These are fragments of the old expected text from the buggy version.
# Any correct fix must change these because greedy output differs from sampled output.
old_fragments = [
    "pulls objects toward the center of the Earth",
]

for frag in old_fragments:
    if frag in src:
        print(f"FAIL: old expected text fragment still present: '{frag}'")
        sys.exit(1)

# Must still have some form of expected output assertion (any string comparison)
# Accept any of: assertEqual, assertIn, assert_close, ==, EXPECTED_, expected_
import ast
tree = ast.parse(src)
has_assertion = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SmolLM3IntegrationTest":
        for item in ast.walk(node):
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute):
                if item.func.attr in ("assertEqual", "assertIn", "assertTrue", "assert_close"):
                    has_assertion = True
                    break
        break

if not has_assertion:
    print("FAIL: no assertions found in SmolLM3IntegrationTest")
    sys.exit(1)

print("PASS: old expected text removed, assertions present")
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_expected_text_changed]=1 && echo "TEST f2p_expected_text_changed: PASS" || echo "TEST f2p_expected_text_changed: FAIL"

# ========== REGRESSION (0.10): Test class and method structure preserved ==========
# [regression] (0.10): All original classes and integration test methods must still exist
echo "=== Regression: test structure ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/tests/models/smollm3/test_modeling_smollm3.py") as f:
    src = f.read()
tree = ast.parse(src)

required_classes = {"SmolLM3IntegrationTest", "SmolLM3ModelTest", "SmolLM3ModelTester"}
required_methods = {"test_model_3b_generation", "test_model_3b_long_prompt", "test_model_3b_logits"}

found_classes = set()
found_methods = set()
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        found_classes.add(node.name)
        if node.name == "SmolLM3IntegrationTest":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    found_methods.add(item.name)

missing_classes = required_classes - found_classes
missing_methods = required_methods - found_methods

if missing_classes:
    print(f"FAIL: missing classes: {missing_classes}")
    sys.exit(1)
if missing_methods:
    print(f"FAIL: missing methods: {missing_methods}")
    sys.exit(1)
print("PASS: all required classes and methods present")
PYEOF
[ $? -eq 0 ] && RESULTS[regression_structure]=1 && echo "TEST regression_structure: PASS" || echo "TEST regression_structure: FAIL"

# ========== ANTI-STUB (0.10): Integration test methods have real bodies ==========
# [regression] (0.10): Test methods must not be stubbed out
echo "=== Anti-stub ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/tests/models/smollm3/test_modeling_smollm3.py") as f:
    src = f.read()

# File length check
lines = len(src.splitlines())
if lines < 100:
    print(f"FAIL: file too short ({lines} lines), likely stubbed")
    sys.exit(1)

tree = ast.parse(src)

# Each integration test method must have a non-trivial body
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SmolLM3IntegrationTest":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name.startswith("test_model_3b"):
                # Count meaningful statements (not docstrings, not pass, not ellipsis)
                meaningful = 0
                for stmt in ast.walk(item):
                    if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                         ast.Expr, ast.Return, ast.Assert,
                                         ast.If, ast.For, ast.With, ast.Call)):
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
                            continue  # skip docstrings
                        meaningful += 1
                if meaningful < 3:
                    print(f"FAIL: {item.name} has only {meaningful} meaningful statements, likely stubbed")
                    sys.exit(1)
        break

print(f"PASS: file has {lines} lines, integration test methods have real bodies")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ========== CONFIG-DERIVED (0.05): ruff format check ==========
# [agent_config] (0.05): "make style runs formatters and linters (ruff)" — CLAUDE.md:2 @ 9cd278715c
echo "=== Config: ruff format ==="
if command -v ruff &>/dev/null; then
    ruff check "$TARGET" --select E,W --quiet 2>/dev/null
    if [ $? -eq 0 ]; then
        RESULTS[config_ruff]=1
        echo "TEST config_ruff: PASS"
    else
        echo "TEST config_ruff: FAIL"
    fi
else
    RESULTS[config_ruff]=1
    echo "TEST config_ruff: PASS (ruff not available, skipped)"
fi

# ========== CONFIG-DERIVED (0.10): Tests added to existing file ==========
# [agent_config] (0.10): "When writing tests, they should be added to an existing file" — .github/copilot-instructions.md:15 @ 9cd278715c
echo "=== Config: tests in existing file ==="
python3 << 'PYEOF'
import subprocess, sys
result = subprocess.run(
    ["git", "diff", "--name-status", "HEAD"],
    cwd="/workspace/transformers", capture_output=True, text=True
)
diff_output = result.stdout.strip()
if not diff_output:
    result = subprocess.run(
        ["git", "diff", "--name-status", "HEAD~1", "HEAD"],
        cwd="/workspace/transformers", capture_output=True, text=True
    )
    diff_output = result.stdout.strip()

for line in diff_output.splitlines():
    parts = line.split('\t')
    if len(parts) >= 2 and parts[0] == 'A' and 'test' in parts[1].lower():
        print(f"FAIL: new test file created: {parts[1]}")
        sys.exit(1)

print("PASS: no new test files created")
PYEOF
[ $? -eq 0 ] && RESULTS[config_tests_existing]=1 && echo "TEST config_tests_existing: PASS" || echo "TEST config_tests_existing: FAIL"

# ========== SCORE COMPUTATION ==========
SCORE=$(python3 -c "
w = {
    'f2p_dosample_in_generate': ${WEIGHTS[f2p_dosample_in_generate]},
    'f2p_no_temperature': ${WEIGHTS[f2p_no_temperature]},
    'f2p_expected_text_changed': ${WEIGHTS[f2p_expected_text_changed]},
    'regression_structure': ${WEIGHTS[regression_structure]},
    'antistub': ${WEIGHTS[antistub]},
    'config_ruff': ${WEIGHTS[config_ruff]},
    'config_tests_existing': ${WEIGHTS[config_tests_existing]},
    'p2p_syntax': ${WEIGHTS[p2p_syntax]},
}
r = {
    'f2p_dosample_in_generate': ${RESULTS[f2p_dosample_in_generate]},
    'f2p_no_temperature': ${RESULTS[f2p_no_temperature]},
    'f2p_expected_text_changed': ${RESULTS[f2p_expected_text_changed]},
    'regression_structure': ${RESULTS[regression_structure]},
    'antistub': ${RESULTS[antistub]},
    'config_ruff': ${RESULTS[config_ruff]},
    'config_tests_existing': ${RESULTS[config_tests_existing]},
    'p2p_syntax': ${RESULTS[p2p_syntax]},
}
total = sum(w[k]*r[k] for k in w)
print(f'{total:.2f}')
")
echo ""
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
