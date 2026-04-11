"""
Task: transformers-dequantize-save-reverse-op
Repo: huggingface/transformers @ 12b6b57cac0397db0afda56f3ab0101729bc5f0f
PR:   #44983

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys

sys.path.insert(0, "/repo/src")

REPO = "/repo"
BASE_COMMIT = "12b6b57cac0397db0afda56f3ab0101729bc5f0f"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All four modified files must parse without syntax errors."""
    import py_compile

    files = [
        f"{REPO}/src/transformers/core_model_loading.py",
        f"{REPO}/src/transformers/integrations/finegrained_fp8.py",
        f"{REPO}/src/transformers/integrations/metal_quantization.py",
        f"{REPO}/src/transformers/integrations/mxfp4.py",
    ]
    for f in files:
        py_compile.compile(f, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests using subprocess execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_identity_op_exists():
    """_IdentityOp class exists in core_model_loading and is a ConversionOps subclass."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
from transformers.core_model_loading import _IdentityOp, ConversionOps

assert issubclass(_IdentityOp, ConversionOps), f"_IdentityOp is not a subclass of ConversionOps"
op = _IdentityOp()
assert isinstance(op, ConversionOps), f"_IdentityOp instance is not a ConversionOps"
print("PASS: _IdentityOp exists and is correct type")
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_identity_op_passthrough():
    """_IdentityOp.convert returns input dict unchanged for varied inputs and dtypes."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import torch
from transformers.core_model_loading import _IdentityOp

op = _IdentityOp()

# Single entry - should return same dict object
d1 = {"w": torch.randn(4, 4)}
r1 = op.convert(d1)
assert r1 is d1, "convert should return the same dict object"

# Multiple entries with different dtypes
d2 = {
    "a": torch.randn(2, 3, dtype=torch.float32),
    "b": torch.randn(5, dtype=torch.float16),
    "c": torch.randn(1, 1, dtype=torch.bfloat16),
}
r2 = op.convert(d2)
assert set(r2.keys()) == {"a", "b", "c"}
for k in d2:
    assert torch.equal(r2[k], d2[k]), f"Values differ for key {k}"
    assert r2[k].dtype == d2[k].dtype, f"Dtype differs for key {k}"

# Empty dict
d3 = {}
r3 = op.convert(d3)
assert r3 == {}, "Empty dict should return empty dict"

print("PASS: _IdentityOp passthrough works correctly")
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_fp8_dequantize_reverse_op():
    """Fp8Dequantize.reverse_op returns a working ConversionOps instead of raising NotImplementedError."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import torch
from transformers.core_model_loading import ConversionOps

try:
    from transformers.integrations.finegrained_fp8 import Fp8Dequantize
except ImportError as e:
    print(f"SKIP: Fp8Dequantize import failed: {e}")
    sys.exit(0)

class MockQuantizer:
    class quantization_config:
        weight_block_size = None

obj = Fp8Dequantize(MockQuantizer())
rev = obj.reverse_op
assert isinstance(rev, ConversionOps), f"reverse_op is not ConversionOps: {type(rev)}"

t1 = torch.randn(8, 16)
t2 = torch.zeros(8)
data = {"layer.weight": t1, "layer.bias": t2}
result = rev.convert(data)
assert set(result.keys()) == set(data.keys()), "Keys don't match"
assert torch.equal(result["layer.weight"], t1), "layer.weight values don't match"
assert torch.equal(result["layer.bias"], t2), "layer.bias values don't match"

print("PASS: Fp8Dequantize.reverse_op works correctly")
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout or "SKIP" in r.stdout


# [pr_diff] fail_to_pass
def test_metal_dequantize_reverse_op():
    """MetalDequantize.reverse_op returns a working ConversionOps instead of raising NotImplementedError."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import torch
from transformers.core_model_loading import ConversionOps

try:
    from transformers.integrations.metal_quantization import MetalDequantize
except ImportError as e:
    print(f"SKIP: MetalDequantize import failed: {e}")
    sys.exit(0)

class MockQuantizer:
    class quantization_config:
        bits = 4
        group_size = 32

obj = MetalDequantize(MockQuantizer())
rev = obj.reverse_op
assert isinstance(rev, ConversionOps), f"reverse_op is not ConversionOps: {type(rev)}"

data = {"layer.weight": torch.randn(16, 16), "layer.bias": torch.ones(16)}
result = rev.convert(data)
assert set(result.keys()) == set(data.keys()), "Keys don't match"
assert torch.equal(result["layer.weight"], data["layer.weight"]), "layer.weight values don't match"
assert torch.equal(result["layer.bias"], data["layer.bias"]), "layer.bias values don't match"

print("PASS: MetalDequantize.reverse_op works correctly")
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout or "SKIP" in r.stdout


# [pr_diff] fail_to_pass
def test_mxfp4_dequantize_reverse_op():
    """Mxfp4Dequantize.reverse_op returns a working ConversionOps instead of raising NotImplementedError."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import torch
from transformers.core_model_loading import ConversionOps

try:
    from transformers.integrations.mxfp4 import Mxfp4Dequantize
except ImportError as e:
    print(f"SKIP: Mxfp4Dequantize import failed: {e}")
    sys.exit(0)

class MockQuantizer:
    class quantization_config:
        pass

obj = Mxfp4Dequantize(MockQuantizer())
rev = obj.reverse_op
assert isinstance(rev, ConversionOps), f"reverse_op is not ConversionOps: {type(rev)}"

data = {"attn.weight": torch.randn(32, 32)}
result = rev.convert(data)
assert torch.equal(result["attn.weight"], data["attn.weight"]), "attn.weight values don't match"

print("PASS: Mxfp4Dequantize.reverse_op works correctly")
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout or "SKIP" in r.stdout


# [pr_diff] fail_to_pass
def test_reverse_op_identity_multiple_entries():
    """reverse_op.convert preserves all keys, values, and dtypes for multi-entry dicts."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import torch
from transformers.core_model_loading import _IdentityOp

rev = _IdentityOp()

t_float32 = torch.randn(4, 4, dtype=torch.float32)
t_float16 = torch.randn(2, 8, dtype=torch.float16)
t_bfloat16 = torch.randn(6, 3, dtype=torch.bfloat16)
data = {"w1": t_float32, "w2": t_float16, "w3": t_bfloat16}
result = rev.convert(data)

assert len(result) == 3, "Result should have 3 entries"
assert torch.equal(result["w1"], t_float32), "w1 values don't match"
assert torch.equal(result["w2"], t_float16), "w2 values don't match"
assert torch.equal(result["w3"], t_bfloat16), "w3 values don't match"
assert result["w1"].dtype == torch.float32, "w1 dtype incorrect"
assert result["w2"].dtype == torch.float16, "w2 dtype incorrect"
assert result["w3"].dtype == torch.bfloat16, "w3 dtype incorrect"

print("PASS: reverse_op preserves keys, values, and dtypes")
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_save_pretrained_dequantize_flow():
    """The full save_pretrained flow with dequantize works without NotImplementedError."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import torch
from transformers.core_model_loading import ConversionOps

errors = []

# Mock quantizer classes
class MockFP8Config:
    weight_block_size = None

class MockFP8Quantizer:
    quantization_config = MockFP8Config()

class MockMetalConfig:
    bits = 4
    group_size = 32

class MockMetalQuantizer:
    quantization_config = MockMetalConfig()

class MockMxfp4Config:
    pass

class MockMxfp4Quantizer:
    quantization_config = MockMxfp4Config()

# Test FP8 dequantize reverse_op
try:
    from transformers.integrations.finegrained_fp8 import Fp8Dequantize
    fp8 = Fp8Dequantize(MockFP8Quantizer())
    rev = fp8.reverse_op
    if not isinstance(rev, ConversionOps):
        errors.append(f"Fp8Dequantize.reverse_op is not ConversionOps: {type(rev)}")
    # Test the reverse op actually works
    data = {"test.weight": torch.randn(8, 8)}
    result = rev.convert(data)
    if "test.weight" not in result:
        errors.append("Fp8Dequantize reverse_op did not preserve key")
except NotImplementedError as e:
    errors.append(f"Fp8Dequantize.reverse_op raised NotImplementedError: {e}")
except ImportError:
    pass  # GPU-dependent imports not available, skip

# Test Metal dequantize reverse_op
try:
    from transformers.integrations.metal_quantization import MetalDequantize
    metal = MetalDequantize(MockMetalQuantizer())
    rev = metal.reverse_op
    if not isinstance(rev, ConversionOps):
        errors.append(f"MetalDequantize.reverse_op is not ConversionOps: {type(rev)}")
    data = {"test.weight": torch.randn(8, 8)}
    result = rev.convert(data)
    if "test.weight" not in result:
        errors.append("MetalDequantize reverse_op did not preserve key")
except NotImplementedError as e:
    errors.append(f"MetalDequantize.reverse_op raised NotImplementedError: {e}")
except ImportError:
    pass  # GPU-dependent imports not available, skip

# Test MXFP4 dequantize reverse_op
try:
    from transformers.integrations.mxfp4 import Mxfp4Dequantize
    mxfp4 = Mxfp4Dequantize(MockMxfp4Quantizer())
    rev = mxfp4.reverse_op
    if not isinstance(rev, ConversionOps):
        errors.append(f"Mxfp4Dequantize.reverse_op is not ConversionOps: {type(rev)}")
    data = {"test.weight": torch.randn(8, 8)}
    result = rev.convert(data)
    if "test.weight" not in result:
        errors.append("Mxfp4Dequantize reverse_op did not preserve key")
except NotImplementedError as e:
    errors.append(f"Mxfp4Dequantize.reverse_op raised NotImplementedError: {e}")
except ImportError:
    pass  # GPU-dependent imports not available, skip

if errors:
    print("FAILURES:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("PASS: All dequantize reverse_op work correctly")
    sys.exit(0)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_chunk_cat_reverse_op():
    """Existing Chunk/Concatenate reverse_op pair still works correctly."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
from transformers.core_model_loading import Chunk, Concatenate

chunk = Chunk(dim=0)
rev = chunk.reverse_op
assert isinstance(rev, Concatenate), f"Chunk.reverse_op should be Concatenate, got {type(rev)}"

cat = Concatenate(dim=0)
rev2 = cat.reverse_op
assert isinstance(rev2, Chunk), f"Concatenate.reverse_op should be Chunk, got {type(rev2)}"

print("PASS: Chunk/Concatenate reverse_op pair works correctly")
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config-derived (agent_config) - rules from CLAUDE.md / agent config files
# ---------------------------------------------------------------------------

def _get_agent_diff():
    """Get the diff of changes made by the agent (or gold patch) relative to base commit."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT],
        cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return r.stdout


# [agent_config] pass_to_pass - CLAUDE.md:2 @ 12b6b57
def test_ruff_check():
    """ruff check passes on all modified files (CLAUDE.md: 'make style: runs ruff')."""
    r = subprocess.run(
        [
            "ruff", "check",
            f"{REPO}/src/transformers/core_model_loading.py",
            f"{REPO}/src/transformers/integrations/finegrained_fp8.py",
            f"{REPO}/src/transformers/integrations/metal_quantization.py",
            f"{REPO}/src/transformers/integrations/mxfp4.py",
            "--quiet",
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


# [agent_config] pass_to_pass - CLAUDE.md:66 @ 12b6b57
def test_no_copied_from_blocks_edited():
    """No '# Copied from' blocks were modified (CLAUDE.md line 66)."""
    diff = _get_agent_diff()
    if not diff:
        return  # No changes = no violations

    in_hunk = False
    for line in diff.splitlines():
        if line.startswith("@@"):
            in_hunk = True
        elif line.startswith("diff --git"):
            in_hunk = False
        elif in_hunk and (line.startswith("+") or line.startswith("-")):
            assert "# Copied from" not in line[1:], (
                f"Diff modifies a '# Copied from' block: {line}"
            )


# [agent_config] pass_to_pass - CLAUDE.md:67 @ 12b6b57
def test_no_modular_generated_files_edited():
    """Generated modeling files with a modular_ source must not be edited directly (CLAUDE.md line 67)."""
    import os

    r = subprocess.run(
        ["git", "diff", "--name-only", BASE_COMMIT],
        cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    files = r.stdout.strip()
    if not files:
        return  # No changes = no violations

    for f in files.splitlines():
        f = f.strip()
        if not f:
            continue
        basename = os.path.basename(f)
        if basename.startswith("modeling_"):
            dirname = os.path.dirname(f)
            modular = os.path.join(REPO, dirname, "modular_" + basename.replace("modeling_", ""))
            assert not os.path.exists(modular), (
                f"{f} has a modular source ({modular}) and should not be edited directly"
            )


# [agent_config] pass_to_pass - .ai/skills/add-or-fix-type-checking/SKILL.md:180-186 @ 12b6b57
def test_no_bare_type_ignore():
    """Any # type: ignore must include a specific error code (e.g. # type: ignore[call-arg])."""
    import re

    diff = _get_agent_diff()
    if not diff:
        return

    bare_pattern = re.compile(r"#\s*type:\s*ignore(?!\[)")
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:]
            assert not bare_pattern.search(content), (
                f"Added line has bare '# type: ignore' without error code: {content.strip()}"
            )


# [agent_config] pass_to_pass - .ai/skills/add-or-fix-type-checking/SKILL.md:189-190 @ 12b6b57
def test_no_assert_for_type_narrowing():
    """Do not use assert for type narrowing - use 'if ...: raise' instead."""
    diff = _get_agent_diff()
    if not diff:
        return

    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:].strip()
            if content.startswith("assert isinstance("):
                assert False, (
                    f"Added line uses assert for type narrowing (use 'if ...: raise' instead): {content}"
                )
            if content.startswith("assert ") and "is not None" in content:
                assert False, (
                    f"Added line uses assert for type narrowing (use 'if ...: raise' instead): {content}"
                )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates - verified to work on base commit
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass - basic transformers imports work
def test_repo_imports():
    """Core transformers modules can be imported without errors (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import torch
from transformers.core_model_loading import Chunk, Concatenate, ConversionOps, WeightConverter
from transformers import PretrainedConfig

# Basic smoke test
assert issubclass(Chunk, ConversionOps), "Chunk is not a ConversionOps subclass"
assert issubclass(Concatenate, ConversionOps), "Concatenate is not a ConversionOps subclass"
print("PASS: Core imports work correctly")
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# [repo_ci] pass_to_pass - ruff format check on modified files
def test_repo_ruff_format():
    """Ruff format check passes on all modified files (pass_to_pass)."""
    r = subprocess.run(
        [
            "ruff", "format", "--check",
            f"{REPO}/src/transformers/core_model_loading.py",
            f"{REPO}/src/transformers/integrations/finegrained_fp8.py",
            f"{REPO}/src/transformers/integrations/metal_quantization.py",
            f"{REPO}/src/transformers/integrations/mxfp4.py",
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass - core_model_loading conversion ops work
def test_repo_core_model_loading():
    """core_model_loading ConversionOps work correctly (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import torch
from transformers.core_model_loading import Chunk, Concatenate

# Test Chunk/Concatenate reverse_op relationship
chunk = Chunk(dim=0)
rev = chunk.reverse_op
assert isinstance(rev, Concatenate), f"Chunk.reverse_op should be Concatenate, got {type(rev)}"

cat = Concatenate(dim=0)
rev2 = cat.reverse_op
assert isinstance(rev2, Chunk), f"Concatenate.reverse_op should be Chunk, got {type(rev2)}"

print("PASS: core_model_loading ops work correctly")
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - Metal quantization config tests
def test_repo_metal_config():
    """MetalConfig unit tests pass (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import unittest
from tests.quantization.metal.test_metal import MetalConfigTest
suite = unittest.TestLoader().loadTestsFromTestCase(MetalConfigTest)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"MetalConfig tests failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - Metal quantizer environment tests
def test_repo_metal_quantizer_env():
    """MetalHfQuantizer environment validation tests pass (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import unittest
from tests.quantization.metal.test_metal import MetalQuantizerEnvironmentTest
suite = unittest.TestLoader().loadTestsFromTestCase(MetalQuantizerEnvironmentTest)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"MetalQuantizerEnvironmentTest failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - Metal affine quantize/dequantize tests
def test_repo_metal_affine_quantize():
    """Metal affine quantize/dequantize roundtrip tests pass (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import unittest
from tests.quantization.metal.test_metal import AffineQuantizeDequantizeTest
suite = unittest.TestLoader().loadTestsFromTestCase(AffineQuantizeDequantizeTest)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AffineQuantizeDequantizeTest failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - Metal Linear module tests
def test_repo_metal_linear():
    """MetalLinear module tests pass (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import unittest
from tests.quantization.metal.test_metal import MetalLinearTest
suite = unittest.TestLoader().loadTestsFromTestCase(MetalLinearTest)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"MetalLinearTest failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - Metal ConversionOps tests
def test_repo_metal_conversion_ops():
    """Metal ConversionOps (MetalQuantize/MetalDequantize) tests pass (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import unittest
from tests.quantization.metal.test_metal import MetalConversionOpsTest
suite = unittest.TestLoader().loadTestsFromTestCase(MetalConversionOpsTest)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"MetalConversionOpsTest failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - MXFP4 config tests
def test_repo_mxfp4_config():
    """Mxfp4Config unit tests pass (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import unittest
from tests.quantization.mxfp4.test_mxfp4 import Mxfp4ConfigTest
suite = unittest.TestLoader().loadTestsFromTestCase(Mxfp4ConfigTest)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Mxfp4ConfigTest failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - core_model_loading glob matching tests
def test_repo_core_model_loading_glob_matching():
    """TestWeightGlobMatching from test_core_model_loading passes (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "parameterized", "-q"],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
import unittest
from tests.utils.test_core_model_loading import TestWeightGlobMatching
suite = unittest.TestLoader().loadTestsFromTestCase(TestWeightGlobMatching)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TestWeightGlobMatching failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - core_model_loading convert and load tests
def test_repo_core_model_loading_convert():
    """TestConvertAndLoadStateDict from test_core_model_loading passes (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "parameterized", "-q"],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
import unittest
from tests.utils.test_core_model_loading import TestConvertAndLoadStateDict
suite = unittest.TestLoader().loadTestsFromTestCase(TestConvertAndLoadStateDict)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TestConvertAndLoadStateDict failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - core_model_loading conversion mapping tests
def test_repo_core_model_loading_mapping():
    """TestConversionMapping from test_core_model_loading passes (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "parameterized", "-q"],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
import unittest
from tests.utils.test_core_model_loading import TestConversionMapping
suite = unittest.TestLoader().loadTestsFromTestCase(TestConversionMapping)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TestConversionMapping failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - finegrained_fp8 config tests
def test_repo_finegrained_fp8_config():
    """FineGrainedFP8ConfigTest from test_fp8 passes (pass_to_pass)."""
    code = '''
import sys
sys.path.insert(0, "/repo/src")
import subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "parameterized", "-q"],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
import unittest
from tests.quantization.finegrained_fp8.test_fp8 import FineGrainedFP8ConfigTest
suite = unittest.TestLoader().loadTestsFromTestCase(FineGrainedFP8ConfigTest)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"FineGrainedFP8ConfigTest failed:\n{r.stdout}\n{r.stderr}"
