"""
Task: slime-glm4v-moe-bridge-layer-spec
Repo: THUDM/slime @ e4d22dc929169fcc2cdf538d1798d9a5473f4d1d
PR:   1738

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/slime"
FILE = Path(f"{REPO}/slime_plugins/megatron_bridge/glm4v_moe.py")


def _parse():
    src = FILE.read_text()
    return src, ast.parse(src)


def _find_method(tree, method_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            return node
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_valid():
    """glm4v_moe.py must parse without syntax errors."""
    src = FILE.read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

_MOE_FREQ_TYPE_SCRIPT = '''\
import ast, sys
from pathlib import Path

src = Path("slime_plugins/megatron_bridge/glm4v_moe.py").read_text()
tree = ast.parse(src)

# Find provider_bridge method
provider_bridge = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "provider_bridge":
        provider_bridge = node
        break

if not provider_bridge:
    print("FAIL: provider_bridge method not found", file=sys.stderr)
    sys.exit(1)

# Find the moe_layer_freq variable assignment and extract its RHS expression
rhs_src = None
for child in ast.walk(provider_bridge):
    if isinstance(child, ast.Assign):
        for target in child.targets:
            if isinstance(target, ast.Name) and "moe_layer_freq" in target.id:
                rhs_src = ast.get_source_segment(src, child.value)
                break
        if rhs_src:
            break

if not rhs_src:
    # Fallback: check the keyword arg value directly
    for child in ast.walk(provider_bridge):
        if isinstance(child, ast.keyword) and child.arg == "moe_layer_freq":
            rhs_src = ast.get_source_segment(src, child.value)
            break

if not rhs_src:
    print("FAIL: Could not find moe_layer_freq computation", file=sys.stderr)
    sys.exit(1)

# Execute the expression with realistic mock values
ns = {"first_k_dense": 1, "num_layers": 46}
result = eval(rhs_src, {"__builtins__": __builtins__}, ns)

if isinstance(result, str):
    print(f"FAIL: moe_layer_freq evaluates to string: {result!r}", file=sys.stderr)
    sys.exit(1)

if not isinstance(result, (list, tuple)):
    print(f"FAIL: moe_layer_freq is {type(result).__name__}, expected list", file=sys.stderr)
    sys.exit(1)

print("PASS")
'''

_MOE_FREQ_VALUES_SCRIPT = '''\
import ast, sys
from pathlib import Path

src = Path("slime_plugins/megatron_bridge/glm4v_moe.py").read_text()
tree = ast.parse(src)

# Find provider_bridge method
provider_bridge = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "provider_bridge":
        provider_bridge = node
        break

if not provider_bridge:
    print("FAIL: provider_bridge not found", file=sys.stderr)
    sys.exit(1)

# Extract the moe_layer_freq RHS expression
rhs_src = None
for child in ast.walk(provider_bridge):
    if isinstance(child, ast.Assign):
        for target in child.targets:
            if isinstance(target, ast.Name) and "moe_layer_freq" in target.id:
                rhs_src = ast.get_source_segment(src, child.value)
                break
        if rhs_src:
            break

if not rhs_src:
    print("FAIL: Could not extract moe_layer_freq expression", file=sys.stderr)
    sys.exit(1)

# Test with multiple (first_k_dense, num_layers) configurations
configs = [(1, 46), (2, 10), (0, 5), (3, 3)]
for dk, nl in configs:
    ns = {
        "first_k_dense": dk,
        "num_layers": nl,
        "num_hidden_layers": nl,
        "first_k_dense_replace": dk,
    }
    result = eval(rhs_src, {"__builtins__": __builtins__}, ns)
    if not isinstance(result, (list, tuple)):
        print(f"FAIL: Not a list for dk={dk}, nl={nl}: {type(result).__name__}", file=sys.stderr)
        sys.exit(1)
    if len(result) != nl:
        print(f"FAIL: Length {len(result)} != {nl} for dk={dk}, nl={nl}", file=sys.stderr)
        sys.exit(1)
    for i in range(dk):
        if result[i] != 0:
            print(f"FAIL: Layer {i} should be dense (0), got {result[i]}", file=sys.stderr)
            sys.exit(1)
    for i in range(dk, nl):
        if result[i] != 1:
            print(f"FAIL: Layer {i} should be MoE (1), got {result[i]}", file=sys.stderr)
            sys.exit(1)

print("PASS")
'''


def test_moe_layer_freq_is_list():
    """moe_layer_freq must evaluate to a list, not a string expression."""
    r = subprocess.run(
        ["python3", "-c", _MOE_FREQ_TYPE_SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Unexpected output: {r.stdout}"


def test_moe_layer_freq_values_correct():
    """moe_layer_freq list has correct dense/MoE pattern for varied configs."""
    r = subprocess.run(
        ["python3", "-c", _MOE_FREQ_VALUES_SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Unexpected output: {r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — AST structural checks (megatron not installable)
# ---------------------------------------------------------------------------

def test_provide_uses_decoder_block_spec():
    """provide() must call get_gpt_decoder_block_spec, not the old function."""
    _, tree = _parse()
    provide = _find_method(tree, "provide")
    assert provide is not None, "provide() method not found"

    calls = set()
    for child in ast.walk(provide):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                calls.add(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                calls.add(child.func.attr)

    assert "get_gpt_layer_with_transformer_engine_spec" not in calls, (
        "Still using old get_gpt_layer_with_transformer_engine_spec"
    )
    assert "get_gpt_decoder_block_spec" in calls, (
        "get_gpt_decoder_block_spec not called in provide()"
    )


def test_provide_passes_config_to_spec():
    """get_gpt_decoder_block_spec must receive a config argument."""
    _, tree = _parse()
    provide = _find_method(tree, "provide")
    assert provide is not None

    for child in ast.walk(provide):
        if isinstance(child, ast.Call):
            name = None
            if isinstance(child.func, ast.Name):
                name = child.func.id
            elif isinstance(child.func, ast.Attribute):
                name = child.func.attr
            if name == "get_gpt_decoder_block_spec":
                kw_names = {kw.arg for kw in child.keywords}
                has_config_kw = "config" in kw_names
                has_positional = len(child.args) >= 1
                assert has_config_kw or has_positional, (
                    "get_gpt_decoder_block_spec called without config"
                )
                return

    raise AssertionError("get_gpt_decoder_block_spec call not found in provide()")


def test_imports_decoder_block_spec():
    """Must import get_gpt_decoder_block_spec, not the old function."""
    _, tree = _parse()

    imported_names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names[alias.asname or alias.name] = alias.name

    for real_name in imported_names.values():
        assert real_name != "get_gpt_layer_with_transformer_engine_spec", (
            "Still imports get_gpt_layer_with_transformer_engine_spec"
        )

    found = any(
        v == "get_gpt_decoder_block_spec" for v in imported_names.values()
    )
    assert found, "get_gpt_decoder_block_spec not imported"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_key_classes_exist():
    """Core classes must still be defined."""
    _, tree = _parse()
    classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    required = {"Glm4vMoeVLModel", "Glm4vMoeVLModelProvider", "Glm4vMoeBridge"}
    missing = required - classes
    assert not missing, f"Missing classes: {missing}"


def test_key_methods_not_stubbed():
    """Core methods must have real logic, not stubs."""
    _, tree = _parse()

    required_methods = {
        "Glm4vMoeVLModelProvider": ["provide"],
        "Glm4vMoeBridge": ["provider_bridge"],
        "Glm4vMoeVLModel": ["__init__", "forward"],
    }
    for cls_name, methods in required_methods.items():
        cls_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == cls_name:
                cls_node = node
                break
        assert cls_node is not None, f"Class {cls_name} not found"

        found = {}
        for item in ast.walk(cls_node):
            if isinstance(item, ast.FunctionDef) and item.name in methods:
                stmts = sum(
                    1 for s in ast.walk(item)
                    if isinstance(s, (ast.Assign, ast.Return, ast.If, ast.For,
                                      ast.Call, ast.AugAssign, ast.AnnAssign))
                )
                found[item.name] = stmts

        for m in methods:
            assert m in found, f"{cls_name}.{m} not found"
            assert found[m] >= 3, (
                f"{cls_name}.{m} has only {found[m]} statements (likely stub)"
            )


def test_file_not_stub():
    """File must not be stubbed out — needs substantial content."""
    lines = [
        l for l in FILE.read_text().splitlines()
        if l.strip() and not l.strip().startswith("#")
    ]
    assert len(lines) >= 150, (
        f"File too short ({len(lines)} non-empty non-comment lines), likely stubbed"
    )
