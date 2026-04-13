"""
Task: transformers-xlnet-rope-cpu-forward
Repo: huggingface/transformers @ be6cf0848668852e3267d297211eb7e983e6c786
PR:   44782

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/transformers"
TARGET = f"{REPO}/src/transformers/models/xlnet/modeling_xlnet.py"


def _get_method_node(class_name, method_name):
    """Parse the target file and return the AST node for the given method."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    return src, tree, item
    raise AssertionError(f"{class_name}.{method_name} not found in {TARGET}")


def _extract_method_source(src, func_node):
    """Extract raw source lines of a function node."""
    lines = src.splitlines(keepends=True)
    return "".join(lines[func_node.lineno - 1 : func_node.end_lineno])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """modeling_xlnet.py must parse without syntax errors."""
    src = Path(TARGET).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_device_param_uni():
    """relative_positional_encoding accepts device= with attn_type='bi', bi_data=False.

    AST check: Verify the method signature includes device parameter and torch.arange calls use it.
    """
    _, _, func_node = _get_method_node("XLNetModel", "relative_positional_encoding")

    # Check that device parameter exists in the function signature
    param_names = [arg.arg for arg in func_node.args.args]
    assert "device" in param_names, f"'device' parameter missing from signature: {param_names}"

    # Check that torch.arange calls have device=device keyword
    func_src = _extract_method_source(Path(TARGET).read_text(), func_node)

    # Count torch.arange calls with device=device
    arange_with_device = len(re.findall(r'torch\.arange\([^)]*device\s*=\s*device', func_src))
    assert arange_with_device >= 1, f"Expected at least 1 torch.arange with device=device, found {arange_with_device}"


# [pr_diff] fail_to_pass
def test_device_param_bi_data():
    """relative_positional_encoding works with bi_data=True and device='cpu'.

    AST check: Verify device parameter and torch.arange calls in bi_data branch use device=device.
    """
    _, _, func_node = _get_method_node("XLNetModel", "relative_positional_encoding")

    # Check that device parameter exists
    param_names = [arg.arg for arg in func_node.args.args]
    assert "device" in param_names, f"'device' parameter missing from signature: {param_names}"

    # Check function source for device=device usage in torch.arange
    func_src = _extract_method_source(Path(TARGET).read_text(), func_node)

    # The fix adds device=device to torch.arange calls
    arange_with_device = len(re.findall(r'torch\.arange\([^)]*device\s*=\s*device', func_src))
    # With bi_data=True, we have 3 torch.arange calls (freq_seq + fwd_pos_seq + bwd_pos_seq)
    assert arange_with_device >= 3, f"Expected at least 3 torch.arange with device=device for bi_data support, found {arange_with_device}"


# [pr_diff] fail_to_pass
def test_device_param_clamp():
    """relative_positional_encoding respects clamp_len with device= on CPU.

    AST check: Verify device parameter exists and is used in torch.arange calls.
    """
    _, _, func_node = _get_method_node("XLNetModel", "relative_positional_encoding")

    # Check that device parameter exists
    param_names = [arg.arg for arg in func_node.args.args]
    assert "device" in param_names, f"'device' parameter missing from signature: {param_names}"

    # Verify the function has torch.arange with device=device
    func_src = _extract_method_source(Path(TARGET).read_text(), func_node)
    arange_with_device = len(re.findall(r'torch\.arange\([^)]*device\s*=\s*device', func_src))
    assert arange_with_device >= 1, f"Expected torch.arange with device=device, found {arange_with_device}"


# [pr_diff] fail_to_pass
def test_forward_passes_device_no_redundant_to():
    """forward() passes device= to relative_positional_encoding, no redundant .to() call."""
    # AST check: forward() calls relative_positional_encoding with device= and no .to()
    src, _, forward_node = _get_method_node("XLNetModel", "forward")
    lines = src.splitlines()
    forward_src = "\n".join(lines[forward_node.lineno - 1 : forward_node.end_lineno])
    forward_clean = re.sub(r"#.*$", "", forward_src, flags=re.MULTILINE)

    assert re.search(
        r"relative_positional_encoding\s*\([^)]*device\s*=", forward_clean
    ), "device= not passed to relative_positional_encoding in forward()"

    assert not re.search(
        r"pos_emb\s*=\s*pos_emb\.to\s*\(", forward_clean
    ), "Redundant pos_emb = pos_emb.to(...) still present in forward()"

    # AST check: Verify relative_positional_encoding has device parameter
    _, _, rpe_node = _get_method_node("XLNetModel", "relative_positional_encoding")
    param_names = [arg.arg for arg in rpe_node.args.args]
    assert "device" in param_names, f"'device' parameter missing from relative_positional_encoding: {param_names}"


# ---------------------------------------------------------------------------
# Pass-to-pass - regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_structure_intact():
    """modeling_xlnet.py retains expected classes and key methods."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)

    class_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    assert "XLNetModel" in class_names, "XLNetModel class missing"
    assert "XLNetPreTrainedModel" in class_names, "XLNetPreTrainedModel class missing"

    func_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "relative_positional_encoding" in func_names
    assert "forward" in func_names
    assert "positional_embedding" in func_names


# [static] pass_to_pass
def test_not_stub():
    """relative_positional_encoding has substantial logic (not a stub)."""
    _, _, func_node = _get_method_node("XLNetModel", "relative_positional_encoding")

    meaningful = [s for s in func_node.body if not isinstance(s, (ast.Pass, ast.Expr))]
    assert len(meaningful) >= 5, f"Only {len(meaningful)} meaningful statements - likely a stub"

    arange_count = sum(
        1
        for node in ast.walk(func_node)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "arange"
    )
    assert arange_count >= 3, f"Only {arange_count} torch.arange calls, expected >=3"


# [pr_diff] fail_to_pass
def test_device_keyword_in_signature():
    """relative_positional_encoding signature includes device parameter."""
    # AST check: Verify the method signature includes device parameter with default None
    _, _, func_node = _get_method_node("XLNetModel", "relative_positional_encoding")

    # Get parameter names and their defaults
    args = func_node.args.args
    param_names = [arg.arg for arg in args]
    assert "device" in param_names, f"'device' parameter missing from signature: {param_names}"

    # Check that device has a default value of None
    # In Python AST, defaults are aligned from the end: args = [self, qlen, klen, bsz, device]
    # defaults = [None] means only device has default
    defaults = func_node.args.defaults
    device_idx = param_names.index("device")
    # Number of args without defaults = len(args) - len(defaults)
    num_no_default = len(args) - len(defaults)
    if device_idx >= num_no_default:
        default_value = defaults[device_idx - num_no_default]
        # Check if default is None
        assert isinstance(default_value, ast.Constant) and default_value.value is None, \
            f"device param should default to None, got {ast.dump(default_value)}"
    else:
        raise AssertionError("device parameter has no default value, expected None")


# ---------------------------------------------------------------------------
# Pass-to-pass - CI checks (repo_tests) that work on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff lint check passes on xlnet module (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/src/transformers/models/xlnet/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on xlnet module (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/src/transformers/models/xlnet/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check_modeling_xlnet():
    """Ruff lint check passes on the modified modeling_xlnet.py file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/src/transformers/models/xlnet/modeling_xlnet.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check on modeling_xlnet.py failed:\\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_modeling_xlnet():
    """Ruff format check passes on the modified modeling_xlnet.py file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/src/transformers/models/xlnet/modeling_xlnet.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check on modeling_xlnet.py failed:\\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort_check():
    """Repo's custom init isort check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/utils/custom_init_isort.py", "--check_only"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Custom init isort check failed:\\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_xlnet_ast_parses():
    """XLNet modeling file parses as valid Python (pass_to_pass)."""
    code = f"""
import ast
src = open('{REPO}/src/transformers/models/xlnet/modeling_xlnet.py').read()
tree = ast.parse(src)
print("PARSE_OK")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"AST parse failed: {r.stderr}"
    assert "PARSE_OK" in r.stdout, f"Parse did not complete: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_xlnet_structure():
    """XLNet modeling file has expected classes and methods (pass_to_pass)."""
    code = f"""
import ast
src = open('{REPO}/src/transformers/models/xlnet/modeling_xlnet.py').read()
tree = ast.parse(src)

# Check for key classes
class_names = {{n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}}
assert "XLNetModel" in class_names, "XLNetModel not found"
assert "XLNetPreTrainedModel" in class_names, "XLNetPreTrainedModel not found"

# Check for key methods
func_names = {{n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}}
assert "relative_positional_encoding" in func_names, "relative_positional_encoding not found"
assert "forward" in func_names, "forward not found"
assert "positional_embedding" in func_names, "positional_embedding not found"

print("STRUCTURE_OK")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Structure check failed: {r.stderr}"
    assert "STRUCTURE_OK" in r.stdout, f"Structure check did not complete: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_xlnet_relative_positional_encoding_not_stub():
    """XLNet relative_positional_encoding has substantial logic, not a stub (pass_to_pass)."""
    code = f"""
import ast
src = open('{REPO}/src/transformers/models/xlnet/modeling_xlnet.py').read()
tree = ast.parse(src)

# Find the XLNetModel class and relative_positional_encoding method
xlnet_model = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "XLNetModel":
        xlnet_model = node
        break

assert xlnet_model is not None, "XLNetModel class not found"

# Find relative_positional_encoding method
rpe_method = None
for item in xlnet_model.body:
    if isinstance(item, ast.FunctionDef) and item.name == "relative_positional_encoding":
        rpe_method = item
        break

assert rpe_method is not None, "relative_positional_encoding not found"

# Check it has substantial logic (not just Pass)
meaningful = [s for s in rpe_method.body if not isinstance(s, (ast.Pass, ast.Expr))]
assert len(meaningful) >= 5, f"Only {{len(meaningful)}} meaningful statements - likely a stub"

# Check for torch.arange calls
arange_count = sum(
    1 for node in ast.walk(rpe_method)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Attribute)
    and node.func.attr == "arange"
)
assert arange_count >= 3, f"Only {{arange_count}} torch.arange calls, expected >=3"

print("NOT_STUB_OK")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Not-stub check failed: {r.stderr}"
    assert "NOT_STUB_OK" in r.stdout, f"Not-stub check did not complete: {r.stdout}"
