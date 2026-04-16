"""
Task: transformers-nemotron-config-docstrings
Repo: huggingface/transformers @ 8dc7a52d766efe76c121c0654a5d24d633bffe9e
PR:   44803

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import textwrap

TARGET = "/workspace/transformers/src/transformers/models/nemotron_h/configuration_nemotron_h.py"


# ---------------------------------------------------------------------------
# Helpers — run structural analysis as a subprocess.  Direct import fails
# because @auto_docstring decorator requires torch (not installed).
# ---------------------------------------------------------------------------

_ANALYSIS_SCRIPT = textwrap.dedent("""\
import ast
import json
import re
import sys

target = sys.argv[1]
source = open(target).read()
tree = ast.parse(source)

cls = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "NemotronHConfig":
        cls = node
        break

if cls is None:
    json.dump({"error": "NemotronHConfig not found"}, sys.stdout)
    sys.exit(1)

docstring = ""
if (cls.body and isinstance(cls.body[0], ast.Expr)
        and isinstance(cls.body[0].value, (ast.Constant, ast.Str))):
    val = cls.body[0].value
    docstring = val.value if isinstance(val, ast.Constant) else val.s

doc_params = re.findall(r"^\\s{4}(\\w+)\\s*\\(", docstring, re.MULTILINE)

annotations = []
defaults = {}
for node in cls.body:
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        name = node.target.id
        annotations.append(name)
        if node.value is not None and isinstance(node.value, ast.Constant):
            defaults[name] = node.value.value

has_post_init = False
alias_names = []
for node in cls.body:
    if isinstance(node, ast.FunctionDef) and node.name == "__post_init__":
        has_post_init = True
        for child in ast.walk(node):
            if (isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Attribute)
                    and child.func.attr == "pop"
                    and isinstance(child.func.value, ast.Name)
                    and child.func.value.id == "kwargs"
                    and child.args
                    and isinstance(child.args[0], ast.Constant)):
                alias_names.append(child.args[0].value)
        break

json.dump({
    "doc_params": doc_params,
    "annotations": annotations,
    "defaults": defaults,
    "has_post_init": has_post_init,
    "alias_names": alias_names,
}, sys.stdout)
""")


def _analyze():
    """Run AST analysis as a subprocess and return parsed structural data."""
    r = subprocess.run(
        ["python3", "-c", _ANALYSIS_SCRIPT, TARGET],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Analysis subprocess failed:\n{r.stderr}"
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without syntax errors."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{TARGET}').read())"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_docstring_params_match_class_annotations():
    """Every documented parameter in the docstring must be an actual class annotation."""
    data = _analyze()
    doc_params = data["doc_params"]
    annotations = set(data["annotations"])

    assert len(doc_params) >= 5, f"Too few documented params: {len(doc_params)}"
    assert len(annotations) >= 10, f"Too few class annotations: {len(annotations)}"

    bad = [p for p in doc_params if p not in annotations]
    assert not bad, f"Documented params not matching any class annotation: {sorted(set(bad))}"


# [pr_diff] fail_to_pass
def test_new_mamba_params_documented():
    """Class annotations for mamba attributes must appear as documented parameters."""
    data = _analyze()
    doc_params = set(data["doc_params"])
    annotations = set(data["annotations"])

    # These are the actual class annotations for mamba layer attributes
    required = {"n_groups", "expand", "use_conv_bias", "chunk_size"}
    assert required <= annotations, (
        f"Expected annotations not found in class: {sorted(required - annotations)}"
    )
    missing = required - doc_params
    assert not missing, f"Required mamba params not documented: {sorted(missing)}"


# [pr_diff] fail_to_pass
def test_old_deprecated_names_removed():
    """Backward-compat kwargs aliases from __post_init__ must not appear as documented params."""
    data = _analyze()
    doc_params = set(data["doc_params"])
    annotations = set(data["annotations"])
    alias_names = set(data["alias_names"])

    assert len(alias_names) > 0, "__post_init__ should contain backward-compat aliases"

    # Alias names that are NOT class annotations must not be documented
    non_annotation_aliases = alias_names - annotations
    found_old = non_annotation_aliases & doc_params
    assert not found_old, f"Backward-compat aliases still documented as params: {sorted(found_old)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_existing_params_preserved():
    """Pre-existing documented params must remain in the docstring."""
    data = _analyze()
    doc_params = set(data["doc_params"])
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
    """__post_init__ must still handle backward-compat aliases."""
    data = _analyze()
    assert data["has_post_init"], "__post_init__ method not found"

    alias_names = set(data["alias_names"])
    assert len(alias_names) >= 4, (
        f"Expected at least 4 backward-compat aliases in __post_init__, found {len(alias_names)}"
    )
    # Verify specific backward-compat aliases are still handled
    expected_aliases = {"mamba_dt_min", "mamba_dt_max", "mamba_dt_limit", "mamba_dt_init_floor"}
    missing = expected_aliases - alias_names
    assert not missing, f"Backward-compat aliases removed from __post_init__: {sorted(missing)}"


# [pr_diff] pass_to_pass
def test_annotation_defaults_consistent():
    """Class annotations for mamba params must have sensible defaults."""
    data = _analyze()
    defaults = data["defaults"]

    expected = {
        "n_groups": 8,
        "expand": 2,
        "use_conv_bias": True,
        "chunk_size": 128,
    }
    for param, default in expected.items():
        assert param in defaults, f"Annotation for '{param}' not found in class body"
        assert defaults[param] == default, (
            f"{param}: expected default {default!r}, got {defaults[param]!r}"
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
