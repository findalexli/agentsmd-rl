"""
Task: vllm-cpu-ct-w4a16-kernel
Repo: vllm-project/vllm @ a8eab8f30dda380a67c515c743365840b4347ccd
PR:   38219

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path

TARGET = Path("/repo/vllm/model_executor/kernels/linear/mixed_precision/cpu.py")

HARDCODED_LAYER_ATTRS = {"qweight", "scales", "qzeros", "g_idx"}


def _parse_target():
    """Parse the target file and return the AST tree."""
    source = TARGET.read_text()
    return ast.parse(source), source


def _find_class(tree, name="CPUWNA16LinearKernel"):
    """Find a class definition by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _find_method(cls_node, name):
    """Find a method by name within a class AST node."""
    for node in ast.walk(cls_node):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _count_hardcoded_layer_accesses(method_node):
    """Count direct layer.qweight / layer.scales / etc. accesses in a method."""
    count = 0
    for child in ast.walk(method_node):
        if (
            isinstance(child, ast.Attribute)
            and child.attr in HARDCODED_LAYER_ATTRS
            and isinstance(child.value, ast.Name)
            and child.value.id == "layer"
        ):
            count += 1
    return count


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    # AST-only because: vllm requires compiled C++ custom ops (torch._custom_ops)
    """Target file must be valid Python."""
    source = TARGET.read_text()
    compile(source, str(TARGET), "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_hardcoded_attrs_in_process_gptq_weights():
    # AST-only because: method uses compiled C++ ops (unpack/pack_quantized_values)
    """_process_gptq_weights must use generic accessors, not layer.qweight etc.

    The buggy code directly accesses layer.qweight, layer.scales, layer.qzeros,
    and layer.g_idx. The fix uses self.w_q_name / getattr / _get_weight_params.
    """
    tree, _ = _parse_target()
    cls = _find_class(tree)
    assert cls is not None, "CPUWNA16LinearKernel class not found"

    method = _find_method(cls, "_process_gptq_weights")
    assert method is not None, "_process_gptq_weights method not found"

    n = _count_hardcoded_layer_accesses(method)
    assert n == 0, (
        f"_process_gptq_weights has {n} hardcoded layer attribute access(es) "
        f"— must use generic accessors (getattr, self.w_q_name, etc.)"
    )


# [pr_diff] fail_to_pass
def test_no_hardcoded_attrs_in_apply_weights():
    # AST-only because: method calls compiled C++ op (ops.cpu_gemm_wna16)
    """apply_weights must use generic accessors, not layer.qweight etc.

    Same bug as _process_gptq_weights: the buggy code passes layer.qweight,
    layer.scales, layer.qzeros, layer.g_idx directly to ops.cpu_gemm_wna16.
    """
    tree, _ = _parse_target()
    cls = _find_class(tree)
    assert cls is not None, "CPUWNA16LinearKernel class not found"

    method = _find_method(cls, "apply_weights")
    assert method is not None, "apply_weights method not found"

    n = _count_hardcoded_layer_accesses(method)
    assert n == 0, (
        f"apply_weights has {n} hardcoded layer attribute access(es) "
        f"— must use generic accessors"
    )


# [pr_diff] fail_to_pass
def test_process_weights_dispatches_by_dimension():
    # AST-only because: method depends on torch.nn.Module with compiled custom ops
    """process_weights_after_loading must dispatch by weight dimension metadata.

    The buggy code uses `not self.config.zero_points` as the sole dispatch
    signal: no zero_points -> GPTQ, else -> raise NotImplementedError("AWQ...").
    CT format HAS zero_points but needs the GPTQ path. The fix must check
    packed_dim vs input_dim on the actual weight tensor to determine format.
    """
    tree, _ = _parse_target()
    cls = _find_class(tree)
    assert cls is not None, "CPUWNA16LinearKernel class not found"

    method = _find_method(cls, "process_weights_after_loading")
    assert method is not None, "process_weights_after_loading method not found"

    # The key fix: dispatch by actual weight dimension metadata, not config flags
    dim_attrs = {"input_dim", "packed_dim"}
    found_dim_access = False
    for child in ast.walk(method):
        if isinstance(child, ast.Attribute) and child.attr in dim_attrs:
            found_dim_access = True
            break

    assert found_dim_access, (
        "process_weights_after_loading does not access input_dim or packed_dim "
        "— CT format dispatch requires checking weight dimension metadata, "
        "not just config.zero_points"
    )


# [pr_diff] fail_to_pass
def test_ct_transpose_in_weight_processing():
    # AST-only because: methods use compiled C++ tensor ops + custom quantization
    """Weight processing must include transposition for CT dimension ordering.

    CT format has input_dim=1, output_dim=0 (opposite of marlin's 0,1).
    The fix must transpose weights/scales/zp via .t() or .transpose() calls
    in _process_gptq_weights or process_weights_after_loading. The base code
    only has .permute in the block-repack section, not for CT layout correction.
    """
    tree, _ = _parse_target()
    cls = _find_class(tree)
    assert cls is not None, "CPUWNA16LinearKernel class not found"

    transpose_methods = {"t", "transpose"}
    target_methods = {"_process_gptq_weights", "process_weights_after_loading"}

    found = False
    for method_name in target_methods:
        method = _find_method(cls, method_name)
        if method is None:
            continue
        for child in ast.walk(method):
            if (
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Attribute)
                and child.func.attr in transpose_methods
            ):
                found = True
                break
        if found:
            break

    assert found, (
        "No .t() or .transpose() calls found in weight processing methods "
        "— CT format requires transposing weights/scales/zp due to different "
        "dimension ordering (input_dim=1 vs marlin's input_dim=0)"
    )


# [pr_diff] fail_to_pass
def test_process_weights_uses_generic_accessors():
    # AST-only because: method depends on torch.nn.Module with compiled custom ops
    """process_weights_after_loading must use getattr/setattr for layer access.

    The base code has no generic accessor usage in process_weights_after_loading
    (it only checks self.config and delegates to _process_gptq_weights or raises).
    The fix moves layer attribute cleanup here using setattr(layer, self.w_zp_name, None)
    and reads weight metadata using getattr(layer, self.w_q_name).
    """
    tree, _ = _parse_target()
    cls = _find_class(tree)
    assert cls is not None, "CPUWNA16LinearKernel class not found"

    method = _find_method(cls, "process_weights_after_loading")
    assert method is not None, "process_weights_after_loading method not found"

    generic_funcs = {"getattr", "setattr", "hasattr"}
    found_count = 0
    for child in ast.walk(method):
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id in generic_funcs
        ):
            found_count += 1

    assert found_count >= 2, (
        f"process_weights_after_loading has only {found_count} getattr/setattr call(s) "
        f"— must use generic accessors for format-agnostic layer attribute access"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from repo
# ---------------------------------------------------------------------------

def _ensure_tool(name: str, pkg: str | None = None) -> None:
    """Ensure a CLI tool is available, installing if needed."""
    import shutil
    import subprocess
    import sys
    if shutil.which(name):
        return
    pkg = pkg or name
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Target file must pass ruff linting (pass_to_pass)."""
    import subprocess
    _ensure_tool("ruff")
    r = subprocess.run(
        ["ruff", "check", "--output-format", "github", str(TARGET)],
        capture_output=True, text=True, timeout=60, cwd="/repo",
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_mypy_check():
    """Target file must pass mypy type checking (pass_to_pass)."""
    import subprocess
    import shutil
    import sys
    _ensure_tool("mypy")
    # Install pydantic to avoid plugin import error in pyproject.toml
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pydantic"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Use --no-incremental to avoid cache issues and explicitly set config file
    r = subprocess.run(
        ["mypy", "--ignore-missing-imports", "--follow-imports=silent", "--no-incremental", str(TARGET)],
        capture_output=True, text=True, timeout=120, cwd="/repo",
        env={**dict(subprocess.os.environ), "MYPY_FORCE_COLOR": "0"}
    )
    assert r.returncode == 0, f"MyPy check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_can_implement_preserved():
    # AST-only because: classmethod references compiled platform/quant config types
    """can_implement must remain a classmethod with full validation logic.

    The method validates platform, quant type, group size, and partition shape.
    Must have @classmethod decorator, >=3 If nodes, >=3 Return nodes.
    """
    tree, _ = _parse_target()
    cls = _find_class(tree)
    assert cls is not None, "CPUWNA16LinearKernel class not found"

    method = _find_method(cls, "can_implement")
    assert method is not None, "can_implement method not found"

    is_classmethod = any(
        (isinstance(d, ast.Name) and d.id == "classmethod")
        or (isinstance(d, ast.Attribute) and d.attr == "classmethod")
        for d in method.decorator_list
    )
    assert is_classmethod, "can_implement must be a @classmethod"

    if_count = sum(1 for n in ast.walk(method) if isinstance(n, ast.If))
    return_count = sum(1 for n in ast.walk(method) if isinstance(n, ast.Return))
    assert if_count >= 3, f"can_implement has only {if_count} If nodes (need >=3)"
    assert return_count >= 3, f"can_implement has only {return_count} Return nodes (need >=3)"


# [static] pass_to_pass
def test_not_stub():
    # AST-only because: class depends on compiled C++ custom ops
    """CPUWNA16LinearKernel must have substantive method implementations.

    Required methods: can_implement, process_weights_after_loading, apply_weights.
    Each must have >=3 meaningful statements. File must be >=60 lines.
    """
    tree, source = _parse_target()
    cls = _find_class(tree)
    assert cls is not None, "CPUWNA16LinearKernel class not found"

    required = {"can_implement", "process_weights_after_loading", "apply_weights"}
    methods = {}
    for node in ast.iter_child_nodes(cls):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stmt_types = (
                ast.Assign, ast.AugAssign, ast.AnnAssign,
                ast.Return, ast.If, ast.For, ast.While,
                ast.Call, ast.Expr, ast.Raise,
            )
            stmts = sum(1 for child in ast.walk(node) if isinstance(child, stmt_types))
            methods[node.name] = stmts

    missing = required - set(methods.keys())
    assert not missing, f"Missing required methods: {missing}"

    shallow = {m: c for m, c in methods.items() if m in required and c < 3}
    assert not shallow, f"Stub methods (< 3 statements): {shallow}"

    line_count = len(source.splitlines())
    assert line_count >= 60, f"Only {line_count} lines — likely a stub"
