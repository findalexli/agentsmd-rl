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
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_device_param_uni():
    """relative_positional_encoding accepts device= with attn_type='bi', bi_data=False."""
    code = """
import sys
sys.path.insert(0, '/workspace/transformers')

import torch

class MockXLNet:
    d_model = 768
    attn_type = "bi"
    bi_data = False
    clamp_len = -1

    def positional_embedding(self, pos_seq, inv_freq, bsz=None):
        sinusoid_inp = torch.einsum("i,d->id", pos_seq, inv_freq)
        pos_emb = torch.cat([torch.sin(sinusoid_inp), torch.cos(sinusoid_inp)], dim=-1)
        if bsz is not None:
            return pos_emb[:, None, :].expand(-1, bsz, -1)
        return pos_emb[:, None, :]

# Copy the method from XLNetModel
from transformers.models.xlnet.modeling_xlnet import XLNetModel
import types

model = MockXLNet()
model.relative_positional_encoding = types.MethodType(XLNetModel.relative_positional_encoding, model)

# Test multiple configurations
test_cases = [
    (10, 20, 2, 768),
    (5, 5, 1, 256),
    (32, 64, 8, 512),
]

for qlen, klen, bsz, d_model in test_cases:
    model.d_model = d_model
    result = model.relative_positional_encoding(qlen=qlen, klen=klen, bsz=bsz, device='cpu')
    assert isinstance(result, torch.Tensor), f"Expected tensor, got {type(result)}"
    assert str(result.device) == 'cpu', f"Expected cpu device, got {result.device}"
    assert result.shape[-1] == d_model, f"Expected last dim={d_model}, got {result.shape[-1]}"
    assert result.shape[0] > 0, "Empty result tensor"

print("PASS")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_device_param_bi_data():
    """relative_positional_encoding works with bi_data=True and device='cpu'."""
    code = """
import sys
sys.path.insert(0, '/workspace/transformers')

import torch

class MockXLNet:
    d_model = 512
    attn_type = "bi"
    bi_data = True
    clamp_len = -1

    def positional_embedding(self, pos_seq, inv_freq, bsz=None):
        sinusoid_inp = torch.einsum("i,d->id", pos_seq, inv_freq)
        pos_emb = torch.cat([torch.sin(sinusoid_inp), torch.cos(sinusoid_inp)], dim=-1)
        if bsz is not None:
            return pos_emb[:, None, :].expand(-1, bsz, -1)
        return pos_emb[:, None, :]

from transformers.models.xlnet.modeling_xlnet import XLNetModel
import types

model = MockXLNet()
model.relative_positional_encoding = types.MethodType(XLNetModel.relative_positional_encoding, model)

# bsz must be even for bi_data (code splits bsz//2 per direction)
test_cases = [
    (8, 16, 4, 512),
    (12, 24, 2, 256),
    (6, 10, 8, 128),
]

for qlen, klen, bsz, d_model in test_cases:
    model.d_model = d_model
    result = model.relative_positional_encoding(qlen=qlen, klen=klen, bsz=bsz, device='cpu')
    assert isinstance(result, torch.Tensor), f"Expected tensor, got {type(result)}"
    assert str(result.device) == 'cpu', f"Expected cpu device, got {result.device}"
    # bi_data=True: fwd uses bsz//2, bwd uses bsz//2, cat on dim=1 -> dim1 = 2*(bsz//2) = bsz
    assert result.shape[1] == bsz, f"Expected dim1={bsz} for bi_data, got {result.shape[1]}"
    assert result.shape[-1] == d_model, f"Expected last dim={d_model}, got {result.shape[-1]}"

print("PASS")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_device_param_clamp():
    """relative_positional_encoding respects clamp_len with device= on CPU."""
    code = """
import sys
sys.path.insert(0, '/workspace/transformers')

import torch

class MockXLNet:
    d_model = 256
    attn_type = "bi"
    bi_data = False
    clamp_len = 4

    def positional_embedding(self, pos_seq, inv_freq, bsz=None):
        sinusoid_inp = torch.einsum("i,d->id", pos_seq, inv_freq)
        pos_emb = torch.cat([torch.sin(sinusoid_inp), torch.cos(sinusoid_inp)], dim=-1)
        if bsz is not None:
            return pos_emb[:, None, :].expand(-1, bsz, -1)
        return pos_emb[:, None, :]

from transformers.models.xlnet.modeling_xlnet import XLNetModel
import types

for bi_data in [False, True]:
    model = MockXLNet()
    model.bi_data = bi_data
    model.relative_positional_encoding = types.MethodType(XLNetModel.relative_positional_encoding, model)

    result = model.relative_positional_encoding(qlen=20, klen=30, bsz=2, device='cpu')
    assert isinstance(result, torch.Tensor), f"Expected tensor, got {type(result)}"
    assert str(result.device) == 'cpu', f"Expected cpu device, got {result.device}"
    assert result.shape[1] == 2, f"Expected dim1=2 (bsz), got {result.shape[1]}"

print("PASS")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


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

    # Subprocess check: verify we can import and the function signature works
    code = """
import sys
sys.path.insert(0, '/workspace/transformers')

from transformers.models.xlnet.modeling_xlnet import XLNetModel
import inspect

# Verify device parameter exists in signature
sig = inspect.signature(XLNetModel.relative_positional_encoding)
assert 'device' in sig.parameters, "device parameter not in relative_positional_encoding signature"

# Verify forward method exists
sig_fwd = inspect.signature(XLNetModel.forward)
assert sig_fwd is not None, "forward method not found"

print("PASS")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


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
    code = """
import sys
sys.path.insert(0, '/workspace/transformers')

from transformers.models.xlnet.modeling_xlnet import XLNetModel
import inspect

sig = inspect.signature(XLNetModel.relative_positional_encoding)
param_names = list(sig.parameters.keys())
assert "device" in param_names, f"'device' parameter missing from signature: {param_names}"

# Also verify it has a default of None
device_param = sig.parameters['device']
assert device_param.default is None, f"device param should default to None, got {device_param.default}"

print("PASS")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout
