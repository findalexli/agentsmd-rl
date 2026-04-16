"""Tests for langchain symlink save path security fix.

This tests that the save() method in prompt classes resolves symlinks
before validating file extensions, preventing a security bypass.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path("/workspace/langchain/libs/core")


def test_symlink_bypass_blocked():
    """Fail-to-pass: Symlink pointing to .py file should be rejected.

    The fix resolves symlinks before checking file extensions.
    Before the fix: save_path.suffix checks the symlink name (".json")
    After the fix: resolved_path.suffix checks the actual file (".py")

    Without the fix, prompt.save(symlink_json_to_py) writes to the .py file.
    With the fix, it raises ValueError because the resolved path ends in .py.
    """
    # Import after setting path
    sys.path.insert(0, str(REPO))
    from langchain_core.prompts.prompt import PromptTemplate
    import warnings

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        target = tmp_path / "malicious.py"
        symlink = tmp_path / "output.json"
        symlink.symlink_to(target)

        prompt = PromptTemplate(input_variables=["name"], template="Hello {name}")

        # Try to save via symlink - this should raise ValueError
        raised_error = False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                prompt.save(symlink)
            except ValueError as e:
                raised_error = True
                assert "must be json or yaml" in str(e), f"Wrong error message: {e}"

        # After the fix: ValueError should be raised AND target should not exist
        # Before the fix: No error is raised AND target will exist (bug!)
        if target.exists():
            # The bug is present - data was written to the .py file!
            content = target.read_text()
            raise AssertionError(
                f"SECURITY BUG: Data was written to {target}! "
                f"Content: {content[:200]}..."
            )

        # The fix is applied if ValueError was raised
        assert raised_error, (
            "Expected ValueError was not raised when saving to symlink pointing to .py file. "
            "The save() method should resolve symlinks before checking file extensions."
        )


def test_symlink_yaml_to_py_blocked():
    """Fail-to-pass: Symlink .yaml -> .py should also be blocked.

    Variant of the symlink bypass with .yaml extension instead of .json.
    """
    sys.path.insert(0, str(REPO))
    from langchain_core.prompts.prompt import PromptTemplate
    import warnings

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        target = tmp_path / "evil.py"
        symlink = tmp_path / "output.yaml"
        symlink.symlink_to(target)

        prompt = PromptTemplate(input_variables=["x"], template="Value: {x}")

        raised_error = False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                prompt.save(symlink)
            except ValueError as e:
                raised_error = True
                assert "must be json or yaml" in str(e)

        if target.exists():
            raise AssertionError(f"SECURITY BUG: Data written to {target}")

        assert raised_error, "ValueError should be raised for .yaml symlink to .py file"


def test_symlink_yml_to_py_blocked():
    """Fail-to-pass: Symlink .yml -> .py should also be blocked."""
    sys.path.insert(0, str(REPO))
    from langchain_core.prompts.prompt import PromptTemplate
    import warnings

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        target = tmp_path / "bad.py"
        symlink = tmp_path / "output.yml"
        symlink.symlink_to(target)

        prompt = PromptTemplate(input_variables=["x"], template="Test: {x}")

        raised_error = False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                prompt.save(symlink)
            except ValueError as e:
                raised_error = True
                assert "must be json or yaml" in str(e)

        if target.exists():
            raise AssertionError(f"SECURITY BUG: Data written to {target}")

        assert raised_error, "ValueError should be raised for .yml symlink to .py file"


def test_legitimate_symlink_to_json_works():
    """Pass-to-pass: Symlinks to valid .json files should work.

    After the fix, legitimate symlinks (output.json -> actual.json) should work.
    """
    sys.path.insert(0, str(REPO))
    from langchain_core.prompts.prompt import PromptTemplate
    import warnings
    import json

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        target = tmp_path / "actual.json"
        symlink = tmp_path / "link.json"
        symlink.symlink_to(target)

        prompt = PromptTemplate(input_variables=["name"], template="Hi {name}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            prompt.save(symlink)

        # Target should exist with valid JSON content
        assert target.exists(), "Target file should be created"
        content = json.loads(target.read_text())
        assert content["template"] == "Hi {name}"


def test_direct_json_save_works():
    """Pass-to-pass: Direct .json save without symlinks should work."""
    sys.path.insert(0, str(REPO))
    from langchain_core.prompts.prompt import PromptTemplate
    import warnings
    import json

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        target = tmp_path / "output.json"

        prompt = PromptTemplate(input_variables=["x"], template="Value: {x}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            prompt.save(target)

        assert target.exists(), "Direct JSON save should work"
        content = json.loads(target.read_text())
        assert content["template"] == "Value: {x}"


def test_repo_prompts_loading_tests():
    """Pass-to-pass: Run prompt loading tests including save/load round-trip.

    Tests in test_loading.py cover the save() functionality, including:
    - test_saving_loading_round_trip: Tests saving and loading prompts work correctly
    - test_symlink_txt_to_py_is_blocked: Tests symlink security protections
    """
    # Install test dependencies first
    deps_result = subprocess.run(
        ["pip", "install", "-q", "blockbuster", "syrupy", "pytest-asyncio",
         "pytest-mock", "freezegun", "responses", "pytest-socket", "pytest-xdist",
         "numpy", "langchain-text-splitters", "pytest-benchmark", "grandalf"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/prompts/test_loading.py",
         "-v", "--tb=short", "-x"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print("STDOUT:", result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
        print("STDERR:", result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
        assert False, f"Loading tests failed: {result.stderr[-300:]}"


def test_repo_prompts_main_tests():
    """Pass-to-pass: Run main prompt tests.

    Tests in test_prompt.py cover core PromptTemplate functionality,
    ensuring the fix doesn't break existing behavior.
    """
    # Install test dependencies first
    subprocess.run(
        ["pip", "install", "-q", "blockbuster", "syrupy", "pytest-asyncio",
         "pytest-mock", "freezegun", "responses", "pytest-socket", "pytest-xdist",
         "numpy", "langchain-text-splitters", "pytest-benchmark", "grandalf"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/prompts/test_prompt.py",
         "-v", "--tb=short", "-x"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print("STDOUT:", result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
        print("STDERR:", result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
        assert False, f"Prompt tests failed: {result.stderr[-300:]}"


def test_repo_ruff_check():
    """Pass-to-pass: Ruff linter check on prompts module (repo CI gate).

    The repo's CI runs ruff check on all code. This test verifies
    the modified file passes linting.
    """
    # Install ruff
    subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    result = subprocess.run(
        ["ruff", "check", "langchain_core/prompts/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_mypy_check():
    """Pass-to-pass: Mypy type check on base.py (repo CI gate).

    The repo's CI runs mypy type checking. This test verifies
    the modified file passes type checking.
    """
    # Install mypy and types
    subprocess.run(
        ["pip", "install", "-q", "mypy", "types-pyyaml"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    result = subprocess.run(
        ["mypy", "langchain_core/prompts/base.py", "--ignore-missing-imports"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"Mypy check failed:\n{result.stdout}\n{result.stderr}"
