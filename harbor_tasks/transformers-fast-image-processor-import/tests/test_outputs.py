"""
Task: transformers-fast-image-processor-import
Repo: huggingface/transformers @ 29db503cdef2f00d1f0ecd5841c3a486708ed1dd
PR:   44926

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
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
    # Use subprocess so transformers init runs in a clean process
    script = """
import importlib, sys
sys.path.insert(0, '/workspace/transformers/src')

models = [
    ("llama4", "image_processing_llama4"),
    ("clip", "image_processing_clip"),
    ("vit", "image_processing_vit"),
]
imported = 0
for model_name, module_name in models:
    fast = f"transformers.models.{model_name}.{module_name}_fast"
    try:
        importlib.import_module(fast)
        imported += 1
    except ModuleNotFoundError:
        print(f"FAIL: {fast}")
        sys.exit(1)
    except ImportError:
        imported += 1  # missing optional deps != missing module

# Also test dynamic discovery
from pathlib import Path
models_dir = Path('/workspace/transformers/src/transformers/models')
dynamic = 0
for pf in sorted(models_dir.rglob("image_processing_*.py"))[:8]:
    if pf.stem.endswith("_fast"):
        continue
    mn = pf.parent.name
    mod = pf.stem
    fast = f"transformers.models.{mn}.{mod}_fast"
    try:
        importlib.import_module(fast)
        dynamic += 1
    except ModuleNotFoundError:
        print(f"FAIL: {fast}")
        sys.exit(1)
    except ImportError:
        dynamic += 1

assert dynamic >= 3, f"Only imported {dynamic} dynamic aliases"
print(f"OK: {imported} known + {dynamic} dynamic")
"""
    r = subprocess.run(
        ["python3", "-c", script],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Fast module import failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_class_redirect_fast_to_normal():
    """XImageProcessorFast imported from alias module resolves to XImageProcessor."""
    script = """
import importlib, sys
sys.path.insert(0, '/workspace/transformers/src')
from pathlib import Path

models_dir = Path('/workspace/transformers/src/transformers/models')
verified = 0
for pf in sorted(models_dir.rglob("image_processing_*.py"))[:8]:
    if pf.stem.endswith("_fast"):
        continue
    mn = pf.parent.name
    mod = pf.stem
    words = mn.replace("_", "-").split("-")
    camel = "".join(w.title() for w in words)

    fast_mod_name = f"transformers.models.{mn}.{mod}_fast"
    real_mod_name = f"transformers.models.{mn}.{mod}"
    fast_cls = f"{camel}ImageProcessorFast"
    real_cls = f"{camel}ImageProcessor"

    try:
        fast_mod = importlib.import_module(fast_mod_name)
        real_mod = importlib.import_module(real_mod_name)
    except ImportError:
        continue
    try:
        cls_a = getattr(fast_mod, fast_cls)
        cls_b = getattr(real_mod, real_cls)
    except AttributeError:
        continue
    assert cls_a is cls_b, f"{fast_cls} != {real_cls}"
    verified += 1

assert verified >= 1, f"Verified {verified} redirects, need at least 1"
print(f"OK: {verified} class redirects verified")
"""
    r = subprocess.run(
        ["python3", "-c", script],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Class redirect test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_check_repo_ignores_fast_aliases():
    """ignore_undocumented() returns True for image_processing_*_fast names."""
    # AST-only because: check_repo.py imports heavy transformers internals at module level
    import os

    source = Path(f"{REPO}/utils/check_repo.py").read_text()
    tree = ast.parse(source)

    func_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "ignore_undocumented":
            func_src = ast.get_source_segment(source, node)
            break
    assert func_src is not None, "ignore_undocumented function not found in check_repo.py"

    # Execute with mocked module-level constants
    ns = {
        "os": os,
        "PATH_TO_TRANSFORMERS": f"{REPO}/src/transformers",
        "DEPRECATED_OBJECTS": set(),
        "UNDOCUMENTED_OBJECTS": set(),
        "SHOULD_HAVE_THEIR_OWN_PAGE": set(),
    }
    exec(compile(ast.parse(func_src), "<check_repo>", "exec"), ns)
    ignore_fn = ns["ignore_undocumented"]

    # These _fast alias names must be ignored
    for name in [
        "image_processing_llama4_fast",
        "image_processing_clip_fast",
        "image_processing_vit_fast",
        "image_processing_blip_fast",
        "image_processing_detr_fast",
    ]:
        assert ignore_fn(name), f"ignore_undocumented('{name}') returned False"

    # Non-fast names must NOT be ignored by this rule
    assert not ignore_fn("image_processing_clip"), (
        "ignore_undocumented should NOT ignore non-_fast image processing names"
    )
    # Unrelated names must not be affected
    assert not ignore_fn("SomeRandomClass"), (
        "ignore_undocumented should not ignore unrelated names"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_imports_preserved():
    """Existing module aliases and core imports still work after changes."""
    script = """
import sys, importlib
sys.path.insert(0, '/workspace/transformers/src')
import transformers
# Core module must load and have expected attributes
assert hasattr(transformers, '__version__'), 'transformers missing __version__'
assert 'AutoImageProcessor' in dir(transformers), 'AutoImageProcessor not exported'
# Existing image_processing_utils_fast alias must still resolve
m = importlib.import_module('transformers.image_processing_utils_fast')
assert hasattr(m, '__name__'), 'image_processing_utils_fast is not a real module'
# tokenization_utils alias (pre-existing) must still work
m2 = importlib.import_module('transformers.tokenization_utils')
assert hasattr(m2, '__name__'), 'tokenization_utils alias broken'
print('OK')
"""
    r = subprocess.run(
        ["python3", "-c", script],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Existing imports broken:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Modified files retain original content (not gutted or replaced with stubs)."""
    init_py = Path(f"{REPO}/src/transformers/__init__.py").read_text()
    init_lines = len(init_py.splitlines())
    assert init_lines >= 500, f"__init__.py only {init_lines} lines"
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
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "src/transformers/__init__.py"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    diff_output = r.stdout
    for line in diff_output.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            assert "# Copied from" not in line, (
                "Diff adds/modifies a '# Copied from' block — these are managed by make fix-repo"
            )
        if line.startswith("-") and not line.startswith("---"):
            assert "# Copied from" not in line, (
                "Diff removes a '# Copied from' block — these are managed by make fix-repo"
            )


# [agent_config] pass_to_pass — CLAUDE.md:67 @ 29db503cdef2f00d1f0ecd5841c3a486708ed1dd
def test_no_modular_generated_files_edited():
    """Changes must not edit files generated from modular_*.py files."""
    # Check that the diff doesn't touch any modeling_*.py that has a corresponding modular_*.py
    r = subprocess.run(
        ["git", "diff", "HEAD", "--name-only"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    changed_files = r.stdout.strip().splitlines()
    for f in changed_files:
        if "/modeling_" in f:
            # Check if a modular file exists for this model
            model_dir = str(Path(f).parent)
            model_name = Path(f).stem.replace("modeling_", "")
            modular_path = Path(f"{REPO}/{model_dir}/modular_{model_name}.py")
            assert not modular_path.exists(), (
                f"{f} is generated from {modular_path.name} — edit the modular file instead"
            )


# [agent_config] pass_to_pass — CLAUDE.md:2 @ 29db503cdef2f00d1f0ecd5841c3a486708ed1dd
def test_ruff_style_check():
    """Modified files pass ruff style checks (make style is required before opening a PR)."""
    import shutil
    if not shutil.which("ruff"):
        pytest.skip("ruff not installed")
    r = subprocess.run(
        ["ruff", "check", "src/transformers/__init__.py", "utils/check_repo.py"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"ruff style violations in modified files:\n{r.stdout}\n{r.stderr}"
