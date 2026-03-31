#!/usr/bin/env bash
set +e

REPO="/repo"
REWARD=0.0

add() {
    REWARD=$(python3 -c "print(round($REWARD + $1, 4))")
}

# ===== GATE: Syntax check =====
# [pr_diff] (gate): All changed files must parse
for f in \
    vllm/transformers_utils/processors/pixtral.py \
    vllm/transformers_utils/processors/voxtral.py \
    vllm/model_executor/models/pixtral.py \
    vllm/model_executor/models/voxtral.py; do
    if ! python3 -c "import ast; ast.parse(open('${REPO}/${f}').read())" 2>/dev/null; then
        echo "GATE FAIL: ${f} has syntax errors"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done
echo "GATE PASSED"

# ===== F2P BEHAVIORAL (0.30): Pixtral processor accepts and uses image_processor =====
# [pr_diff] (0.30): Constructor must accept image_processor kwarg and store it (not create internally)
# AST-extract + exec justified: module imports torch, mistral_common, transformers — cannot import
P1=0
python3 << 'PYEOF'
import ast, textwrap, sys

class Mock:
    """Universal mock that handles any attribute chain or call."""
    def __getattr__(self, name): return Mock()
    def __call__(self, *a, **kw): return Mock()
    def __bool__(self): return True
    def __iter__(self): return iter([])

source = open("/repo/vllm/transformers_utils/processors/pixtral.py").read()
tree = ast.parse(source)
lines = source.splitlines(keepends=True)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "MistralCommonPixtralProcessor":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                found = True
                func_src = textwrap.dedent("".join(lines[item.lineno-1:item.end_lineno]))
                ns = {
                    "__builtins__": __builtins__,
                    "MistralCommonImageProcessor": Mock,
                    "ProcessorMixin": type("PM", (), {}),
                }
                class_src = "class TestProc:\n" + textwrap.indent(func_src, "    ")
                exec(class_src, ns)
                TestProc = ns["TestProc"]

                # Create a sentinel with a unique marker
                class Sentinel:
                    mm_encoder = Mock()
                    def __getattr__(self, name): return Mock()
                sentinel = Sentinel()
                sentinel._is_sentinel = True

                obj = object.__new__(TestProc)
                mock_tok = Mock()

                # Behavioral test: call __init__ with image_processor keyword
                try:
                    TestProc.__init__(obj, mock_tok, image_processor=sentinel)
                except TypeError as e:
                    print(f"FAIL: __init__ rejects image_processor keyword: {e}")
                    sys.exit(1)

                # Verify self.image_processor was set from the parameter (not created internally)
                if not hasattr(obj, "image_processor"):
                    print("FAIL: self.image_processor not set after __init__")
                    sys.exit(1)
                if not (hasattr(obj.image_processor, "_is_sentinel") and obj.image_processor._is_sentinel is True):
                    print("FAIL: self.image_processor created internally, not from parameter")
                    sys.exit(1)

                print("PASS: Pixtral processor accepts image_processor and stores it from param")
                sys.exit(0)
        break

if not found:
    print("FAIL: MistralCommonPixtralProcessor.__init__ not found")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && P1=1
[ "$P1" = "1" ] && add 0.30

# ===== F2P BEHAVIORAL (0.30): Voxtral processor accepts and uses feature_extractor =====
# [pr_diff] (0.30): Constructor must accept feature_extractor kwarg and store it (not create internally)
# AST-extract + exec justified: module imports torch, mistral_common, transformers — cannot import
P2=0
python3 << 'PYEOF'
import ast, textwrap, sys

class Mock:
    def __getattr__(self, name): return Mock()
    def __call__(self, *a, **kw): return Mock()
    def __bool__(self): return True
    def __iter__(self): return iter([])

source = open("/repo/vllm/transformers_utils/processors/voxtral.py").read()
tree = ast.parse(source)
lines = source.splitlines(keepends=True)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "MistralCommonVoxtralProcessor":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                found = True
                func_src = textwrap.dedent("".join(lines[item.lineno-1:item.end_lineno]))
                ns = {
                    "__builtins__": __builtins__,
                    "MistralCommonFeatureExtractor": Mock,
                    "ProcessorMixin": type("PM", (), {}),
                }
                class_src = "class TestProc:\n" + textwrap.indent(func_src, "    ")
                exec(class_src, ns)
                TestProc = ns["TestProc"]

                class Sentinel:
                    audio_encoder = Mock()
                    def __getattr__(self, name): return Mock()
                sentinel = Sentinel()
                sentinel._is_sentinel = True

                obj = object.__new__(TestProc)
                mock_tok = Mock()

                try:
                    TestProc.__init__(obj, mock_tok, feature_extractor=sentinel)
                except TypeError as e:
                    print(f"FAIL: __init__ rejects feature_extractor keyword: {e}")
                    sys.exit(1)

                if not hasattr(obj, "feature_extractor"):
                    print("FAIL: self.feature_extractor not set after __init__")
                    sys.exit(1)
                if not (hasattr(obj.feature_extractor, "_is_sentinel") and obj.feature_extractor._is_sentinel is True):
                    print("FAIL: self.feature_extractor created internally, not from parameter")
                    sys.exit(1)

                print("PASS: Voxtral processor accepts feature_extractor and stores it from param")
                sys.exit(0)
        break

if not found:
    print("FAIL: MistralCommonVoxtralProcessor.__init__ not found")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && P2=1
[ "$P2" = "1" ] && add 0.30

# ===== F2P STRUCTURAL (0.10): Pixtral model get_image_processor + integration =====
# [pr_diff] (0.10): Model info class must have get_image_processor AND get_hf_processor must pass it
# AST justified: pixtral.py imports torch, vllm CUDA internals — cannot import
P3=0
python3 << 'PYEOF'
import ast, sys

source = open("/repo/vllm/model_executor/models/pixtral.py").read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if not isinstance(node, ast.ClassDef):
        continue
    methods = {item.name: item for item in node.body
               if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
    if "get_image_processor" not in methods or "get_hf_processor" not in methods:
        continue

    # Sub-check A: get_image_processor has a substantive return (not pass/None)
    gip = methods["get_image_processor"]
    has_return = False
    for s in ast.walk(gip):
        if isinstance(s, ast.Return) and s.value is not None:
            if not (isinstance(s.value, ast.Constant) and s.value.value is None):
                has_return = True
                break
    if not has_return:
        print("FAIL: get_image_processor has no substantive return statement")
        sys.exit(1)

    # Sub-check B: get_hf_processor references image_processor
    # (keyword arg, variable name, or call to self.get_image_processor)
    ghp = methods["get_hf_processor"]
    found_ref = False
    for s in ast.walk(ghp):
        if isinstance(s, ast.keyword) and s.arg == "image_processor":
            found_ref = True; break
        if isinstance(s, ast.Name) and s.id == "image_processor":
            found_ref = True; break
        if (isinstance(s, ast.Call) and isinstance(s.func, ast.Attribute)
                and s.func.attr == "get_image_processor"):
            found_ref = True; break
    if not found_ref:
        print("FAIL: get_hf_processor does not reference image_processor")
        sys.exit(1)

    print(f"PASS: {node.name} has get_image_processor + integration in get_hf_processor")
    sys.exit(0)

print("FAIL: no class with both get_image_processor and get_hf_processor")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && P3=1
[ "$P3" = "1" ] && add 0.10

# ===== F2P STRUCTURAL (0.10): Voxtral model get_feature_extractor + integration =====
# [pr_diff] (0.10): Model info class must have get_feature_extractor AND get_hf_processor must pass it
# AST justified: voxtral.py imports torch, vllm CUDA internals — cannot import
P4=0
python3 << 'PYEOF'
import ast, sys

source = open("/repo/vllm/model_executor/models/voxtral.py").read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if not isinstance(node, ast.ClassDef):
        continue
    methods = {item.name: item for item in node.body
               if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
    if "get_feature_extractor" not in methods or "get_hf_processor" not in methods:
        continue

    gfe = methods["get_feature_extractor"]
    has_return = False
    for s in ast.walk(gfe):
        if isinstance(s, ast.Return) and s.value is not None:
            if not (isinstance(s.value, ast.Constant) and s.value.value is None):
                has_return = True
                break
    if not has_return:
        print("FAIL: get_feature_extractor has no substantive return statement")
        sys.exit(1)

    ghp = methods["get_hf_processor"]
    found_ref = False
    for s in ast.walk(ghp):
        if isinstance(s, ast.keyword) and s.arg == "feature_extractor":
            found_ref = True; break
        if isinstance(s, ast.Name) and s.id == "feature_extractor":
            found_ref = True; break
        if (isinstance(s, ast.Call) and isinstance(s.func, ast.Attribute)
                and s.func.attr == "get_feature_extractor"):
            found_ref = True; break
    if not found_ref:
        print("FAIL: get_hf_processor does not reference feature_extractor")
        sys.exit(1)

    print(f"PASS: {node.name} has get_feature_extractor + integration in get_hf_processor")
    sys.exit(0)

print("FAIL: no class with both get_feature_extractor and get_hf_processor")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && P4=1
[ "$P4" = "1" ] && add 0.10

# ===== P2P REGRESSION (0.10): get_hf_processor preserved in both model files =====
# [pr_diff] (0.10): Existing get_hf_processor API must not be removed
P5=0
python3 << 'PYEOF'
import ast, sys

for path in [
    "/repo/vllm/model_executor/models/pixtral.py",
    "/repo/vllm/model_executor/models/voxtral.py",
]:
    tree = ast.parse(open(path).read())
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_hf_processor":
            found = True
            break
    if not found:
        print(f"FAIL: {path} missing get_hf_processor")
        sys.exit(1)

print("PASS: get_hf_processor preserved in both model files")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && P5=1
[ "$P5" = "1" ] && add 0.10

# ===== ANTI-STUB (0.10): Changed files are not trivially small =====
# [pr_diff] (0.10): Changed files must not be stubs or near-empty
P6=0
python3 << 'PYEOF'
import sys
for f in [
    "/repo/vllm/transformers_utils/processors/pixtral.py",
    "/repo/vllm/transformers_utils/processors/voxtral.py",
    "/repo/vllm/model_executor/models/pixtral.py",
    "/repo/vllm/model_executor/models/voxtral.py",
]:
    lines = len(open(f).readlines())
    if lines < 50:
        print(f"FAIL: {f} too short ({lines} lines) — likely a stub")
        sys.exit(1)
print("PASS: all files substantial")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && P6=1
[ "$P6" = "1" ] && add 0.10

# ===== SUMMARY =====
echo ""
echo "=== RESULTS ==="
echo "Pixtral processor behavioral:     ${P1} (0.30)"
echo "Voxtral processor behavioral:     ${P2} (0.30)"
echo "Pixtral model integration:        ${P3} (0.10)"
echo "Voxtral model integration:        ${P4} (0.10)"
echo "P2P get_hf_processor preserved:   ${P5} (0.10)"
echo "Anti-stub:                        ${P6} (0.10)"
echo ""
echo "Total reward: ${REWARD}"

echo "${REWARD}" > /logs/verifier/reward.txt

BEH=$(python3 -c "print(round(${P1}*0.30 + ${P2}*0.30, 4))")
STR=$(python3 -c "print(round(${P3}*0.10 + ${P4}*0.10, 4))")
REG=$(python3 -c "print(round(${P5}*0.10 + ${P6}*0.10, 4))")
python3 -c "
import json
data = {
    'reward': ${REWARD},
    'behavioral': ${BEH},
    'structural': ${STR},
    'regression': ${REG},
    'config': 0.0,
    'style_rubric': 0.0,
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
print(json.dumps(data))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
