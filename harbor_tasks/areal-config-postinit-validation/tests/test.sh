#!/usr/bin/env bash
set +e
set -uo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="/workspace/AReaL"
cd "$REPO"

TOTAL=0.0
add() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

###############################################################################
# GATE: Syntax check — abort on failure
###############################################################################
# [pr_diff] (0.00): All modified files must be valid Python
GATE_PASS=1
for f in areal/api/cli_args.py areal/utils/data.py; do
    if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "GATE FAIL: $f has syntax errors"
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" -eq 0 ]; then
    echo "0.0" > "/logs/verifier/reward.txt"
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"structural":0.0}' \
        > "/logs/verifier/reward.json"
    exit 0
fi

###############################################################################
# Helper: extract NormConfig class from source and exec it
###############################################################################
EXTRACT_NORMCONFIG='
import re, sys
from dataclasses import dataclass, field

src = open("areal/api/cli_args.py").read()
match = re.search(
    r"(@dataclass\nclass NormConfig:.*?)(?=\n@dataclass\n|\nclass \w)",
    src, re.DOTALL
)
if not match:
    # Try alternate pattern: decorator with parens or extra decorators
    match = re.search(
        r"(@dataclass[^\n]*\nclass NormConfig:.*?)(?=\n@dataclass|\nclass \w)",
        src, re.DOTALL
    )
if not match:
    print("FAIL: Could not find NormConfig class")
    sys.exit(1)
class_src = match.group(1)
ns = {"__builtins__": __builtins__}
exec("from dataclasses import dataclass, field\n" + class_src, ns)
NormConfig = ns["NormConfig"]
'

###############################################################################
# Helper: extract a __post_init__ method from a class via AST,
# neutralize super().__post_init__(), and return it as a callable
###############################################################################
EXTRACT_POST_INIT='
import ast, textwrap, sys, logging
from types import SimpleNamespace

logger = logging.getLogger("test_extract")

def extract_post_init(filepath, classname):
    """Extract __post_init__ from classname, neutralize super() call, return callable."""
    src = open(filepath).read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == classname:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    lines = src.splitlines(keepends=True)
                    func_src = textwrap.dedent("".join(lines[item.lineno-1:item.end_lineno]))
                    # Neutralize super().__post_init__() so we can call in isolation
                    func_src = func_src.replace("super().__post_init__()", "pass")
                    ns = {"__builtins__": __builtins__, "ValueError": ValueError, "logger": logger}
                    exec(func_src, ns)
                    return ns["__post_init__"]
    return None
'

###############################################################################
# BEHAVIORAL: Fail-to-pass tests (0.65 total)
###############################################################################

# [pr_diff] (0.12): NormConfig(mean_level="invalid") raises ValueError at construction
python3 -c "
${EXTRACT_NORMCONFIG}
try:
    NormConfig(mean_level='invalid', std_level='batch', group_size=1)
    print('FAIL: NormConfig accepted invalid mean_level without raising')
    exit(1)
except (ValueError, TypeError) as e:
    print('PASS: NormConfig rejects invalid mean_level at construction')
" && add 0.12 || echo "FAIL: NormConfig mean_level validation"

# [pr_diff] (0.08): NormConfig(std_level="invalid") raises ValueError at construction
python3 -c "
${EXTRACT_NORMCONFIG}
try:
    NormConfig(mean_level='batch', std_level='invalid', group_size=1)
    print('FAIL: NormConfig accepted invalid std_level without raising')
    exit(1)
except (ValueError, TypeError) as e:
    print('PASS: NormConfig rejects invalid std_level at construction')
" && add 0.08 || echo "FAIL: NormConfig std_level validation"

# [pr_diff] (0.10): NormConfig(mean_level="group", group_size=0) raises ValueError
python3 -c "
${EXTRACT_NORMCONFIG}
try:
    NormConfig(mean_level='group', std_level='batch', group_size=0)
    print('FAIL: NormConfig accepted group_size=0 with group normalization')
    exit(1)
except (ValueError, TypeError) as e:
    print('PASS: NormConfig rejects group_size=0 with group normalization')
" && add 0.10 || echo "FAIL: NormConfig group_size validation"

# [pr_diff] (0.10): PPOActorConfig.__post_init__ rejects negative SAPO temperature
# WHY AST-EXTRACT: PPOActorConfig inherits from TrainEngineConfig → complex nested
# config types requiring torch, ray. We extract __post_init__, neutralize super(),
# and CALL it with a mock self — testing actual validation behavior, not string matching.
python3 -c "
${EXTRACT_POST_INIT}
from types import SimpleNamespace

post_init = extract_post_init('areal/api/cli_args.py', 'PPOActorConfig')
assert post_init is not None, 'PPOActorConfig.__post_init__ not found'

# Test: negative sapo_tau_pos should raise ValueError
mock_self = SimpleNamespace(
    use_sapo_loss=True,
    sapo_tau_pos=-1.0,
    sapo_tau_neg=0.5,
    use_decoupled_loss=False,
    behave_imp_weight_mode='disabled',
    behave_imp_weight_cap=None,
)
try:
    post_init(mock_self)
    print('FAIL: PPOActorConfig accepted negative sapo_tau_pos')
    exit(1)
except ValueError:
    print('PASS: PPOActorConfig rejects negative sapo_tau_pos')
except AttributeError:
    # Acceptable: might access other attrs we didn't mock — but the validation
    # for sapo temps should happen before accessing unrelated attrs
    print('FAIL: PPOActorConfig accesses other attrs before validating SAPO temps')
    exit(1)
" && add 0.10 || echo "FAIL: PPOActorConfig SAPO temp validation"

# [pr_diff] (0.05): PPOActorConfig.__post_init__ also rejects zero sapo_tau_neg
python3 -c "
${EXTRACT_POST_INIT}
from types import SimpleNamespace

post_init = extract_post_init('areal/api/cli_args.py', 'PPOActorConfig')
assert post_init is not None, 'PPOActorConfig.__post_init__ not found'

mock_self = SimpleNamespace(
    use_sapo_loss=True,
    sapo_tau_pos=1.0,
    sapo_tau_neg=0.0,
    use_decoupled_loss=False,
    behave_imp_weight_mode='disabled',
    behave_imp_weight_cap=None,
)
try:
    post_init(mock_self)
    print('FAIL: PPOActorConfig accepted zero sapo_tau_neg')
    exit(1)
except ValueError:
    print('PASS: PPOActorConfig rejects zero sapo_tau_neg')
except AttributeError:
    print('FAIL: PPOActorConfig accesses other attrs before validating SAPO temps')
    exit(1)
" && add 0.05 || echo "FAIL: PPOActorConfig SAPO tau_neg validation"

# [pr_diff] (0.10): PPOActorConfig.__post_init__ rejects SAPO + decoupled_loss combo
python3 -c "
${EXTRACT_POST_INIT}
from types import SimpleNamespace

post_init = extract_post_init('areal/api/cli_args.py', 'PPOActorConfig')
assert post_init is not None, 'PPOActorConfig.__post_init__ not found'

mock_self = SimpleNamespace(
    use_sapo_loss=True,
    sapo_tau_pos=1.0,
    sapo_tau_neg=1.0,
    use_decoupled_loss=True,
    behave_imp_weight_mode='disabled',
    behave_imp_weight_cap=None,
)
try:
    post_init(mock_self)
    print('FAIL: PPOActorConfig accepted SAPO + decoupled_loss')
    exit(1)
except ValueError:
    print('PASS: PPOActorConfig rejects SAPO + decoupled_loss')
except AttributeError:
    print('FAIL: PPOActorConfig accesses other attrs before SAPO+decoupled check')
    exit(1)
" && add 0.10 || echo "FAIL: PPOActorConfig SAPO+decoupled check"

# [pr_diff] (0.10): BaseExperimentConfig.__post_init__ validates total_train_epochs > 0
# WHY AST-EXTRACT: BaseExperimentConfig has complex nested config deps. Extract + call.
python3 -c "
${EXTRACT_POST_INIT}
from types import SimpleNamespace

post_init = extract_post_init('areal/api/cli_args.py', 'BaseExperimentConfig')
assert post_init is not None, 'BaseExperimentConfig.__post_init__ not found'

mock_self = SimpleNamespace(
    total_train_epochs=0,
)
try:
    post_init(mock_self)
    print('FAIL: BaseExperimentConfig accepted total_train_epochs=0')
    exit(1)
except ValueError:
    print('PASS: BaseExperimentConfig rejects total_train_epochs=0')
except AttributeError:
    print('FAIL: BaseExperimentConfig accesses other attrs before epochs check')
    exit(1)
" && add 0.10 || echo "FAIL: BaseExperimentConfig epochs validation"

###############################################################################
# REGRESSION: Pass-to-pass (0.10)
###############################################################################

# [pr_diff] (0.05): Valid NormConfig values still construct without error
python3 -c "
${EXTRACT_NORMCONFIG}

# Default construction should work
c = NormConfig()
assert c.mean_level == 'batch'
assert c.std_level == 'batch'
assert c.group_size == 1

# Valid group config should work
c2 = NormConfig(mean_level='group', std_level='batch', group_size=4)
assert c2.group_size == 4

# None levels should work
c3 = NormConfig(mean_level=None, std_level=None)
print('PASS: Valid NormConfig defaults construct OK')
" && add 0.05 || echo "FAIL: NormConfig valid defaults"

# [pr_diff] (0.05): Normalization.__init__ no longer has redundant mean_level/std_level validation
python3 -c "
import ast

src = open('areal/utils/data.py').read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'Normalization':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                # Walk AST nodes looking for raise statements that mention mean_level/std_level
                init_src = ast.get_source_segment(src, item)
                # Check both string patterns and AST raise nodes
                has_redundant = False
                for child in ast.walk(item):
                    if isinstance(child, ast.Raise) and child.exc is not None:
                        raise_src = ast.get_source_segment(src, child)
                        if raise_src and ('mean_level' in raise_src or 'std_level' in raise_src):
                            has_redundant = True
                if 'mean_level not in' in init_src or 'std_level not in' in init_src:
                    has_redundant = True
                assert not has_redundant, \
                    'Normalization.__init__ still has redundant mean_level/std_level validation'
                print('PASS: Normalization.__init__ no longer has redundant validation')
                exit(0)

print('FAIL: Could not find Normalization.__init__')
exit(1)
" && add 0.05 || echo "FAIL: Normalization redundant validation"

###############################################################################
# CONFIG-DERIVED (0.10)
###############################################################################

# [agent_config] (0.05): Validation uses ValueError (AST node check, not string match) — .claude/rules/api-config.md:37-38 @ 03d71153
python3 -c "
import ast

src = open('areal/api/cli_args.py').read()
tree = ast.parse(src)

target_classes = {'NormConfig', 'PPOActorConfig', 'BaseExperimentConfig'}
found_raise = {}

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name in target_classes:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__post_init__':
                has_raise = False
                uses_valueerror = True
                for child in ast.walk(item):
                    if isinstance(child, ast.Raise) and child.exc is not None:
                        has_raise = True
                        # Check that the raised exception is ValueError
                        exc = child.exc
                        if isinstance(exc, ast.Call):
                            exc = exc.func
                        if isinstance(exc, ast.Name) and exc.id != 'ValueError':
                            uses_valueerror = False
                        elif isinstance(exc, ast.Attribute) and exc.attr != 'ValueError':
                            uses_valueerror = False
                if has_raise:
                    found_raise[node.name] = uses_valueerror

# At least NormConfig should have raise ValueError (it's the core of the fix)
assert 'NormConfig' in found_raise, 'NormConfig.__post_init__ has no raise statements'
assert found_raise['NormConfig'], 'NormConfig should raise ValueError, not other exception types'
print('PASS: Validation uses ValueError (AST node verified)')
" && add 0.05 || echo "FAIL: ValueError check"

# [agent_config] (0.05): No wildcard imports — CLAUDE.md:88 @ 03d71153
python3 -c "
import ast
for f in ['areal/api/cli_args.py', 'areal/utils/data.py']:
    tree = ast.parse(open(f).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and any(
            alias.name == '*' for alias in node.names
        ):
            print(f'FAIL: Wildcard import in {f}: from {node.module} import *')
            exit(1)
print('PASS: no wildcard imports')
" && add 0.05 || echo "FAIL: wildcard imports found"

###############################################################################
# STRUCTURAL: Anti-stub + consistency (0.15)
###############################################################################

# [pr_diff] (0.05): NormConfig.__post_init__ has real validation (not just comments/pass)
python3 -c "
import ast

src = open('areal/api/cli_args.py').read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'NormConfig':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__post_init__':
                # Count meaningful statements (not Pass, not Expr with string constants)
                meaningful = 0
                for stmt in ast.walk(item):
                    if isinstance(stmt, ast.If):
                        meaningful += 1
                    elif isinstance(stmt, ast.Raise):
                        meaningful += 1
                    elif isinstance(stmt, ast.Assert):
                        meaningful += 1
                    elif isinstance(stmt, ast.Assign):
                        meaningful += 1
                assert meaningful >= 2, \
                    f'NormConfig.__post_init__ has only {meaningful} meaningful statements (stub?)'
                print('PASS: NormConfig has __post_init__ with real validation')
                exit(0)

print('FAIL: NormConfig missing __post_init__')
exit(1)
" && add 0.05 || echo "FAIL: NormConfig __post_init__ anti-stub"

# [pr_diff] (0.05): BaseExperimentConfig.__post_init__ has real validation
python3 -c "
import ast

src = open('areal/api/cli_args.py').read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'BaseExperimentConfig':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__post_init__':
                meaningful = 0
                for stmt in ast.walk(item):
                    if isinstance(stmt, (ast.If, ast.Raise, ast.Assert, ast.Assign)):
                        meaningful += 1
                assert meaningful >= 1, \
                    f'BaseExperimentConfig.__post_init__ has {meaningful} meaningful statements'
                print('PASS: BaseExperimentConfig has __post_init__')
                exit(0)

print('FAIL: BaseExperimentConfig missing __post_init__')
exit(1)
" && add 0.05 || echo "FAIL: BaseExperimentConfig __post_init__ anti-stub"

# [pr_diff] (0.05): PPOActorConfig.__post_init__ calls super().__post_init__()
python3 -c "
import ast

src = open('areal/api/cli_args.py').read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'PPOActorConfig':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__post_init__':
                # Check for super().__post_init__() call via AST nodes
                for child in ast.walk(item):
                    if isinstance(child, ast.Call):
                        func = child.func
                        if (isinstance(func, ast.Attribute)
                            and func.attr == '__post_init__'
                            and isinstance(func.value, ast.Call)
                            and isinstance(func.value.func, ast.Name)
                            and func.value.func.id == 'super'):
                            print('PASS: PPOActorConfig calls super().__post_init__()')
                            exit(0)
                print('FAIL: PPOActorConfig.__post_init__ does not call super().__post_init__()')
                exit(1)

print('FAIL: PPOActorConfig.__post_init__ not found')
exit(1)
" && add 0.05 || echo "FAIL: PPOActorConfig super() call"

###############################################################################
# TOTAL
###############################################################################
echo ""
echo "Total score: $TOTAL"
echo "$TOTAL" > "/logs/verifier/reward.txt"

python3 -c "
import json
total = $TOTAL
behavioral = min(0.65, total)
remainder = max(0, total - 0.65)
regression = min(0.10, remainder)
remainder = max(0, remainder - 0.10)
config = min(0.10, remainder)
remainder = max(0, remainder - 0.10)
structural = min(0.15, remainder)
print(json.dumps({
    'reward': total,
    'behavioral': round(behavioral, 2),
    'regression': round(regression, 2),
    'config': round(config, 2),
    'structural': round(structural, 2),
    'style_rubric': 0.0
}))
" > "/logs/verifier/reward.json"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
