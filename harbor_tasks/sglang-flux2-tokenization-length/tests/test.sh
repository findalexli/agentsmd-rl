#!/usr/bin/env bash
set +e

TARGET="/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_f2p]=0.35
WEIGHTS[behavioral_klein]=0.30
WEIGHTS[behavioral_p2p]=0.15
WEIGHTS[structural]=0.10
WEIGHTS[antistub]=0.05
WEIGHTS[config]=0.05

for key in behavioral_f2p behavioral_klein behavioral_p2p structural antistub config; do
    RESULTS[$key]=0
done

# ===== GATE: Code must be syntactically valid =====
python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi

# ===== PRIMARY 1 (35%): Flux2PipelineConfig overrides text_encoder_extra_args to 512 =====
# [pr_diff] (0.35): Flux2PipelineConfig must override text_encoder_extra_args with max_length=512
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py"

def check_flux2_override():
    """Check that Flux2PipelineConfig overrides text_encoder_extra_args with max_length=512."""
    with open(TARGET) as f:
        src = f.read()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Flux2PipelineConfig":
            # Find text_encoder_extra_args field with max_length=512
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and item.target.id == "text_encoder_extra_args":
                    # Check the default_factory is a lambda or list with max_length=512
                    if isinstance(item.value, ast.List):
                        # Direct list assignment
                        for elt in item.value.elts:
                            if isinstance(elt, ast.Dict):
                                for k, v in zip(elt.keys, elt.values):
                                    if isinstance(k, ast.Constant) and k.value == "max_length":
                                        if isinstance(v, ast.Constant) and v.value == 512:
                                            print("PASS: Flux2PipelineConfig.text_encoder_extra_args has max_length=512")
                                            sys.exit(0)
                    elif isinstance(item.value, ast.Call):
                        # field(default_factory=lambda: [...])
                        if isinstance(item.value.func, ast.Name) and item.value.func.id == "field":
                            for kw in item.value.keywords:
                                if kw.arg == "default_factory":
                                    # Check if lambda returns list with max_length=512
                                    if isinstance(kw.value, ast.Lambda):
                                        body = kw.value.body
                                        if isinstance(body, ast.List):
                                            for elt in body.elts:
                                                if isinstance(elt, ast.Dict):
                                                    for k, v in zip(elt.keys, elt.values):
                                                        if isinstance(k, ast.Constant) and k.value == "max_length":
                                                            if isinstance(v, ast.Constant) and v.value == 512:
                                                                print("PASS: Flux2PipelineConfig.text_encoder_extra_args has max_length=512")
                                                                sys.exit(0)
            break

    print("FAIL: Flux2PipelineConfig does not properly override text_encoder_extra_args with max_length=512")
    sys.exit(1)

check_flux2_override()
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_f2p]=1

# ===== PRIMARY 2 (30%): Klein ignores inbound max_length and forces 512 =====
# [pr_diff] (0.30): Klein must ignore tok_kwargs['max_length'] and always use 512
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py"

def check_klein_enforcement():
    """
    Check that Flux2KleinPipelineConfig.tokenize_prompt:
    1. Pops max_length from tok_kwargs (doesn't use it)
    2. Explicitly sets max_length = 512 (not from kwargs)
    """
    with open(TARGET) as f:
        src = f.read()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Flux2KleinPipelineConfig":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "tokenize_prompt":
                    func_body = "\n".join(src.splitlines()[item.lineno-1:item.end_lineno])
                    body_ast = item

                    # Check 1: tok_kwargs.pop("max_length", ...) is called
                    has_pop = False
                    for stmt in ast.walk(body_ast):
                        if isinstance(stmt, ast.Call):
                            if isinstance(stmt.func, ast.Attribute):
                                if stmt.func.attr == "pop":
                                    # Check if popping "max_length"
                                    if stmt.args and isinstance(stmt.args[0], ast.Constant):
                                        if stmt.args[0].value == "max_length":
                                            has_pop = True

                    # Check 2: max_length = 512 assignment exists (not from popped value)
                    has_explicit_512 = False
                    for stmt in body_ast.body:
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Name) and target.id == "max_length":
                                    if isinstance(stmt.value, ast.Constant) and stmt.value.value == 512:
                                        has_explicit_512 = True

                    if has_pop and has_explicit_512:
                        print("PASS: Klein tokenize_prompt pops max_length and explicitly sets 512")
                        sys.exit(0)
                    else:
                        print(f"FAIL: Klein missing pop={has_pop}, explicit_512={has_explicit_512}")
                        sys.exit(1)

    print("FAIL: Could not find Flux2KleinPipelineConfig.tokenize_prompt")
    sys.exit(1)

check_klein_enforcement()
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_klein]=1

# ===== P2P Check (15%): Parent FluxPipelineConfig behavior preserved =====
# [repo_tests] (0.15): FluxPipelineConfig still has max_length=77 in text_encoder_extra_args
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py"

def check_parent_unchanged():
    """Ensure parent FluxPipelineConfig still uses max_length=77 (not accidentally changed)."""
    with open(TARGET) as f:
        src = f.read()
    tree = ast.parse(src)

    found_77 = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "FluxPipelineConfig":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and hasattr(item.target, 'id'):
                    if item.target.id == "text_encoder_extra_args":
                        # Check for max_length=77 in the value
                        for child in ast.walk(item.value):
                            if isinstance(child, ast.Constant) and child.value == 77:
                                found_77 = True
                                break

    if found_77:
        print("PASS: FluxPipelineConfig still uses max_length=77")
        sys.exit(0)
    else:
        print("FAIL: FluxPipelineConfig max_length=77 was modified")
        sys.exit(1)

check_parent_unchanged()
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_p2p]=1

# ===== STRUCTURAL (10%): Both config classes exist =====
# [agent_config] (0.10): Flux2PipelineConfig and Flux2KleinPipelineConfig exist
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py"

def check_classes_exist():
    with open(TARGET) as f:
        src = f.read()
    tree = ast.parse(src)

    classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}

    required = {"Flux2PipelineConfig", "Flux2KleinPipelineConfig"}
    if required.issubset(classes):
        print("PASS: Both Flux2 config classes exist")
        sys.exit(0)
    else:
        missing = required - classes
        print(f"FAIL: Missing classes: {missing}")
        sys.exit(1)

check_classes_exist()
PYEOF
RESULTS[structural]=$?

# ===== ANTI-STUB (5%): Meaningful implementation =====
# [static] (0.05): tokenize_prompt methods have meaningful body
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py"

def check_not_stub():
    with open(TARGET) as f:
        src = f.read()
    tree = ast.parse(src)

    min_lines = 100
    total_lines = len(src.splitlines())

    # Count actual statements (not just pass/ellipsis/docstrings)
    stmt_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "tokenize_prompt":
            for stmt in node.body:
                if isinstance(stmt, ast.Pass):
                    continue
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                    # Docstring
                    continue
                stmt_count += 1

    if total_lines > min_lines and stmt_count >= 4:
        print("PASS: Non-stub implementation")
        sys.exit(0)
    else:
        print(f"FAIL: Lines={total_lines}, tokenize_prompt stmts={stmt_count}")
        sys.exit(1)

check_not_stub()
PYEOF
RESULTS[antistub]=$?

# ===== CONFIG-DERIVED (5%): Test file main guard =====
# [agent_config] (0.05): "Run ruff format and check test files have __main__ guard"
# Source: python/sglang/multimodal_gen/.claude/skills/write-sglang-test/SKILL.md:8-10 @ edd4d540
cd /workspace/sglang 2>/dev/null
NEW_TEST_FILES=$(git diff --name-only --diff-filter=A HEAD 2>/dev/null | grep -E '^test/.*\.py$' || true)
if [ -z "$NEW_TEST_FILES" ]; then
    RESULTS[config]=1
else
    ALL_OK=1
    for tf in $NEW_TEST_FILES; do
        python3 -c "import ast; tree = ast.parse(open('/workspace/sglang/$tf').read()); exits = [node for node in ast.walk(tree) if isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__']; sys.exit(0 if exits else 1)" 2>/dev/null
        if [ $? -ne 0 ]; then
            ALL_OK=0
            break
        fi
    done
    [ "$ALL_OK" -eq 1 ] && RESULTS[config]=1
fi

# Calculate total score
SCORE=$(python3 -c "
w={'behavioral_f2p':${WEIGHTS[behavioral_f2p]},'behavioral_klein':${WEIGHTS[behavioral_klein]},'behavioral_p2p':${WEIGHTS[behavioral_p2p]},'structural':${WEIGHTS[structural]},'antistub':${WEIGHTS[antistub]},'config':${WEIGHTS[config]}}
r={'behavioral_f2p':${RESULTS[behavioral_f2p]},'behavioral_klein':${RESULTS[behavioral_klein]},'behavioral_p2p':${RESULTS[behavioral_p2p]},'structural':${RESULTS[structural]},'antistub':${RESULTS[antistub]},'config':${RESULTS[config]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")

echo "TOTAL: $SCORE"
echo "Details: f2p=${RESULTS[behavioral_f2p]} klein=${RESULTS[behavioral_klein]} p2p=${RESULTS[behavioral_p2p]} struct=${RESULTS[structural]} stub=${RESULTS[antistub]} config=${RESULTS[config]}"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
