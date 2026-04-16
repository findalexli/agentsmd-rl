"""Test outputs for langchain symlink security fix."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = "/workspace/langchain"
CORE_LIB = f"{REPO}/libs/core"


def test_import_loading_module():
    """Can import the loading module and access _load_template."""
    sys.path.insert(0, CORE_LIB)
    from langchain_core.prompts.loading import _load_template
    assert callable(_load_template)


def test_symlink_txt_to_py_is_blocked():
    """A .txt symlink pointing to a .py file should be blocked."""
    sys.path.insert(0, CORE_LIB)
    from langchain_core.prompts.loading import _load_template

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a .py file with sensitive content
        py_file = Path(tmpdir) / "secret.py"
        py_file.write_text("INTERNAL_SECRET='ABC-123-XYZ'")

        # Create a symlink with .txt extension pointing to the .py file
        txt_link = Path(tmpdir) / "exploit_link.txt"
        txt_link.symlink_to(py_file)

        # Try to load via the symlink - should raise ValueError
        config = {"template_path": txt_link}
        with pytest.raises(ValueError):
            _load_template("template", config, allow_dangerous_paths=True)


def test_symlink_jinja2_rce_is_blocked():
    """A .txt symlink pointing to a jinja2 template should be blocked."""
    sys.path.insert(0, CORE_LIB)
    from langchain_core.prompts.loading import _load_template

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a file with jinja2 RCE payload
        payload_file = Path(tmpdir) / "payload.j2"
        payload_file.write_text("{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}")

        # Create a symlink with .txt extension pointing to the payload
        txt_link = Path(tmpdir) / "rce_bypass.txt"
        txt_link.symlink_to(payload_file)

        # Try to load via the symlink - should raise ValueError
        config = {"template_path": txt_link}
        with pytest.raises(ValueError):
            _load_template("template", config, allow_dangerous_paths=True)


def test_real_txt_file_still_works():
    """A real .txt file should still be loadable."""
    sys.path.insert(0, CORE_LIB)
    from langchain_core.prompts.loading import _load_template

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a real .txt file
        txt_file = Path(tmpdir) / "real_template.txt"
        txt_file.write_text("Hello, {name}!")

        # Load via the file - should work
        config = {"template_path": txt_file}
        result = _load_template("template", config, allow_dangerous_paths=True)

        assert result["template"] == "Hello, {name}!"
        assert "template_path" not in result


def test_symlink_txt_to_txt_works():
    """A .txt symlink pointing to a real .txt file should work."""
    sys.path.insert(0, CORE_LIB)
    from langchain_core.prompts.loading import _load_template

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a real .txt file
        txt_file = Path(tmpdir) / "real_template.txt"
        txt_file.write_text("Hello, {name}!")

        # Create a symlink with .txt extension pointing to the real .txt
        txt_link = Path(tmpdir) / "link.txt"
        txt_link.symlink_to(txt_file)

        # Load via the symlink - should work since it resolves to .txt
        config = {"template_path": txt_link}
        result = _load_template("template", config, allow_dangerous_paths=True)

        assert result["template"] == "Hello, {name}!"


def test_unit_tests_still_pass():
    """Existing unit tests in the repo should still pass (pass_to_pass)."""
    # Run the specific test file related to prompt loading
    cmd = [
        "python", "-m", "pytest",
        "libs/core/tests/unit_tests/prompts/test_loading.py",
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ]
    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout}\n{result.stderr}"


def test_repo_imports():
    """Repo's prompt imports are valid (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/prompts/test_imports.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/libs/core",
    )
    assert r.returncode == 0, f"Import tests failed:\n{r.stderr[-500:]}"


def test_repo_prompt_unit_tests():
    """Repo's prompt unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/prompts/test_prompt.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=f"{REPO}/libs/core",
    )
    assert r.returncode == 0, f"Prompt tests failed:\n{r.stderr[-500:]}"


def test_repo_loading_unit_tests():
    """Repo's loading unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/prompts/test_loading.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=f"{REPO}/libs/core",
    )
    assert r.returncode == 0, f"Loading tests failed:\n{r.stderr[-500:]}"
