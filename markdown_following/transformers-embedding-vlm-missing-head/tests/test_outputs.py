"""
Task: transformers-embedding-vlm-missing-head
Repo: huggingface/transformers @ 05514c4bb641ba1537d17048fd93f50f45d5f19d
PR:   45000

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, "/workspace/repo/src")
REPO = Path("/workspace/repo")

MODIFIED_FILES = [
    "src/transformers/models/colpali/modeling_colpali.py",
    "src/transformers/models/colqwen2/modeling_colqwen2.py",
    "src/transformers/models/colqwen2/modular_colqwen2.py",
    "src/transformers/models/colmodernvbert/modeling_colmodernvbert.py",
    "src/transformers/conversion_mapping.py",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_class_method_source(filepath, class_name, method_name):
    """Extract source text of a method within a class using AST."""
    # AST-only because: VLM instantiation (vision+language model) exceeds 4GB container RAM
    src = filepath.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                    return ast.get_source_segment(src, item)
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without syntax errors."""
    for f in MODIFIED_FILES:
        source = (REPO / f).read_text()
        ast.parse(source)


# [pr_diff] pass_to_pass
def test_modules_import():
    """All affected modules import without errors."""
    from transformers.models.colpali.modeling_colpali import ColPaliForRetrieval
    from transformers.models.colqwen2.modeling_colqwen2 import ColQwen2ForRetrieval
    from transformers.models.colmodernvbert.modeling_colmodernvbert import (
        ColModernVBertForRetrieval,
    )
    from transformers.conversion_mapping import _build_checkpoint_conversion_mapping

    assert ColPaliForRetrieval is not None
    assert ColQwen2ForRetrieval is not None
    assert ColModernVBertForRetrieval is not None
    assert callable(_build_checkpoint_conversion_mapping)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — must use base model class, not causal LM
# AST-only because: VLM instantiation (vision+language model) exceeds 4GB container RAM
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_colpali_uses_base_model_class():
    """ColPali must not use AutoModelForImageTextToText (needs base model without LM head)."""
    src = (REPO / "src/transformers/models/colpali/modeling_colpali.py").read_text()
    assert "AutoModelForImageTextToText" not in src, (
        "ColPali should not use AutoModelForImageTextToText — "
        "retrieval models need a base model without the LM head"
    )


# [pr_diff] fail_to_pass
def test_colqwen2_uses_base_model_class():
    """ColQwen2 must not use AutoModelForImageTextToText (needs base model without LM head)."""
    src = (REPO / "src/transformers/models/colqwen2/modeling_colqwen2.py").read_text()
    assert "AutoModelForImageTextToText" not in src, (
        "ColQwen2 should not use AutoModelForImageTextToText — "
        "retrieval models need a base model without the LM head"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — forward() must call vlm directly, not through .model
# AST-only because: VLM instantiation (vision+language model) exceeds 4GB container RAM
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_colpali_forward_no_model_indirection():
    """ColPali forward must call self.vlm() directly, not self.vlm.model()."""
    fpath = REPO / "src/transformers/models/colpali/modeling_colpali.py"
    fwd = _get_class_method_source(fpath, "ColPaliForRetrieval", "forward")
    assert fwd is not None, "Could not find ColPaliForRetrieval.forward()"
    assert "self.vlm.model(" not in fwd, (
        "forward() calls self.vlm.model() — with a base model (no head), "
        "the VLM should be called directly via self.vlm()"
    )
    assert "self.vlm(" in fwd, (
        "forward() should contain a call to self.vlm() for the VLM forward pass"
    )


# [pr_diff] fail_to_pass
def test_colqwen2_forward_no_model_indirection():
    """ColQwen2 forward must not go through self.vlm.model (use self.vlm directly)."""
    fpath = REPO / "src/transformers/models/colqwen2/modeling_colqwen2.py"
    fwd = _get_class_method_source(fpath, "ColQwen2ForRetrieval", "forward")
    assert fwd is not None, "Could not find ColQwen2ForRetrieval.forward()"
    assert "self.vlm.model(" not in fwd, (
        "forward() calls self.vlm.model() — with a base model (no head), "
        "the VLM should be called directly via self.vlm()"
    )
    assert "self.vlm.model.visual(" not in fwd, (
        "forward() calls self.vlm.model.visual() — with a base model, "
        "visual should be accessed via self.vlm.visual()"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — base_model_prefix must be set to 'vlm'
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_colpali_base_model_prefix():
    """ColPaliForRetrieval.base_model_prefix must be 'vlm'."""
    from transformers.models.colpali.modeling_colpali import ColPaliForRetrieval

    assert ColPaliForRetrieval.base_model_prefix == "vlm", (
        f"Expected base_model_prefix='vlm', got {ColPaliForRetrieval.base_model_prefix!r}"
    )


# [pr_diff] fail_to_pass
def test_colqwen2_base_model_prefix():
    """ColQwen2ForRetrieval.base_model_prefix must be 'vlm'."""
    from transformers.models.colqwen2.modeling_colqwen2 import ColQwen2ForRetrieval

    assert ColQwen2ForRetrieval.base_model_prefix == "vlm", (
        f"Expected base_model_prefix='vlm', got {ColQwen2ForRetrieval.base_model_prefix!r}"
    )


# [pr_diff] fail_to_pass
def test_colmodernvbert_base_model_prefix():
    """ColModernVBertForRetrieval.base_model_prefix must be 'vlm'."""
    from transformers.models.colmodernvbert.modeling_colmodernvbert import (
        ColModernVBertForRetrieval,
    )

    assert ColModernVBertForRetrieval.base_model_prefix == "vlm", (
        f"Expected base_model_prefix='vlm', got {ColModernVBertForRetrieval.base_model_prefix!r}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — conversion mapping changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_colqwen2_conversion_mapping():
    """colqwen2 must exist in the checkpoint conversion mapping."""
    from transformers.conversion_mapping import _build_checkpoint_conversion_mapping

    mapping = _build_checkpoint_conversion_mapping()
    assert "colqwen2" in mapping, (
        f"colqwen2 not in conversion mapping; keys: {sorted(mapping.keys())}"
    )


# [agent_config] fail_to_pass — CLAUDE.md:67 @ 05514c4bb641ba1537d17048fd93f50f45d5f19d
def test_modular_colqwen2_no_model_indirection():
    """modular_colqwen2.py (source of truth) must also call self.vlm() directly, not self.vlm.model().

    CLAUDE.md line 67: when a modular file is present it is the authoritative source;
    the fix must be present there, not only in the generated modeling file.
    """
    fpath = REPO / "src/transformers/models/colqwen2/modular_colqwen2.py"
    fwd = _get_class_method_source(fpath, "ColQwen2ForRetrieval", "forward")
    assert fwd is not None, "Could not find ColQwen2ForRetrieval.forward() in modular_colqwen2.py"
    assert "self.vlm.model(" not in fwd, (
        "modular_colqwen2.py forward() still calls self.vlm.model() — "
        "the modular file is the source of truth and must also contain the fix"
    )
    assert "self.vlm.model.visual(" not in fwd, (
        "modular_colqwen2.py forward() still calls self.vlm.model.visual() — "
        "with a base model, visual should be accessed via self.vlm.visual()"
    )


# [pr_diff] fail_to_pass
def test_colpali_no_conversion_mapping():
    """colpali entry must be removed from conversion mapping.

    With AutoModel (base model), the old vlm->vlm.model weight renaming
    is no longer needed and causes incorrect weight loading.
    """
    from transformers.conversion_mapping import _build_checkpoint_conversion_mapping

    mapping = _build_checkpoint_conversion_mapping()
    assert "colpali" not in mapping, (
        "colpali should not have a conversion mapping entry — "
        "with base model, no vlm->vlm.model renaming is needed"
    )


# ---------------------------------------------------------------------------
# Repo CI tests (pass_to_pass, repo_tests) — subprocess.run() commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    r = subprocess.run(
        [
            "ruff",
            "check",
            "src/transformers/models/colpali/modeling_colpali.py",
            "src/transformers/models/colqwen2/modeling_colqwen2.py",
            "src/transformers/models/colmodernvbert/modeling_colmodernvbert.py",
            "src/transformers/conversion_mapping.py",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    r = subprocess.run(
        [
            "ruff",
            "format",
            "--check",
            "src/transformers/models/colpali/modeling_colpali.py",
            "src/transformers/models/colqwen2/modeling_colqwen2.py",
            "src/transformers/models/colmodernvbert/modeling_colmodernvbert.py",
            "src/transformers/conversion_mapping.py",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_unittest_colpali():
    """ColPali unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "datasets", "parameterized", "-q"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    r = subprocess.run(
        [
            "python",
            "-m",
            "unittest",
            "tests.models.colpali.test_modeling_colpali.ColPaliForRetrievalModelTest.test_can_be_initialized_on_meta",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ColPali unit test failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unittest_colqwen2():
    """ColQwen2 unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "datasets", "parameterized", "-q"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    r = subprocess.run(
        [
            "python",
            "-m",
            "unittest",
            "tests.models.colqwen2.test_modeling_colqwen2.ColQwen2ForRetrievalModelTest.test_can_be_initialized_on_meta",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ColQwen2 unit test failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unittest_colmodernvbert():
    """ColModernVBert unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "datasets", "parameterized", "Pillow", "-q"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    r = subprocess.run(
        [
            "python",
            "-m",
            "unittest",
            "tests.models.colmodernvbert.test_modeling_colmodernvbert.ColModernVBertForRetrievalModelTest.test_can_be_initialized_on_meta",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ColModernVBert unit test failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_missing_keys_colpali():
    """ColPali missing keys test passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "datasets", "parameterized", "-q"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    r = subprocess.run(
        [
            "python",
            "-m",
            "unittest",
            "tests.models.colpali.test_modeling_colpali.ColPaliForRetrievalModelTest.test_correct_missing_keys",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ColPali missing keys test failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_missing_keys_colqwen2():
    """ColQwen2 missing keys test passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "datasets", "parameterized", "-q"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    r = subprocess.run(
        [
            "python",
            "-m",
            "unittest",
            "tests.models.colqwen2.test_modeling_colqwen2.ColQwen2ForRetrievalModelTest.test_correct_missing_keys",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ColQwen2 missing keys test failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
