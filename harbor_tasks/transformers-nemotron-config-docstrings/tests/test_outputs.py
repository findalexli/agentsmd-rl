"""
Task: transformers-nemotron-config-docstrings
Repo: huggingface/transformers @ 8dc7a52d766efe76c121c0654a5d24d633bffe9e
PR:   44803

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess

TARGET = "/workspace/transformers/src/transformers/models/nemotron_h/configuration_nemotron_h.py"


# ---------------------------------------------------------------------------
# Helpers — AST-only because: @strict/@auto_docstring decorators require
# heavy deps (huggingface_hub internals, torch optional) that may not be
# importable in the test environment. The task is about docstring text,
# which cannot be "called".
# ---------------------------------------------------------------------------


def _source():
    return open(TARGET).read()


def _class_node():
    """Return the NemotronHConfig class AST node."""
    tree = ast.parse(_source())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NemotronHConfig":
            return node
    raise AssertionError("NemotronHConfig class not found")


def _docstring():
    """Extract the raw docstring from the class."""
    cls = _class_node()
    if (
        cls.body
        and isinstance(cls.body[0], ast.Expr)
        and isinstance(cls.body[0].value, (ast.Constant, ast.Str))
    ):
        val = cls.body[0].value
        return val.value if isinstance(val, ast.Constant) else val.s
    raise AssertionError("NemotronHConfig has no docstring")


def _docstring_param_names():
    """Extract parameter names documented in the docstring (indented name followed by parens)."""
    return re.findall(r"^\s{4}(\w+)\s*\(", _docstring(), re.MULTILINE)


def _class_annotations():
    """Extract class-level annotated attribute names via AST."""
    cls = _class_node()
    names = []
    for node in cls.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.append(node.target.id)
    return names


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without syntax errors."""
    ast.parse(_source())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_docstring_params_match_class_annotations():
    """Every documented parameter in the docstring must be an actual class annotation."""
    doc_params = _docstring_param_names()
    assert len(doc_params) >= 5, f"Too few documented params: {len(doc_params)}"

    annotations = set(_class_annotations())
    assert len(annotations) >= 10, f"Too few class annotations: {len(annotations)}"

    bad = [p for p in doc_params if p not in annotations]
    assert not bad, f"Documented params not matching any class annotation: {sorted(set(bad))}"


# [pr_diff] fail_to_pass
def test_new_mamba_params_documented():
    """The four actual mamba attributes (n_groups, expand, use_conv_bias, chunk_size)
    must appear as documented parameters in the docstring."""
    doc_params = set(_docstring_param_names())
    required = {"n_groups", "expand", "use_conv_bias", "chunk_size"}
    missing = required - doc_params
    assert not missing, f"Required mamba params not documented: {sorted(missing)}"


# [pr_diff] fail_to_pass
def test_old_deprecated_names_removed():
    """Old backward-compat alias names must NOT appear as documented params.
    These are the mamba_dt_* names that only exist as __post_init__ aliases."""
    doc_params = set(_docstring_param_names())
    old_names = {"mamba_dt_min", "mamba_dt_max", "mamba_dt_limit", "mamba_dt_init_floor"}
    found_old = old_names & doc_params
    assert not found_old, f"Old deprecated names still documented: {sorted(found_old)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_existing_params_preserved():
    """Pre-existing documented params must remain in the docstring."""
    doc_params = set(_docstring_param_names())
    # These params exist in both the base and fixed versions
    existing = {
        "mamba_hidden_act", "mamba_ssm_cache_dtype",
        "moe_shared_expert_intermediate_size", "moe_latent_size",
        "use_mamba_kernels", "ssm_state_size",
        "num_logits_to_keep", "use_bias", "residual_in_fp32",
    }
    missing = existing - doc_params
    assert not missing, f"Existing params removed from docstring: {sorted(missing)}"


# [pr_diff] pass_to_pass
def test_backward_compat_aliases_in_post_init():
    """__post_init__ must still handle backward-compat aliases (mamba_dt_* → time_step_*)."""
    cls = _class_node()
    post_init = None
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__post_init__":
            post_init = node
            break
    assert post_init is not None, "__post_init__ method not found"

    source_lines = ast.get_source_segment(_source(), post_init)
    assert source_lines is not None, "Could not extract __post_init__ source"

    # Verify backward-compat aliases are still handled
    expected_aliases = ["mamba_dt_min", "mamba_dt_max", "mamba_dt_limit", "mamba_dt_init_floor"]
    for alias in expected_aliases:
        assert alias in source_lines, f"Backward-compat alias '{alias}' removed from __post_init__"


# [pr_diff] pass_to_pass
def test_annotation_defaults_consistent():
    """Class annotations for the four mamba params must have sensible defaults."""
    # AST-only because: verifying class-level defaults without importing heavy deps
    cls = _class_node()
    expected = {
        "n_groups": 8,
        "expand": 2,
        "use_conv_bias": True,
        "chunk_size": 128,
    }
    found = {}
    for node in cls.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            if name in expected and node.value is not None:
                if isinstance(node.value, ast.Constant):
                    found[name] = node.value.value
    for param, default in expected.items():
        assert param in found, f"Annotation for '{param}' not found in class body"
        assert found[param] == default, (
            f"{param}: expected default {default!r}, got {found[param]!r}"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:2 @ 8dc7a52d766efe76c121c0654a5d24d633bffe9e
def test_ruff_format():
    """make style runs ruff — modified file must pass ruff format check."""
    r = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", TARGET],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands from the repo
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass — from Makefile:check-repo (ruff check)
def test_repo_ruff_check():
    """Repo's ruff linter passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", TARGET],
        capture_output=True, text=True, timeout=60, cwd="/workspace/transformers",
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — from Makefile:check-repo (ruff format --check)
def test_repo_ruff_format_check():
    """Repo's ruff format check passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", TARGET],
        capture_output=True, text=True, timeout=60, cwd="/workspace/transformers",
    )
    assert r.returncode == 0, f"ruff format --check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — from Makefile:check-repo (check_inits.py)
def test_repo_check_inits():
    """Repo's init file consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        capture_output=True, text=True, timeout=120, cwd="/workspace/transformers",
    )
    assert r.returncode == 0, f"check_inits.py failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — from Makefile:check-repo (check_dummies.py)
def test_repo_check_dummies():
    """Repo's dummy objects check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_dummies.py"],
        capture_output=True, text=True, timeout=120, cwd="/workspace/transformers",
    )
    assert r.returncode == 0, f"check_dummies.py failed:\n{r.stderr[-500:]}"
