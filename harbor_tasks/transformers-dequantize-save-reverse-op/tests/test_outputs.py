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
# Gates (pass_to_pass, static) — syntax / compilation checks
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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_identity_op_exists():
    """_IdentityOp class exists in core_model_loading and is a ConversionOps subclass."""
    from transformers.core_model_loading import _IdentityOp, ConversionOps

    assert issubclass(_IdentityOp, ConversionOps)
    # Must be instantiable without arguments
    op = _IdentityOp()
    assert isinstance(op, ConversionOps)


# [pr_diff] fail_to_pass
def test_identity_op_passthrough():
    """_IdentityOp.convert returns input dict unchanged for varied inputs."""
    import torch
    from transformers.core_model_loading import _IdentityOp

    op = _IdentityOp()

    # Single entry
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
        assert torch.equal(r2[k], d2[k])
        assert r2[k].dtype == d2[k].dtype

    # Empty dict
    d3 = {}
    r3 = op.convert(d3)
    assert r3 == {}


# [pr_diff] fail_to_pass
def test_fp8_dequantize_reverse_op():
    """Fp8Dequantize.reverse_op returns a working ConversionOps instead of raising NotImplementedError."""
    import torch
    from transformers.core_model_loading import ConversionOps

    try:
        from transformers.integrations.finegrained_fp8 import Fp8Dequantize
    except ImportError:
        # AST-only because: finegrained_fp8 may have GPU-dependent imports unavailable on CPU
        import ast

        src = open(f"{REPO}/src/transformers/integrations/finegrained_fp8.py").read()
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Fp8Dequantize":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "reverse_op":
                        for dec in item.decorator_list:
                            if isinstance(dec, ast.Name) and dec.id == "property":
                                found = True
                assert found, "Fp8Dequantize must have a @property reverse_op"
                return
        assert False, "Fp8Dequantize class not found"

    class MockQuantizer:
        class quantization_config:
            weight_block_size = None

    obj = Fp8Dequantize(MockQuantizer())
    rev = obj.reverse_op
    assert isinstance(rev, ConversionOps)

    t1 = torch.randn(8, 16)
    t2 = torch.zeros(8)
    data = {"layer.weight": t1, "layer.bias": t2}
    result = rev.convert(data)
    assert set(result.keys()) == set(data.keys())
    assert torch.equal(result["layer.weight"], t1)
    assert torch.equal(result["layer.bias"], t2)


# [pr_diff] fail_to_pass
def test_metal_dequantize_reverse_op():
    """MetalDequantize.reverse_op returns a working ConversionOps instead of raising NotImplementedError."""
    import torch
    from transformers.core_model_loading import ConversionOps

    try:
        from transformers.integrations.metal_quantization import MetalDequantize
    except ImportError:
        # AST-only because: metal_quantization may have GPU-dependent imports unavailable on CPU
        import ast

        src = open(f"{REPO}/src/transformers/integrations/metal_quantization.py").read()
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "MetalDequantize":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "reverse_op":
                        for dec in item.decorator_list:
                            if isinstance(dec, ast.Name) and dec.id == "property":
                                found = True
                assert found, "MetalDequantize must have a @property reverse_op"
                return
        assert False, "MetalDequantize class not found"

    class MockQuantizer:
        class quantization_config:
            bits = 4
            group_size = 32

    obj = MetalDequantize(MockQuantizer())
    rev = obj.reverse_op
    assert isinstance(rev, ConversionOps)

    data = {"layer.weight": torch.randn(16, 16), "layer.bias": torch.ones(16)}
    result = rev.convert(data)
    assert set(result.keys()) == set(data.keys())
    assert torch.equal(result["layer.weight"], data["layer.weight"])
    assert torch.equal(result["layer.bias"], data["layer.bias"])


# [pr_diff] fail_to_pass
def test_mxfp4_dequantize_reverse_op():
    """Mxfp4Dequantize.reverse_op returns a working ConversionOps instead of raising NotImplementedError."""
    import torch
    from transformers.core_model_loading import ConversionOps

    try:
        from transformers.integrations.mxfp4 import Mxfp4Dequantize
    except ImportError:
        # AST-only because: mxfp4 may have GPU-dependent imports unavailable on CPU
        import ast

        src = open(f"{REPO}/src/transformers/integrations/mxfp4.py").read()
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Mxfp4Dequantize":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "reverse_op":
                        for dec in item.decorator_list:
                            if isinstance(dec, ast.Name) and dec.id == "property":
                                found = True
                assert found, "Mxfp4Dequantize must have a @property reverse_op"
                return
        assert False, "Mxfp4Dequantize class not found"

    class MockQuantizer:
        class quantization_config:
            pass

    obj = Mxfp4Dequantize(MockQuantizer())
    rev = obj.reverse_op
    assert isinstance(rev, ConversionOps)

    data = {"attn.weight": torch.randn(32, 32)}
    result = rev.convert(data)
    assert torch.equal(result["attn.weight"], data["attn.weight"])


# [pr_diff] fail_to_pass
def test_reverse_op_identity_multiple_entries():
    """reverse_op.convert preserves all keys, values, and dtypes for multi-entry dicts."""
    import torch
    from transformers.core_model_loading import _IdentityOp

    rev = _IdentityOp()

    t_float32 = torch.randn(4, 4, dtype=torch.float32)
    t_float16 = torch.randn(2, 8, dtype=torch.float16)
    t_bfloat16 = torch.randn(6, 3, dtype=torch.bfloat16)
    data = {"w1": t_float32, "w2": t_float16, "w3": t_bfloat16}
    result = rev.convert(data)

    assert len(result) == 3
    assert torch.equal(result["w1"], t_float32)
    assert torch.equal(result["w2"], t_float16)
    assert torch.equal(result["w3"], t_bfloat16)
    assert result["w1"].dtype == torch.float32
    assert result["w2"].dtype == torch.float16
    assert result["w3"].dtype == torch.bfloat16


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_chunk_cat_reverse_op():
    """Existing Chunk/Cat reverse_op pair still works correctly."""
    from transformers.core_model_loading import Chunk, Cat

    chunk = Chunk(dim=0)
    rev = chunk.reverse_op
    assert isinstance(rev, Cat), f"Chunk.reverse_op should be Cat, got {type(rev)}"

    cat = Cat(dim=0)
    rev2 = cat.reverse_op
    assert isinstance(rev2, Chunk), f"Cat.reverse_op should be Chunk, got {type(rev2)}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / agent config files
# ---------------------------------------------------------------------------

def _get_agent_diff():
    """Get the diff of changes made by the agent (or gold patch) relative to base commit."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT],
        cwd=REPO, capture_output=True, text=True,
    )
    return r.stdout


# [agent_config] pass_to_pass — CLAUDE.md:2 @ 12b6b57
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
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


# [agent_config] pass_to_pass — CLAUDE.md:66 @ 12b6b57
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


# [agent_config] pass_to_pass — CLAUDE.md:67 @ 12b6b57
def test_no_modular_generated_files_edited():
    """Generated modeling files with a modular_ source must not be edited directly (CLAUDE.md line 67)."""
    import os

    r = subprocess.run(
        ["git", "diff", "--name-only", BASE_COMMIT],
        cwd=REPO, capture_output=True, text=True,
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


# [agent_config] pass_to_pass — .ai/skills/add-or-fix-type-checking/SKILL.md:180-186 @ 12b6b57
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


# [agent_config] pass_to_pass — .ai/skills/add-or-fix-type-checking/SKILL.md:189-190 @ 12b6b57
def test_no_assert_for_type_narrowing():
    """Do not use assert for type narrowing — use 'if ...: raise' instead."""
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
