"""
Task: transformers-xlnet-rope-cpu-forward
Repo: huggingface/transformers @ be6cf0848668852e3267d297211eb7e983e6c786
PR:   44782

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
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


def _build_mock_class(func_src, d_model, attn_type, bi_data, clamp_len):
    """Build exec code with a MockXLNet class embedding the extracted method."""
    return f"""
import torch

class MockXLNet:
    d_model = {d_model}
    attn_type = "{attn_type}"
    bi_data = {bi_data}
    clamp_len = {clamp_len}

    def positional_embedding(self, pos_seq, inv_freq, bsz=None):
        sinusoid_inp = torch.einsum("i,d->id", pos_seq, inv_freq)
        pos_emb = torch.cat([torch.sin(sinusoid_inp), torch.cos(sinusoid_inp)], dim=-1)
        if bsz is not None:
            return pos_emb[:, None, :].expand(-1, bsz, -1)
        return pos_emb[:, None, :]

{func_src}
"""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """modeling_xlnet.py must parse without syntax errors."""
    src = Path(TARGET).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_device_param_uni():
    """relative_positional_encoding accepts device= with attn_type='bi', bi_data=False."""
    import torch

    src, _, func_node = _get_method_node("XLNetModel", "relative_positional_encoding")
    func_src = _extract_method_source(src, func_node)

    # Test with multiple (qlen, klen, bsz, d_model) combos to prevent hardcoding
    test_cases = [
        (10, 20, 2, 768),
        (5, 5, 1, 256),
        (32, 64, 8, 512),
    ]
    for qlen, klen, bsz, d_model in test_cases:
        exec_code = _build_mock_class(func_src, d_model, "bi", False, -1)
        exec_code += f"""
model = MockXLNet()
result = model.relative_positional_encoding(qlen={qlen}, klen={klen}, bsz={bsz}, device='cpu')
assert isinstance(result, torch.Tensor), f"Expected tensor, got {{type(result)}}"
assert str(result.device) == 'cpu', f"Expected cpu device, got {{result.device}}"
assert result.shape[-1] == {d_model}, f"Expected last dim={d_model}, got {{result.shape[-1]}}"
assert result.shape[0] > 0, "Empty result tensor"
"""
        exec(exec_code, {"__builtins__": __builtins__})


# [pr_diff] fail_to_pass
def test_device_param_bi_data():
    """relative_positional_encoding works with bi_data=True and device='cpu'."""
    import torch

    src, _, func_node = _get_method_node("XLNetModel", "relative_positional_encoding")
    func_src = _extract_method_source(src, func_node)

    # bsz must be even for bi_data (code splits bsz//2 per direction)
    test_cases = [
        (8, 16, 4, 512),
        (12, 24, 2, 256),
        (6, 10, 8, 128),
    ]
    for qlen, klen, bsz, d_model in test_cases:
        exec_code = _build_mock_class(func_src, d_model, "bi", True, -1)
        exec_code += f"""
model = MockXLNet()
result = model.relative_positional_encoding(qlen={qlen}, klen={klen}, bsz={bsz}, device='cpu')
assert isinstance(result, torch.Tensor), f"Expected tensor, got {{type(result)}}"
assert str(result.device) == 'cpu', f"Expected cpu device, got {{result.device}}"
# bi_data=True: fwd uses bsz//2, bwd uses bsz//2, cat on dim=1 → dim1 = 2*(bsz//2) = bsz
assert result.shape[1] == {bsz}, f"Expected dim1={bsz} for bi_data, got {{result.shape[1]}}"
assert result.shape[-1] == {d_model}, f"Expected last dim={d_model}, got {{result.shape[-1]}}"
"""
        exec(exec_code, {"__builtins__": __builtins__})


# [pr_diff] fail_to_pass
def test_device_param_clamp():
    """relative_positional_encoding respects clamp_len with device= on CPU."""
    import torch

    src, _, func_node = _get_method_node("XLNetModel", "relative_positional_encoding")
    func_src = _extract_method_source(src, func_node)

    # Test with clamp_len > 0, both bi_data modes
    for bi_data in [False, True]:
        exec_code = _build_mock_class(func_src, 256, "bi", bi_data, 4)
        exec_code += f"""
model = MockXLNet()
result = model.relative_positional_encoding(qlen=20, klen=30, bsz=2, device='cpu')
assert isinstance(result, torch.Tensor), f"Expected tensor, got {{type(result)}}"
assert str(result.device) == 'cpu', f"Expected cpu device, got {{result.device}}"
assert result.shape[1] == 2, f"Expected dim1=2 (bsz), got {{result.shape[1]}}"
"""
        exec(exec_code, {"__builtins__": __builtins__})


# [pr_diff] fail_to_pass
def test_forward_passes_device_no_redundant_to():
    """forward() passes device= to relative_positional_encoding, no redundant .to() call."""
    # AST-only because: forward() requires full model instantiation with weights,
    # tokenizer, and config — too heavy for isolated unit test
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


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
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
    assert len(meaningful) >= 5, f"Only {len(meaningful)} meaningful statements — likely a stub"

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
    _, _, func_node = _get_method_node("XLNetModel", "relative_positional_encoding")
    param_names = [arg.arg for arg in func_node.args.args]
    assert "device" in param_names, (
        f"'device' parameter missing from relative_positional_encoding signature: {param_names}"
    )
