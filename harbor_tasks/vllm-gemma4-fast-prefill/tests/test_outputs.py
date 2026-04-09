"""
Task: vllm-gemma4-fast-prefill
Repo: vllm @ e69a265135ef48312d78130f64b7bfce4cd81a37
PR:   38879

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: GPU/model-weight dependent code — AST analysis is used because
we cannot instantiate vLLM models or run CUDA kernels in this environment.
"""

import ast
from pathlib import Path

REPO = "/workspace/vllm"
TARGET = Path(REPO) / "vllm" / "model_executor" / "models" / "gemma4.py"


def _parse_gemma4():
    """Parse gemma4.py and return the AST tree + source text."""
    src = TARGET.read_text()
    return ast.parse(src), src


def _find_class(tree, name):
    """Find a top-level class by name."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _class_methods(cls_node):
    """Return set of method names in a class."""
    return {
        node.name
        for node in cls_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """gemma4.py must parse without syntax errors."""
    src = TARGET.read_text()
    compile(src, str(TARGET), "exec")


# [static] pass_to_pass
def test_gemma4_model_class_exists():
    """Gemma4Model class still exists with forward method."""
    tree, _ = _parse_gemma4()
    cls = _find_class(tree, "Gemma4Model")
    assert cls is not None, "Gemma4Model class not found"
    methods = _class_methods(cls)
    assert "forward" in methods, "Gemma4Model.forward not found"
    assert "__init__" in methods, "Gemma4Model.__init__ not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — YOCO fast prefill classes and wiring
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_self_decoder_layers_class():
    """Gemma4SelfDecoderLayers must exist as nn.Module with embedding methods."""
    tree, _ = _parse_gemma4()
    cls = _find_class(tree, "Gemma4SelfDecoderLayers")
    assert cls is not None, "Gemma4SelfDecoderLayers class not found"

    # Must inherit from nn.Module
    base_names = []
    for base in cls.bases:
        if isinstance(base, ast.Attribute):
            base_names.append(base.attr)
        elif isinstance(base, ast.Name):
            base_names.append(base.id)
    assert "Module" in base_names, (
        f"Gemma4SelfDecoderLayers must inherit nn.Module, got bases: {base_names}"
    )

    # Must have embedding + forward methods
    methods = _class_methods(cls)
    for required in [
        "__init__",
        "forward",
        "embed_input_ids",
        "get_per_layer_inputs",
        "project_per_layer_inputs",
    ]:
        assert required in methods, (
            f"Gemma4SelfDecoderLayers missing method: {required}"
        )


# [pr_diff] fail_to_pass
def test_cross_decoder_layers_class():
    """Gemma4CrossDecoderLayers must exist as nn.Module with forward."""
    tree, _ = _parse_gemma4()
    cls = _find_class(tree, "Gemma4CrossDecoderLayers")
    assert cls is not None, "Gemma4CrossDecoderLayers class not found"

    base_names = []
    for base in cls.bases:
        if isinstance(base, ast.Attribute):
            base_names.append(base.attr)
        elif isinstance(base, ast.Name):
            base_names.append(base.id)
    assert "Module" in base_names, (
        f"Gemma4CrossDecoderLayers must inherit nn.Module, got bases: {base_names}"
    )

    methods = _class_methods(cls)
    assert "forward" in methods, "Gemma4CrossDecoderLayers missing forward method"
    assert "__init__" in methods, "Gemma4CrossDecoderLayers missing __init__"


# [pr_diff] fail_to_pass
def test_run_decoder_layers_helper():
    """_run_decoder_layers must be a standalone module-level function."""
    tree, _ = _parse_gemma4()

    func = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_run_decoder_layers":
            func = node
            break
    assert func is not None, (
        "_run_decoder_layers not found as a module-level function"
    )

    # Must accept decoder_layers, positions, hidden_states
    params = [arg.arg for arg in func.args.args]
    assert "decoder_layers" in params, (
        f"_run_decoder_layers missing 'decoder_layers' param, got: {params}"
    )
    assert "hidden_states" in params, (
        f"_run_decoder_layers missing 'hidden_states' param, got: {params}"
    )
    assert "positions" in params, (
        f"_run_decoder_layers missing 'positions' param, got: {params}"
    )

    # Must have non-trivial body (loop over layers)
    body_stmts = [
        s for s in func.body
        if not isinstance(s, (ast.Expr,))
        or not isinstance(getattr(s, "value", None), ast.Constant)
    ]
    assert len(body_stmts) >= 3, (
        f"_run_decoder_layers body too short ({len(body_stmts)} stmts), expected loop logic"
    )


# [pr_diff] fail_to_pass
def test_fast_prefill_forward_method():
    """Gemma4Model must have a fast_prefill_forward method with non-trivial body."""
    tree, _ = _parse_gemma4()
    cls = _find_class(tree, "Gemma4Model")
    assert cls is not None, "Gemma4Model class not found"

    fp_method = None
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == "fast_prefill_forward":
            fp_method = node
            break
    assert fp_method is not None, (
        "fast_prefill_forward method not found in Gemma4Model"
    )

    # Must accept positions, input_ids (or similar)
    params = [arg.arg for arg in fp_method.args.args]
    assert "self" in params, "fast_prefill_forward must be an instance method"
    assert "positions" in params, "fast_prefill_forward must accept 'positions'"
    assert "input_ids" in params, "fast_prefill_forward must accept 'input_ids'"

    # Non-trivial body: at least 8 statements (not a stub)
    body_stmts = [
        s for s in fp_method.body
        if not isinstance(s, (ast.Expr,))
        or not isinstance(getattr(s, "value", None), ast.Constant)
    ]
    assert len(body_stmts) >= 8, (
        f"fast_prefill_forward body too short ({len(body_stmts)} stmts)"
    )


# [pr_diff] fail_to_pass
def test_fast_prefill_calls_both_decoders():
    """fast_prefill_forward must invoke both self_decoder and cross_decoder."""
    tree, src = _parse_gemma4()
    cls = _find_class(tree, "Gemma4Model")
    assert cls is not None, "Gemma4Model class not found"

    fp_method = None
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == "fast_prefill_forward":
            fp_method = node
            break
    assert fp_method is not None, "fast_prefill_forward not found"

    # Collect self.attr accesses in the method body
    self_attrs = set()
    for sub in ast.walk(fp_method):
        if (
            isinstance(sub, ast.Attribute)
            and isinstance(sub.value, ast.Name)
            and sub.value.id == "self"
        ):
            self_attrs.add(sub.attr)

    assert "self_decoder" in self_attrs, (
        "fast_prefill_forward doesn't reference self.self_decoder"
    )
    assert "cross_decoder" in self_attrs, (
        "fast_prefill_forward doesn't reference self.cross_decoder"
    )


# [pr_diff] fail_to_pass
def test_forward_branches_on_fast_prefill():
    """Gemma4Model.forward must branch on fast_prefill_enabled."""
    tree, src = _parse_gemma4()
    cls = _find_class(tree, "Gemma4Model")
    assert cls is not None, "Gemma4Model class not found"

    fwd = None
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == "forward":
            fwd = node
            break
    assert fwd is not None, "Gemma4Model.forward not found"

    # Extract the source text of the forward method
    fwd_src = ast.get_source_segment(src, fwd)
    if fwd_src is None:
        # Fallback: check by line range
        lines = src.splitlines()
        fwd_src = "\n".join(lines[fwd.lineno - 1 : fwd.end_lineno])

    assert "fast_prefill" in fwd_src, (
        "Gemma4Model.forward does not reference fast_prefill — "
        "expected a branch on fast_prefill_enabled"
    )


# [pr_diff] fail_to_pass
def test_yoco_split_in_init():
    """Gemma4Model.__init__ must set up self_decoder and cross_decoder."""
    tree, src = _parse_gemma4()
    cls = _find_class(tree, "Gemma4Model")
    assert cls is not None, "Gemma4Model class not found"

    init = None
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            init = node
            break
    assert init is not None, "Gemma4Model.__init__ not found"

    # Check that __init__ assigns self.self_decoder and self.cross_decoder
    assigned_attrs = set()
    for sub in ast.walk(init):
        if isinstance(sub, ast.Assign):
            for target in sub.targets:
                if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"
                ):
                    assigned_attrs.add(target.attr)

    assert "self_decoder" in assigned_attrs, (
        "Gemma4Model.__init__ does not assign self.self_decoder"
    )
    assert "cross_decoder" in assigned_attrs, (
        "Gemma4Model.__init__ does not assign self.cross_decoder"
    )
