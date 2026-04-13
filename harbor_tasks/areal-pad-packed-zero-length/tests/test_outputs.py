"""
Task: areal-pad-packed-zero-length
Repo: inclusionAI/AReaL @ c961323ec4d989a52c78e5b42fc32f665367949f
PR:   #1104

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """areal/utils/data.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(f"{REPO}/areal/utils/data.py", doraise=True)


# [repo_tests] pass_to_pass — repo's ruff lint check (from .github/workflows/pre-commit.yml)
def test_ruff_lint():
    """Ruff linter passes on areal/utils/data.py (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/areal/utils/data.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — repo's ruff format check (from .github/workflows/pre-commit.yml)
def test_ruff_format():
    """Ruff format check passes on areal/utils/data.py (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/areal/utils/data.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — repo's ruff lint check on multiple core files
def test_ruff_lint_core_utils():
    """Ruff linter passes on core areal/utils files (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Check specific core files that are properly formatted
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/areal/utils/data.py", f"{REPO}/areal/utils/constants.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint on core utils files failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — trailing whitespace check (from .pre-commit-config.yaml)
def test_no_trailing_whitespace():
    """No trailing whitespace in areal/utils/data.py (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-n", "[[:space:]]$", f"{REPO}/areal/utils/data.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 1, f"Found trailing whitespace:\n{r.stdout}"


# [repo_tests] pass_to_pass — newline at EOF check (from .pre-commit-config.yaml)
def test_newline_at_eof():
    """areal/utils/data.py ends with a newline (pass_to_pass)."""
    r = subprocess.run(
        f'tail -c1 "{REPO}/areal/utils/data.py" | od -An -tx1 | grep -q "0a"',
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, "File does not end with a newline"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_extra_cu_seqlens_when_no_padding():
    """When total_length == pad_to_length, cu_seqlens must not gain an extra entry."""
    import sys
    sys.path.insert(0, REPO)
    import torch
    from areal.utils.data import pad_packed_tensor_dict

    cu_seqlens = torch.tensor([0, 4, 10], dtype=torch.long)
    data = {
        "cu_seqlens": cu_seqlens,
        "max_seqlen": 6,
        "input_ids": torch.arange(10, dtype=torch.long),
    }
    result_data, pad_len, old_cu, align_len = pad_packed_tensor_dict(data, pad_to_length=10)

    assert pad_len == 0, f"Expected pad_length=0, got {pad_len}"
    assert result_data["cu_seqlens"].shape[0] == 3, (
        f"cu_seqlens should be unchanged (length 3), got {result_data['cu_seqlens'].shape[0]}"
    )
    # No zero-length segment
    cs = result_data["cu_seqlens"]
    for i in range(cs.shape[0] - 1):
        seg = (cs[i + 1] - cs[i]).item()
        assert seg > 0, f"Zero-length segment at index {i}: {cs.tolist()}"


# [pr_diff] fail_to_pass
def test_data_unchanged_when_no_padding():
    """When pad_length==0, returned data dict must be the exact same object (no copies)."""
    import sys
    sys.path.insert(0, REPO)
    import torch
    from areal.utils.data import pad_packed_tensor_dict

    cu_seqlens = torch.tensor([0, 5, 10], dtype=torch.long)
    input_ids = torch.arange(10, dtype=torch.long)
    data = {
        "cu_seqlens": cu_seqlens,
        "max_seqlen": 5,
        "input_ids": input_ids,
    }
    result_data, pad_len, old_cu, align_len = pad_packed_tensor_dict(data, pad_to_length=10)

    assert pad_len == 0, f"Expected pad_length=0, got {pad_len}"
    # cu_seqlens must not gain extra entries
    assert result_data["cu_seqlens"].shape[0] == cu_seqlens.shape[0], (
        f"cu_seqlens grew from {cu_seqlens.shape[0]} to {result_data['cu_seqlens'].shape[0]}"
    )
    assert torch.equal(result_data["input_ids"], input_ids), "input_ids were modified"
    assert result_data["max_seqlen"] == 5, f"max_seqlen changed to {result_data['max_seqlen']}"


# [pr_diff] fail_to_pass
def test_single_sequence_no_padding():
    """Single-sequence batch where total_length == pad_to_length returns unchanged."""
    import sys
    sys.path.insert(0, REPO)
    import torch
    from areal.utils.data import pad_packed_tensor_dict

    cu_seqlens = torch.tensor([0, 8], dtype=torch.long)
    data = {
        "cu_seqlens": cu_seqlens,
        "max_seqlen": 8,
        "input_ids": torch.ones(8, dtype=torch.long),
    }
    result_data, pad_len, old_cu, align_len = pad_packed_tensor_dict(data, pad_to_length=8)

    assert pad_len == 0
    assert result_data["cu_seqlens"].shape[0] == 2, "cu_seqlens should remain length 2"
    assert torch.equal(result_data["input_ids"], data["input_ids"])


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_normal_padding_works():
    """Normal padding (pad_length > 0) still appends correctly."""
    import sys
    sys.path.insert(0, REPO)
    import torch
    from areal.utils.data import pad_packed_tensor_dict

    cu_seqlens = torch.tensor([0, 3, 7], dtype=torch.long)
    data = {
        "cu_seqlens": cu_seqlens,
        "max_seqlen": 4,
        "input_ids": torch.arange(7, dtype=torch.long),
    }
    result_data, pad_len, old_cu, align_len = pad_packed_tensor_dict(data, pad_to_length=12)

    assert pad_len == 5, f"Expected pad_length=5, got {pad_len}"
    assert result_data["cu_seqlens"].shape[0] == 4, (
        f"Expected 4 cu_seqlens entries, got {result_data['cu_seqlens'].shape[0]}"
    )
    assert result_data["cu_seqlens"][-1].item() == 12
    assert result_data["input_ids"].shape[0] == 12
    assert result_data["max_seqlen"] >= 5


# [repo_tests] pass_to_pass
def test_pad_to_length_too_small_raises():
    """pad_to_length < total_length must raise ValueError."""
    import sys
    sys.path.insert(0, REPO)
    import torch
    import pytest
    from areal.utils.data import pad_packed_tensor_dict

    cu_seqlens = torch.tensor([0, 5, 10], dtype=torch.long)
    data = {
        "cu_seqlens": cu_seqlens,
        "max_seqlen": 5,
        "input_ids": torch.arange(10, dtype=torch.long),
    }
    with pytest.raises(ValueError):
        pad_packed_tensor_dict(data, pad_to_length=5)


# [repo_tests] pass_to_pass
def test_old_cu_seqlens_returned():
    """Returned old_cu_seqlens matches the original cu_seqlens."""
    import sys
    sys.path.insert(0, REPO)
    import torch
    from areal.utils.data import pad_packed_tensor_dict

    cu_seqlens = torch.tensor([0, 3, 7], dtype=torch.long)
    data = {
        "cu_seqlens": cu_seqlens.clone(),
        "max_seqlen": 4,
        "input_ids": torch.arange(7, dtype=torch.long),
    }
    result_data, pad_len, old_cu, align_len = pad_packed_tensor_dict(data, pad_to_length=12)
    assert torch.equal(old_cu, cu_seqlens)


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """pad_packed_tensor_dict has substantive logic, not a stub."""
    import ast

    src = Path(f"{REPO}/areal/utils/data.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "pad_packed_tensor_dict":
            stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
            assert len(stmts) >= 5, f"Function body too short ({len(stmts)} stmts)"
            return
    raise AssertionError("pad_packed_tensor_dict not found")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:93 @ c961323ec4d989a52c78e5b42fc32f665367949f
def test_no_wildcard_imports():
    """No wildcard imports in areal/utils/data.py (CLAUDE.md hard rule)."""
    import ast

    src = Path(f"{REPO}/areal/utils/data.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.names:
            for alias in node.names:
                assert alias.name != "*", f"Wildcard import from {node.module}"


# [agent_config] pass_to_pass — AGENTS.md:90 @ c961323ec4d989a52c78e5b42fc32f665367949f
def test_no_print_statements():
    """No print() calls in areal/utils/data.py (AGENTS.md hard rule: use getLogger, never print)."""
    import ast

    src = Path(f"{REPO}/areal/utils/data.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                raise AssertionError(
                    f"print() call found at line {node.lineno} in areal/utils/data.py"
                )


# [agent_config] pass_to_pass — AGENTS.md:40 @ c961323ec4d989a52c78e5b42fc32f665367949f
def test_returns_consistent_tuple():
    """Function returns 4-tuple for both padding and no-padding cases (existing pattern)."""
    import sys
    sys.path.insert(0, REPO)
    import torch
    from areal.utils.data import pad_packed_tensor_dict

    # Case 1: no padding needed
    data_no_pad = {
        "cu_seqlens": torch.tensor([0, 4, 10], dtype=torch.long),
        "max_seqlen": 6,
        "input_ids": torch.arange(10, dtype=torch.long),
    }
    r1 = pad_packed_tensor_dict(data_no_pad, pad_to_length=10)
    assert isinstance(r1, tuple) and len(r1) == 4, f"No-pad case: expected 4-tuple, got {type(r1)}"

    # Case 2: padding needed
    data_pad = {
        "cu_seqlens": torch.tensor([0, 3, 7], dtype=torch.long),
        "max_seqlen": 4,
        "input_ids": torch.arange(7, dtype=torch.long),
    }
    r2 = pad_packed_tensor_dict(data_pad, pad_to_length=12)
    assert isinstance(r2, tuple) and len(r2) == 4, f"Pad case: expected 4-tuple, got {type(r2)}"
