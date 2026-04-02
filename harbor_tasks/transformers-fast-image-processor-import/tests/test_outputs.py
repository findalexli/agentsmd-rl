"""
Task: transformers-fast-image-processor-import
Repo: huggingface/transformers @ 29db503cdef2f00d1f0ecd5841c3a486708ed1dd
PR:   44926

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

REPO = "/workspace/transformers"
sys.path.insert(0, f"{REPO}/src")


def _find_image_processor_models():
    """Find models that have image_processing_*.py files (not _fast)."""
    models_dir = Path(f"{REPO}/src/transformers/models")
    results = []
    for proc_file in sorted(models_dir.rglob("image_processing_*.py")):
        if proc_file.stem.endswith("_fast"):
            continue
        model_name = proc_file.parent.name
        module_name = proc_file.stem
        words = model_name.replace("_", "-").split("-")
        camel = "".join(w.title() for w in words)
        results.append((model_name, module_name, camel))
    return results


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import ast

    for rel in [
        "src/transformers/__init__.py",
        "utils/check_repo.py",
    ]:
        source = Path(f"{REPO}/{rel}").read_text()
        ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_import_fast_module():
    """Importing from image_processing_*_fast module paths must not raise ModuleNotFoundError."""
    # Test specific known models to prevent gaming via dynamic discovery
    known_models = [
        ("llama4", "image_processing_llama4"),
        ("clip", "image_processing_clip"),
        ("vit", "image_processing_vit"),
    ]

    imported = 0
    for model_name, module_name in known_models:
        fast_module = f"transformers.models.{model_name}.{module_name}_fast"
        try:
            importlib.import_module(fast_module)
            imported += 1
        except ModuleNotFoundError:
            pytest.fail(f"ModuleNotFoundError importing {fast_module}")
        except ImportError:
            imported += 1  # missing optional deps ≠ missing module

    assert imported >= 1, "Could not import any fast module alias"

    # Also test dynamically discovered models to verify the fix is general
    models = _find_image_processor_models()
    assert len(models) > 0, "No image_processing files found in repo"

    dynamic_imported = 0
    for model_name, module_name, _camel in models[:8]:
        fast_module = f"transformers.models.{model_name}.{module_name}_fast"
        try:
            importlib.import_module(fast_module)
            dynamic_imported += 1
        except ModuleNotFoundError:
            pytest.fail(f"ModuleNotFoundError importing {fast_module}")
        except ImportError:
            dynamic_imported += 1
    assert dynamic_imported >= 3, "Could not import at least 3 fast module aliases"


# [pr_diff] fail_to_pass
def test_class_redirect_fast_to_normal():
    """XImageProcessorFast imported from alias module resolves to XImageProcessor."""
    models = _find_image_processor_models()
    assert len(models) > 0

    verified = 0
    for model_name, module_name, camel in models[:8]:
        fast_mod_name = f"transformers.models.{model_name}.{module_name}_fast"
        real_mod_name = f"transformers.models.{model_name}.{module_name}"
        fast_cls_name = f"{camel}ImageProcessorFast"
        real_cls_name = f"{camel}ImageProcessor"

        try:
            fast_mod = importlib.import_module(fast_mod_name)
            real_mod = importlib.import_module(real_mod_name)
        except ImportError:
            continue

        try:
            cls_from_alias = getattr(fast_mod, fast_cls_name)
            cls_from_real = getattr(real_mod, real_cls_name)
        except AttributeError:
            continue

        assert cls_from_alias is cls_from_real, (
            f"{fast_cls_name} from alias is not the same object as {real_cls_name}"
        )
        verified += 1

    assert verified >= 1, "Could not verify class redirect for any model"


# [pr_diff] fail_to_pass
def test_check_repo_ignores_fast_aliases():
    """ignore_undocumented() returns True for image_processing_*_fast names."""
    sys.path.insert(0, REPO)
    from utils.check_repo import ignore_undocumented

    # Test several model names to prevent hardcoding
    for name in [
        "image_processing_llama4_fast",
        "image_processing_clip_fast",
        "image_processing_vit_fast",
        "image_processing_blip_fast",
        "image_processing_detr_fast",
    ]:
        assert ignore_undocumented(name), (
            f"ignore_undocumented('{name}') returned False, expected True"
        )

    # Verify non-fast names are NOT ignored (specificity check)
    assert not ignore_undocumented("image_processing_clip"), (
        "ignore_undocumented should NOT ignore non-_fast image processing names"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_imports_preserved():
    """Existing module aliases and core imports still work after changes."""
    from transformers import AutoTokenizer, AutoImageProcessor
    from transformers import image_processing_utils_fast

    # Verify they are real classes/modules, not stubs
    assert hasattr(AutoTokenizer, "from_pretrained"), (
        "AutoTokenizer missing from_pretrained method"
    )
    assert hasattr(AutoImageProcessor, "from_pretrained"), (
        "AutoImageProcessor missing from_pretrained method"
    )
    assert hasattr(image_processing_utils_fast, "__name__"), (
        "image_processing_utils_fast is not a real module"
    )


# [static] pass_to_pass
def test_not_stub():
    """Modified files retain original content (not gutted or replaced with stubs)."""
    init_py = Path(f"{REPO}/src/transformers/__init__.py").read_text()
    init_lines = len(init_py.splitlines())
    assert init_lines >= 500, f"__init__.py only {init_lines} lines"
    # Verify key content still present
    assert "_create_module_alias" in init_py, "__init__.py missing _create_module_alias"
    assert "image_processing_utils_fast" in init_py, "__init__.py missing image_processing_utils_fast alias"

    check_repo = Path(f"{REPO}/utils/check_repo.py").read_text()
    assert "ignore_undocumented" in check_repo, "check_repo.py missing ignore_undocumented function"
    assert len(check_repo.splitlines()) >= 500, "check_repo.py too short"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:66 @ 29db503cdef2f00d1f0ecd5841c3a486708ed1dd
def test_no_copied_from_blocks_edited():
    """Changes must not alter lines inside '# Copied from' blocks in __init__.py."""
    # AST-only because: need to compare git state, not execute code
    init_path = f"{REPO}/src/transformers/__init__.py"
    current = Path(init_path).read_text()

    # Verify # Copied from blocks still exist and are intact
    # The __init__.py has Copied from blocks; verify they weren't removed or mangled
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "src/transformers/__init__.py"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    diff_output = r.stdout
    # If diff touches a "# Copied from" line, that's a violation
    for line in diff_output.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            assert "# Copied from" not in line, (
                "Diff adds/modifies a '# Copied from' block — these are managed by make fix-repo"
            )
        if line.startswith("-") and not line.startswith("---"):
            assert "# Copied from" not in line, (
                "Diff removes a '# Copied from' block — these are managed by make fix-repo"
            )
