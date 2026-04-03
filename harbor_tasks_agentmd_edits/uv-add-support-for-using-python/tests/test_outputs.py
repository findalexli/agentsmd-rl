"""
Task: uv-add-support-for-using-python
Repo: astral-sh/uv @ 4419f9cd39bd5951e2212342aa208fa479206f52
PR:   18454

Add Python 3.6 interpreter support: patch vendored packaging modules to
remove from __future__ import annotations and quote PEP 604/585 type hints,
lower version floor in get_interpreter_info.py, create a reapplicable patch
file, and update the packaging README to document applied patches.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import py_compile
import tempfile
from pathlib import Path

REPO = "/workspace/uv"
PACKAGING = Path(REPO) / "crates" / "uv-python" / "python" / "packaging"
INTERPRETER_INFO = Path(REPO) / "crates" / "uv-python" / "python" / "get_interpreter_info.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files parse without errors."""
    files = [
        INTERPRETER_INFO,
        PACKAGING / "_elffile.py",
        PACKAGING / "_manylinux.py",
        PACKAGING / "_musllinux.py",
    ]
    for f in files:
        assert f.exists(), f"File not found: {f}"
        # py_compile raises on syntax errors
        with tempfile.NamedTemporaryFile(suffix=".pyc") as tmp:
            py_compile.compile(str(f), cfile=tmp.name, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def _find_version_floor(tree: ast.AST) -> tuple:
    """Walk AST to find the sys.version_info < (major, minor) comparison
    that gates the 'unsupported Python' error path in get_interpreter_info.py."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        # Looking for: sys.version_info < (3, N)
        left = node.left
        if not (isinstance(left, ast.Attribute) and
                isinstance(left.value, ast.Name) and
                left.value.id == "sys" and
                left.attr == "version_info"):
            continue
        for op, comp in zip(node.ops, node.comparators):
            if isinstance(op, ast.Lt) and isinstance(comp, ast.Tuple):
                elts = comp.elts
                if (len(elts) == 2 and
                        isinstance(elts[0], ast.Constant) and elts[0].value == 3 and
                        isinstance(elts[1], ast.Constant)):
                    return (3, elts[1].value)
    return None


# [pr_diff] fail_to_pass
def test_version_floor_lowered():
    """get_interpreter_info.py must reject Python < 3.6, not < 3.7."""
    source = INTERPRETER_INFO.read_text()
    tree = ast.parse(source)
    floor = _find_version_floor(tree)
    assert floor is not None, "Could not find sys.version_info < (3, N) comparison"
    assert floor == (3, 6), (
        f"Version floor should be (3, 6) but found {floor}. "
        "Python 3.6 interpreters must be supported."
    )


def _has_future_annotations(filepath: Path) -> bool:
    """Check if a Python file has 'from __future__ import annotations'."""
    tree = ast.parse(filepath.read_text())
    for node in ast.walk(tree):
        if (isinstance(node, ast.ImportFrom) and
                node.module == "__future__" and
                any(alias.name == "annotations" for alias in node.names)):
            return True
    return False


# [pr_diff] fail_to_pass
def test_elffile_no_future_annotations():
    """_elffile.py must not use 'from __future__ import annotations' (Python 3.6 compat)."""
    elffile = PACKAGING / "_elffile.py"
    assert elffile.exists(), "_elffile.py not found"
    assert not _has_future_annotations(elffile), (
        "_elffile.py still has 'from __future__ import annotations'. "
        "This must be removed for Python 3.6 compatibility."
    )


# [pr_diff] fail_to_pass
def test_manylinux_no_future_annotations():
    """_manylinux.py must not use 'from __future__ import annotations' (Python 3.6 compat)."""
    manylinux = PACKAGING / "_manylinux.py"
    assert manylinux.exists(), "_manylinux.py not found"
    assert not _has_future_annotations(manylinux), (
        "_manylinux.py still has 'from __future__ import annotations'. "
        "This must be removed for Python 3.6 compatibility."
    )


# [pr_diff] fail_to_pass
def test_musllinux_no_future_annotations():
    """_musllinux.py must not use 'from __future__ import annotations' (Python 3.6 compat)."""
    musllinux = PACKAGING / "_musllinux.py"
    assert musllinux.exists(), "_musllinux.py not found"
    assert not _has_future_annotations(musllinux), (
        "_musllinux.py still has 'from __future__ import annotations'. "
        "This must be removed for Python 3.6 compatibility."
    )


def _find_py36_incompatible_annotations(filepath: Path) -> list:
    """Find annotations using PEP 604 pipe syntax or PEP 585 lowercase generics.

    These are incompatible with Python 3.6:
    - PEP 604: str | None (needs 3.10+)
    - PEP 585: dict[K, V], tuple[int, ...] (needs 3.9+)
    """
    tree = ast.parse(filepath.read_text())
    PEP585_BUILTINS = {"dict", "list", "tuple", "set", "frozenset", "type"}
    issues = []

    for node in ast.walk(tree):
        # Collect all annotation nodes
        ann_nodes = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns:
                ann_nodes.append((f"{node.name} return", node.returns))
            for arg in node.args.args:
                if arg.annotation:
                    ann_nodes.append((f"{node.name} arg '{arg.arg}'", arg.annotation))
        if isinstance(node, ast.AnnAssign) and node.annotation:
            ann_nodes.append(("variable annotation", node.annotation))

        for desc, ann in ann_nodes:
            for subnode in ast.walk(ann):
                if isinstance(subnode, ast.BinOp) and isinstance(subnode.op, ast.BitOr):
                    issues.append(f"{desc}: uses '|' union syntax (PEP 604, needs 3.10+)")
                if (isinstance(subnode, ast.Subscript) and
                        isinstance(subnode.value, ast.Name) and
                        subnode.value.id in PEP585_BUILTINS):
                    issues.append(
                        f"{desc}: uses lowercase '{subnode.value.id}[...]' (PEP 585, needs 3.9+)"
                    )
    return issues


# [pr_diff] fail_to_pass
def test_elffile_annotations_quoted():
    """_elffile.py type annotations must be Python 3.6 compatible.

    Without 'from __future__ import annotations', bare 'str | None' or
    'tuple[int, ...]' would fail on Python < 3.10 / 3.9. They must be
    either string-quoted or replaced with typing equivalents.
    """
    elffile = PACKAGING / "_elffile.py"
    issues = _find_py36_incompatible_annotations(elffile)
    assert not issues, (
        f"_elffile.py has Python 3.6-incompatible annotations:\n"
        + "\n".join(f"  - {i}" for i in issues)
    )


# [pr_diff] fail_to_pass
def test_manylinux_annotations_py36_compat():
    """_manylinux.py type annotations must be Python 3.6 compatible."""
    manylinux = PACKAGING / "_manylinux.py"
    issues = _find_py36_incompatible_annotations(manylinux)
    assert not issues, (
        f"_manylinux.py has Python 3.6-incompatible annotations:\n"
        + "\n".join(f"  - {i}" for i in issues)
    )


# [pr_diff] fail_to_pass
def test_musllinux_annotations_py36_compat():
    """_musllinux.py type annotations must be Python 3.6 compatible."""
    musllinux = PACKAGING / "_musllinux.py"
    issues = _find_py36_incompatible_annotations(musllinux)
    assert not issues, (
        f"_musllinux.py has Python 3.6-incompatible annotations:\n"
        + "\n".join(f"  - {i}" for i in issues)
    )


# [pr_diff] fail_to_pass
def test_patch_file_exists():
    """A patch file documenting the Python 3.6 compat changes must exist."""
    patch_files = list(PACKAGING.glob("*.patch"))
    assert len(patch_files) >= 1, (
        "No .patch file found in the packaging directory. "
        "A patch file should document the Python 3.6 compatibility changes "
        "so they can be reapplied when re-vendoring."
    )
    # The patch should reference the key changes
    patch_content = patch_files[0].read_text()
    assert "annotations" in patch_content.lower() or "3.6" in patch_content, (
        "Patch file should describe the Python 3.6 / annotations changes"
    )
    # It should contain diff-like content
    assert "---" in patch_content or "diff" in patch_content.lower(), (
        "Patch file should contain diff/patch format content"
    )


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    When vendored code is patched, the README should be updated to list
    the patches so future maintainers know what was changed and can
    reapply patches when updating the vendored code.
    """
    readme = PACKAGING / "README.md"
    assert readme.exists(), "packaging/README.md not found"
    content = readme.read_text()

    # Must mention patches somewhere
    assert "patch" in content.lower(), (
        "README.md should mention the applied patches"
    )
    # Must reference the actual patch file
    patch_files = list(PACKAGING.glob("*.patch"))
    if patch_files:
        patch_name = patch_files[0].name
        assert patch_name in content, (
            f"README.md should reference the patch file '{patch_name}'"
        )
    # Should have a section structure (heading or list) for patches
    assert "##" in content or "- " in content, (
        "README.md should have structured documentation of patches"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_packaging_modules_importable():
    """Vendored packaging modules must still be importable after changes."""
    import importlib
    import sys

    # Add packaging parent to path
    packaging_parent = str(Path(REPO) / "crates" / "uv-python" / "python")
    if packaging_parent not in sys.path:
        sys.path.insert(0, packaging_parent)

    # These should import without error
    for mod_name in ("packaging._elffile", "packaging._manylinux", "packaging._musllinux"):
        # Remove from cache to force fresh import
        if mod_name in sys.modules:
            del sys.modules[mod_name]
        mod = importlib.import_module(mod_name)
        assert mod is not None, f"Failed to import {mod_name}"
